"""Model wrappers with one interface.

Every wrapper takes the raw signal-strength matrix (100 = not detected), applies
its own way of writing "not detected", and predicts both coordinates:

    model = make_model(name, params, seed)
    model.fit(X_raw, y, rp_ids)        # y is (n, 2): ECoord, NCoord
    pred = model.predict(X_raw_test)   # (m, 2)

Model definitions follow briefs/P1-E01.md, "Models".
"""
from __future__ import annotations

import time

import numpy as np

from .data import average_per_point, cap_rows, encode

TFMS = ("tabpfn-nan", "tabpfn-ph", "tabicl")
TUNED = ("knn", "rf", "lgbm-ph", "lgbm-nan", "svr", "mlp")
BASELINES = TUNED + ("gp",)
ALL_MODELS = TFMS + BASELINES
# Models with randomness: one run per seed. The others (knn, svr, gp) run once.
SEEDED = ("tabpfn-nan", "tabpfn-ph", "tabicl", "rf", "lgbm-ph", "lgbm-nan", "mlp")

ENCODING = {
    "tabpfn-nan": "missing", "tabpfn-ph": "placeholder", "tabicl": "missing",
    "knn": "placeholder", "rf": "placeholder", "lgbm-ph": "placeholder", "lgbm-nan": "missing",
    "svr": "placeholder", "mlp": "placeholder", "gp": "placeholder",
}

# Thread counts are fixed so that a run gives the same numbers on any machine with
# at least this many cores. They are settings of the run, not of the model.
LGBM_THREADS = 4
BLAS_THREADS = 4
SVR_CACHE_MB = 1000
GP_RANDOM_STATE = 0  # only seeds the restarts of the marginal-likelihood optimiser


def _blas_limit():
    from threadpoolctl import threadpool_limits

    return threadpool_limits(limits=BLAS_THREADS)


class _Model:
    name = ""

    def __init__(self, params: dict | None = None, seed: int = 0, n_jobs: int = 1, device: str = "cuda"):
        self.params = dict(params or {})
        self.seed = int(seed)
        self.n_jobs = int(n_jobs)
        self.device = device
        self.info: dict = {}

    @property
    def encoding(self) -> str:
        return self.info.get("encoding", ENCODING[self.name])

    def _enc(self, X_raw: np.ndarray) -> np.ndarray:
        return encode(X_raw, self.encoding)


class KNN(_Model):
    name = "knn"

    def fit(self, X, y, rp=None):
        from sklearn.neighbors import KNeighborsRegressor

        self.m = KNeighborsRegressor(**self.params, n_jobs=self.n_jobs).fit(self._enc(X), y)
        return self

    def predict(self, X):
        return self.m.predict(self._enc(X))


class RF(_Model):
    name = "rf"

    def fit(self, X, y, rp=None):
        from sklearn.ensemble import RandomForestRegressor

        self.m = RandomForestRegressor(**self.params, random_state=self.seed, n_jobs=self.n_jobs).fit(self._enc(X), y)
        return self

    def predict(self, X):
        return self.m.predict(self._enc(X))


class LGBM(_Model):
    """LightGBM, one model per coordinate, both sharing one set of values."""

    def fit(self, X, y, rp=None):
        import lightgbm as lgb

        Xe = self._enc(X)
        self.m = [
            lgb.LGBMRegressor(**self.params, subsample_freq=1, random_state=self.seed,
                              n_jobs=LGBM_THREADS, verbose=-1).fit(Xe, y[:, j])
            for j in range(2)
        ]
        return self

    def predict(self, X):
        Xe = self._enc(X)
        return np.column_stack([m.predict(Xe) for m in self.m])


class LGBMPlaceholder(LGBM):
    name = "lgbm-ph"


class LGBMMissing(LGBM):
    name = "lgbm-nan"


class SVRModel(_Model):
    """SVR with RBF kernel, one model per coordinate, inputs standardised."""

    name = "svr"

    def fit(self, X, y, rp=None):
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVR

        self.sx = StandardScaler().fit(self._enc(X))
        Xs = self.sx.transform(self._enc(X))
        self.m = [SVR(kernel="rbf", cache_size=SVR_CACHE_MB, **self.params).fit(Xs, y[:, j]) for j in range(2)]
        return self

    def predict(self, X):
        Xs = self.sx.transform(self._enc(X))
        return np.column_stack([m.predict(Xs) for m in self.m])


class MLP(_Model):
    """MLPRegressor with two outputs, inputs and targets standardised."""

    name = "mlp"

    def fit(self, X, y, rp=None):
        from sklearn.neural_network import MLPRegressor
        from sklearn.preprocessing import StandardScaler

        self.sx = StandardScaler().fit(self._enc(X))
        self.sy = StandardScaler().fit(y)
        with _blas_limit():
            self.m = MLPRegressor(**self.params, early_stopping=True, max_iter=1000, random_state=self.seed).fit(
                self.sx.transform(self._enc(X)), self.sy.transform(y)
            )
        self.info["n_iter"] = int(self.m.n_iter_)
        return self

    def predict(self, X):
        with _blas_limit():
            return self.sy.inverse_transform(self.m.predict(self.sx.transform(self._enc(X))))


