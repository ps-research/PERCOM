"""Optuna search for the tuned baselines.

Search spaces, sampler and objective follow briefs/P1-E01.md:
TPE sampler with seed 0, 30 trials, objective = mean positioning error averaged
over 3 folds of GroupKFold on the training data, with the reference point as the
group. The test file is never touched here.
"""
from __future__ import annotations

import time

import numpy as np

from .metrics import positioning_error
from .models import make_model

N_TRIALS = 30
N_FOLDS = 3
SAMPLER_SEED = 0
TUNING_MODEL_SEED = 0  # random_state of rf, lgbm and mlp inside the search

# Categorical choices are passed to Optuna as strings and decoded here.
_RF_MAX_FEATURES = {"sqrt": "sqrt", "0.3": 0.3, "0.5": 0.5, "1.0": 1.0}
_RF_MAX_DEPTH = {"none": None, "10": 10, "20": 20, "30": 30}
_MLP_LAYERS = {"256": (256,), "256-128": (256, 128), "512-256": (512, 256), "256-128-64": (256, 128, 64)}


def suggest(name: str, trial) -> dict:
    """Draw one set of values from the search space of ``name``."""
    if name == "knn":
        return dict(
            n_neighbors=trial.suggest_int("n_neighbors", 1, 30),
            weights=trial.suggest_categorical("weights", ["uniform", "distance"]),
            metric=trial.suggest_categorical("metric", ["euclidean", "manhattan"]),
        )
    if name == "rf":
        return dict(
            n_estimators=trial.suggest_categorical("n_estimators", [200, 500]),
            max_features=_RF_MAX_FEATURES[trial.suggest_categorical("max_features", list(_RF_MAX_FEATURES))],
            min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 10),
            max_depth=_RF_MAX_DEPTH[trial.suggest_categorical("max_depth", list(_RF_MAX_DEPTH))],
        )
    if name in ("lgbm-ph", "lgbm-nan"):
        return dict(
            n_estimators=trial.suggest_int("n_estimators", 200, 1500),
            learning_rate=trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            num_leaves=trial.suggest_int("num_leaves", 8, 128),
            min_child_samples=trial.suggest_int("min_child_samples", 1, 50),
            subsample=trial.suggest_float("subsample", 0.5, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.3, 1.0),
            reg_lambda=trial.suggest_float("reg_lambda", 0.001, 10.0, log=True),
        )
    if name == "svr":
        return dict(
            C=trial.suggest_float("C", 0.1, 1000.0, log=True),
            gamma=trial.suggest_float("gamma", 0.0001, 1.0, log=True),
            epsilon=trial.suggest_float("epsilon", 0.01, 1.0, log=True),
        )
    if name == "mlp":
        return dict(
            hidden_layer_sizes=_MLP_LAYERS[trial.suggest_categorical("hidden_layer_sizes", list(_MLP_LAYERS))],
            alpha=trial.suggest_float("alpha", 1e-6, 1e-2, log=True),
            learning_rate_init=trial.suggest_float("learning_rate_init", 1e-4, 1e-2, log=True),
        )
    raise ValueError(f"{name} has no search space")


def folds(n_rows: int, groups: np.ndarray):
    from sklearn.model_selection import GroupKFold

    return list(GroupKFold(n_splits=N_FOLDS).split(np.zeros(n_rows), groups=groups))


def _fold_error(name, params, X, y, groups, train_idx, val_idx, n_jobs) -> float:
    model = make_model(name, params, seed=TUNING_MODEL_SEED, n_jobs=n_jobs)
    model.fit(X[train_idx], y[train_idx], groups[train_idx])
    return float(positioning_error(y[val_idx], model.predict(X[val_idx])).mean())


def cv_error(name: str, params: dict, X: np.ndarray, y: np.ndarray, groups: np.ndarray, n_jobs: int = 1,
             parallel=None) -> tuple[float, list[float]]:
    """Mean positioning error of each fold, and their average."""
    from joblib import delayed

    splits = folds(len(X), groups)
    inner = max(1, n_jobs // N_FOLDS)
    if parallel is None:
        per_fold = [_fold_error(name, params, X, y, groups, tr, va, n_jobs) for tr, va in splits]
    else:
        per_fold = parallel(delayed(_fold_error)(name, params, X, y, groups, tr, va, inner) for tr, va in splits)
    return float(np.mean(per_fold)), [float(v) for v in per_fold]


def run_search(name: str, X: np.ndarray, y: np.ndarray, groups: np.ndarray, n_trials: int = N_TRIALS,
               n_jobs: int = 1, log=None) -> dict:
    """Run the search of one baseline on one survey. Trials run one after the other."""
    import optuna
    from joblib import Parallel

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    decoded: dict[int, dict] = {}
    t0 = time.perf_counter()
    with Parallel(n_jobs=min(N_FOLDS, max(1, n_jobs))) as parallel:

        def objective(trial):
            params = suggest(name, trial)
            decoded[trial.number] = params
            mean, per_fold = cv_error(name, params, X, y, groups, n_jobs=n_jobs, parallel=parallel)
            for i, v in enumerate(per_fold):
                trial.set_user_attr(f"fold{i}_mean_error", v)
            if log:
                log(f"trial {trial.number:2d} value={mean:.4f} params={params}")
            return mean

        study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=SAMPLER_SEED))
        study.optimize(objective, n_trials=n_trials)
    # joblib keeps its worker processes alive for five idle minutes; a process that
    # ran a search would wait that long before it can exit. Stop them now.
    from joblib.externals.loky import get_reusable_executor

    get_reusable_executor().shutdown(wait=True, kill_workers=True)
    return dict(
        model=name,
        best_params=decoded[study.best_trial.number],
        best_value=float(study.best_value),
        best_trial=int(study.best_trial.number),
        n_trials=int(len(study.trials)),
        search_seconds=time.perf_counter() - t0,
        trials=study.trials_dataframe(),
        settings=dict(sampler="TPESampler", sampler_seed=SAMPLER_SEED, n_trials=n_trials, n_folds=N_FOLDS,
                      cv="GroupKFold by reference point", objective="mean positioning error averaged over folds",
                      model_seed_in_search=TUNING_MODEL_SEED),
    )


def params_to_json(params: dict) -> dict:
    """Make best values JSON-friendly (tuples become lists)."""
    return {k: (list(v) if isinstance(v, tuple) else v) for k, v in params.items()}


def params_from_json(params: dict) -> dict:
    out = dict(params)
    if isinstance(out.get("hidden_layer_sizes"), list):
        out["hidden_layer_sizes"] = tuple(out["hidden_layer_sizes"])
    return out