class GP(_Model):
    """Gaussian process regression, one model per coordinate.

    Fitted on one fingerprint per reference point (the mean of its scans after the
    placeholder is applied), inputs standardised, normalize_y=True, kernel
    ConstantKernel * RBF + WhiteKernel with one length scale, tuned by its own
    marginal likelihood with three restarts.
    """

    name = "gp"

    def fit(self, X, y, rp=None):
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
        from sklearn.preprocessing import StandardScaler

        if rp is None:
            raise ValueError("gp needs the reference-point id of every row")
        Xm, ym = average_per_point(self._enc(X), y, rp)
        self.sx = StandardScaler().fit(Xm)
        Xs = self.sx.transform(Xm)
        self.m = []
        with _blas_limit():
            for j in range(2):
                kernel = ConstantKernel() * RBF() + WhiteKernel()
                self.m.append(
                    GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=3, normalize_y=True,
                                             random_state=GP_RANDOM_STATE).fit(Xs, ym[:, j])
                )
        self.info["fitted_rows"] = int(len(Xm))
        self.info["kernels"] = [str(m.kernel_) for m in self.m]
        return self

    def predict(self, X):
        Xs = self.sx.transform(self._enc(X))
        with _blas_limit():
            return np.column_stack([m.predict(Xs) for m in self.m])


class _Context(_Model):
    """Shared logic of the tabular foundation models: the context and its optional cap."""

    cap_always = True  # TabPFN: capped whenever the survey has more than 10,000 rows

    def __init__(self, *args, cap_context: bool | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cap_context = self.cap_always if cap_context is None else cap_context

    def _context(self, X, y, rp):
        rows = cap_rows(rp, self.seed) if (self.cap_context and rp is not None) else None
        self.info["context_capped"] = rows is not None
        if rows is not None:
            X, y = X[rows], y[rows]
        self.info["context_rows"] = int(len(X))
        return X, y


class TabPFN(_Context):
    """TabPFN v2, default settings, one regressor per coordinate. The seed is the run seed."""

    def fit(self, X, y, rp=None):
        from tabpfn import TabPFNRegressor
        from tabpfn.constants import ModelVersion

        X, y = self._context(X, y, rp)
        Xe = self._enc(X)
        self.m = [
            TabPFNRegressor.create_default_for_version(ModelVersion.V2, device=self.device,
                                                       random_state=self.seed).fit(Xe, y[:, j])
            for j in range(2)
        ]
        self.info["model_path"] = str(self.m[0].model_path)
        return self

    def predict(self, X):
        Xe = self._enc(X)
        return np.column_stack([np.asarray(m.predict(Xe)) for m in self.m])


class TabPFNMissing(TabPFN):
    name = "tabpfn-nan"


class TabPFNPlaceholder(TabPFN):
    name = "tabpfn-ph"


class TabICL(_Context):
    """TabICLv2, default checkpoint, one regressor per coordinate.

    "Not detected" is passed as NaN. If the library rejects NaN the placeholder is
    used instead. The context is every row unless ``cap_context=True`` (the
    out-of-memory fallback of the brief).
    """

    name = "tabicl"
    cap_always = False

    def _fit(self, X, y):
        from tabicl import TabICLRegressor

        Xe = self._enc(X)
        return [TabICLRegressor(device=self.device, random_state=self.seed).fit(Xe, y[:, j]) for j in range(2)]

    def fit(self, X, y, rp=None):
        X, y = self._context(X, y, rp)
        try:
            self.m = self._fit(X, y)
        except ValueError as exc:
            if "nan" not in str(exc).lower():
                raise
            self.info["encoding"] = "placeholder"
            self.info["nan_rejected"] = str(exc)[:300]
            self.m = self._fit(X, y)
        self.info["checkpoint"] = str(self.m[0].checkpoint_version)
        return self

    def predict(self, X):
        Xe = self._enc(X)
        return np.column_stack([np.asarray(m.predict(Xe)) for m in self.m])


_REGISTRY = {
    "knn": KNN, "rf": RF, "lgbm-ph": LGBMPlaceholder, "lgbm-nan": LGBMMissing, "svr": SVRModel, "mlp": MLP,
    "gp": GP, "tabpfn-nan": TabPFNMissing, "tabpfn-ph": TabPFNPlaceholder, "tabicl": TabICL,
}


def make_model(name: str, params: dict | None = None, seed: int = 0, n_jobs: int = 1, device: str = "cuda",
               **kwargs) -> _Model:
    return _REGISTRY[name](params, seed=seed, n_jobs=n_jobs, device=device, **kwargs)


def is_gpu_model(name: str) -> bool:
    return name in TFMS


def is_out_of_memory(exc: BaseException) -> bool:
    return type(exc).__name__ == "OutOfMemoryError" or "out of memory" in str(exc).lower()


def timed_fit_predict(model: _Model, X_train, y_train, rp_train, X_test) -> tuple[np.ndarray, dict]:
    """Fit, predict, and return the cost: fit seconds, predict seconds, peak GPU memory."""
    gpu = is_gpu_model(model.name)
    if gpu:
        import torch

        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    model.fit(X_train, y_train, rp_train)
    if gpu:
        torch.cuda.synchronize()
    t1 = time.perf_counter()
    pred = np.asarray(model.predict(X_test), dtype=float)
    if gpu:
        torch.cuda.synchronize()
    t2 = time.perf_counter()
    cost = dict(fit_s=t1 - t0, predict_s=t2 - t1, peak_gpu_mem_mb=None, peak_gpu_reserved_mb=None)
    if gpu:
        cost["peak_gpu_mem_mb"] = torch.cuda.max_memory_allocated() / 2 ** 20
        cost["peak_gpu_reserved_mb"] = torch.cuda.max_memory_reserved() / 2 ** 20
    return pred, cost
