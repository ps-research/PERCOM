"""P1-E03: extra measurements approved by the PI on 2026-11-15 (options A to E).

    python -m p1.e3x gpu  --out OUT --e1-out E1_OUT --configs HCXY-All HCXY-AP   (A, B, C)
    python -m p1.e3x own  --out OUT --e1-out E1_OUT --configs HCXY-All           (D: more Part B draws)
    python -m p1.e3x report --out results/P1-E03 --e1-out results/P1-E01 --e2-out results/P1-E02

A. Uncertainty: predictive quantiles of the tabular foundation models and the GP's
   predictive standard deviation, on the full survey; coverage and width of central
   intervals, and whether the predicted spread ranks the errors.
B. Scans per reference point: context built from k scans of every reference point.
C. Seeds 5 to 19 of the tabular foundation models on the full survey (P1-E01 had 0 to 4).
D. Part B of P1-E02 with draws 10 to 29 (P1-E02 had 0 to 9).
E. Error by phone and by user of the test rows (analysis of saved predictions, in the report).

Everything not stated is as in P1-E01 and P1-E02 and uses their code.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from . import data as D
from .common import get_logger, git_commit, node_tag, now_utc, read_json, register_session, usable_cpus, write_json
from .e1 import final_unit
from .e2 import SHARES_B, switched_off
from .metrics import error_stats, positioning_error
from .models import ALL_MODELS, BASELINES, TFMS, TUNED, make_model, timed_fit_predict
from .tuning import params_from_json, params_to_json

QUANTILES = [0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.975]
LEVELS = {50: (0.25, 0.75), 80: (0.1, 0.9), 90: (0.05, 0.95), 95: (0.025, 0.975)}
UNC_MODELS = ["tabpfn-nan", "tabpfn-ph", "tabicl", "gp"]
SEEDS_A = [0, 1, 2, 3, 4]
SCANS = [1, 2, 5, 10, 20, 26, 30]
SCAN_CONFIGS = ["HCXY-All", "SYL-All"]
SCAN_MODELS = ["tabpfn-nan", "tabpfn-ph", "tabicl", "knn", "gp"]
SEEDS_C = list(range(5, 20))
DRAWS_D = list(range(10, 30))


# ----------------------------------------------------------------------------- A. uncertainty
def predict_quantiles(m, X_raw: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Point prediction (as in P1-E01: the mean) and quantiles, shape (n, 2) and (n, 2, len(QUANTILES))."""
    Xe = m._enc(X_raw)
    means, qs = [], []
    if m.name.startswith("tabpfn"):
        for r in m.m:
            out = r.predict(Xe, output_type="main", quantiles=QUANTILES)
            means.append(np.asarray(out["mean"]))
            qs.append(np.column_stack([np.asarray(q) for q in out["quantiles"]]))
    elif m.name == "tabicl":
        for r in m.m:
            out = r.predict(Xe, output_type=["mean", "quantiles"], alphas=QUANTILES)
            means.append(np.asarray(out["mean"]))
            qs.append(np.asarray(out["quantiles"]))
    elif m.name == "gp":
        from scipy.stats import norm

        Xs = m.sx.transform(Xe)
        for r in m.m:
            mu, sd = r.predict(Xs, return_std=True)
            means.append(mu)
            qs.append(mu[:, None] + sd[:, None] * norm.ppf(QUANTILES)[None, :])
    else:
        raise ValueError(f"{m.name} has no predictive distribution")
    return np.column_stack(means), np.stack(qs, axis=1)


def uncertainty_stats(y: np.ndarray, pred: np.ndarray, q: np.ndarray) -> dict:
    err = positioning_error(y, pred)
    out = dict(**error_stats(err))
    qi = {v: i for i, v in enumerate(QUANTILES)}
    spread80 = None
    for level, (lo, hi) in LEVELS.items():
        low, high = q[:, :, qi[lo]], q[:, :, qi[hi]]
        inside = (y >= low) & (y <= high)
        out[f"cover{level}_E"] = float(inside[:, 0].mean())
        out[f"cover{level}_N"] = float(inside[:, 1].mean())
        out[f"cover{level}_both"] = float(inside.all(axis=1).mean())
        width = high - low
        out[f"width{level}_m"] = float(width.mean())
        if level == 80:
            spread80 = width.mean(axis=1)
    from scipy.stats import spearmanr

    out["spearman_spread80_error"] = float(spearmanr(spread80, err).statistic)
    order = np.argsort(spread80)
    k = max(1, len(err) // 10)
    out["error_most_confident_10pct_m"] = float(err[order[:k]].mean())
    out["error_least_confident_10pct_m"] = float(err[order[-k:]].mean())
    return out


def run_uncertainty(configs, data_root, out: Path, device: str, log) -> None:
    for config in configs:
        s = D.load_config(config, data_root)
        for model in UNC_MODELS:
            for seed in (SEEDS_A if model in TFMS else [0]):
                rid = f"{config}__{model}__seed{seed}"
                path = out / "logs" / "uncertainty" / f"{rid}.json"
                if path.exists():
                    continue
                m = make_model(model, {}, seed=seed, n_jobs=usable_cpus(), device=device)
                t0 = time.perf_counter()
                m.fit(s.X_train, s.y_train, s.rp_train)
                pred, q = predict_quantiles(m, s.X_test)
                st = uncertainty_stats(s.y_test, pred, q)
                pdir = out / "metrics" / "predictions" / "uncertainty"
                pdir.mkdir(parents=True, exist_ok=True)
                cols = {"row": np.arange(len(pred)), "test_point": s.tp_test, "ECoord": s.y_test[:, 0],
                        "NCoord": s.y_test[:, 1], "pred_ECoord": pred[:, 0], "pred_NCoord": pred[:, 1],
                        "error_m": positioning_error(s.y_test, pred)}
                for j, c in enumerate(("E", "N")):
                    for i, lev in enumerate(QUANTILES):
                        cols[f"q{lev:g}_{c}"] = q[:, j, i]
                pd.DataFrame(cols).to_csv(pdir / f"{rid}.csv.gz", index=False, float_format="%.5f", compression="gzip")
                write_json(path, dict(config=config, model=model, seed=seed, quantiles=QUANTILES, stats=st,
                                      info=m.info, encoding=m.encoding, seconds=time.perf_counter() - t0,
                                      node=node_tag(), code_commit=git_commit(), finished_utc=now_utc()))
                log.info(f"done A {rid} mean={st['mean']:.3f} cover80_both={st['cover80_both']:.3f} "
                         f"spearman={st['spearman_spread80_error']:.3f}")


# ----------------------------------------------------------------------------- B. scans per reference point
def scan_rows(rp_ids: np.ndarray, k: int, seed: int) -> np.ndarray:
    """k scans of every reference point, drawn without replacement with ``seed``."""
    rng = np.random.default_rng(seed)
    rows = []
    for rp in np.unique(rp_ids):
        idx = np.flatnonzero(rp_ids == rp)
        rows.append(rng.choice(idx, size=min(k, len(idx)), replace=False))
    return np.sort(np.concatenate(rows))


def run_scans(configs, data_root, out: Path, e1_out: Path, device: str, log) -> None:
    for config in (c for c in configs if c in SCAN_CONFIGS):
        s = D.load_config(config, data_root)
        knn_params = params_from_json(read_json(e1_out / "config" / "best_params" / f"{config}__knn.json")["best_params"])
        for k in SCANS:
            for seed in SEEDS_A:
                rows = scan_rows(s.rp_train, k, seed)
                for model in SCAN_MODELS:
                    rid = f"{config}__k{k:02d}__seed{seed}__{model}"
                    path = out / "logs" / "scans" / f"{rid}.json"
                    if path.exists():
                        continue
                    if model in ("knn", "gp") and seed > 0:
                        continue  # no randomness in the model; the scan draw of seed 0 is kept
                    params = knn_params if model == "knn" else {}
                    kw = {}
                    if model.startswith("tabpfn"):
                        kw["cap_context"] = False  # the context is the k-scan survey itself
                    m = make_model(model, params, seed=seed, n_jobs=usable_cpus(), device=device, **kw)
                    if model.startswith("tabpfn") and len(rows) > D.TABPFN_MAX_ROWS:
                        m.info["ignore_pretraining_limits"] = True
                        _orig = m.fit

                        def _fit(X, y, rp=None, _m=m):
                            from tabpfn import TabPFNRegressor
                            from tabpfn.constants import ModelVersion

                            Xe = _m._enc(X)
                            _m.m = [TabPFNRegressor.create_default_for_version(
                                ModelVersion.V2, device=_m.device, random_state=_m.seed,
                                ignore_pretraining_limits=True).fit(Xe, y[:, j]) for j in range(2)]
                            _m.info.update(context_rows=int(len(X)), context_capped=False)
                            return _m

                        m.fit = _fit
                    pred, cost = timed_fit_predict(m, s.X_train[rows], s.y_train[rows], s.rp_train[rows], s.X_test)
                    err = positioning_error(s.y_test, pred)
                    write_json(path, dict(config=config, scans_per_point=k, seed=seed, model=model,
                                          context_rows=int(len(rows)), params=params_to_json(params),
                                          stats=error_stats(err), cost=cost, info=m.info, node=node_tag(),
                                          code_commit=git_commit(), finished_utc=now_utc()))
                    log.info(f"done B {rid} rows={len(rows)} mean={err.mean():.3f} fit={cost['fit_s']:.1f}s "
                             f"gpu={cost['peak_gpu_mem_mb'] or 0:.0f}MB")


# ----------------------------------------------------------------------------- C. more seeds
def run_seeds(configs, data_root, out: Path, device: str, log) -> None:
    for config in configs:
        for model in TFMS:
            for seed in SEEDS_C:
                final_unit(config, model, seed, data_root, out, device, log)


# ----------------------------------------------------------------------------- D. more Part B draws
def run_more_e3(configs, data_root, out: Path, e1_out: Path, device: str, models, log) -> None:
    for config in configs:
        s = D.load_config(config, data_root)
        sets = [(share, d, switched_off(len(s.mac_cols), share, d)) for share in SHARES_B[1:] for d in DRAWS_D]
        X_all = []
        for share, d, off in sets:
            X = s.X_test.copy()
            X[:, off] = D.NOT_DETECTED
            X_all.append(X)
        X_all = np.vstack(X_all)
        for model in models:
            rid = f"{config}__{model}"
            path = out / "logs" / "e3more" / f"{rid}.json"
            if path.exists():
                continue
            params = {}
            if model in TUNED:
                params = params_from_json(read_json(e1_out / "config" / "best_params" / f"{config}__{model}.json")["best_params"])
            m = make_model(model, params, seed=0, n_jobs=usable_cpus(), device=device)
            m.fit(s.X_train, s.y_train, s.rp_train)
            chunk, preds = 10_000, []
            for i in range(0, len(X_all), chunk):
                preds.append(np.asarray(m.predict(X_all[i:i + chunk]), dtype=float))
            pred = np.vstack(preds)
            n = len(s.X_test)
            per_set = []
            for j, (share, d, off) in enumerate(sets):
                err = positioning_error(s.y_test, pred[j * n:(j + 1) * n])
                per_set.append(dict(share=share, draw=d, n_off=int(len(off)), **error_stats(err)))
            write_json(path, dict(config=config, model=model, seed=0, params=params_to_json(params), draws=DRAWS_D,
                                  per_set=per_set, node=node_tag(), code_commit=git_commit(), finished_utc=now_utc()))
            log.info(f"done D {rid} share60_mean={np.mean([r['mean'] for r in per_set if r['share'] == 60]):.3f}")


# ----------------------------------------------------------------------------- command line
def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["gpu", "own", "report"])
    p.add_argument("--out", default="results/P1-E03")
    p.add_argument("--e1-out", default="results/P1-E01")
    p.add_argument("--e2-out", default="results/P1-E02")
    p.add_argument("--data", default=D.DEFAULT_ROOT)
    p.add_argument("--configs", nargs="+", default=D.ALL_CONFIGS, choices=D.ALL_CONFIGS)
    p.add_argument("--parts", nargs="+", default=["A", "B", "C"], choices=["A", "B", "C"])
    p.add_argument("--device", default="cuda")
    a = p.parse_args(argv)
    out, e1_out = Path(a.out), Path(a.e1_out)
    if a.command == "report":
        from .report_e3x import write_report

        write_report(out, e1_out, Path(a.e2_out), a.data)
        return
    register_session("e2")  # paused, like P1-E02, while a P1-E01 timed run is going
    log = get_logger(f"e3x.{a.command}", out / "logs" / f"{a.command}_{node_tag()}.log")
    log.info(f"{a.command}: configs={a.configs} parts={a.parts} node={node_tag()}")
    if a.command == "gpu":
        if "A" in a.parts:
            run_uncertainty(a.configs, a.data, out, a.device, log)
        if "B" in a.parts:
            run_scans(a.configs, a.data, out, e1_out, a.device, log)
        if "C" in a.parts:
            run_seeds(a.configs, a.data, out, a.device, log)
    else:
        run_more_e3([c for c in a.configs if c in D.MAIN_CONFIGS], a.data, out, e1_out, a.device, list(ALL_MODELS), log)
    log.info(f"{a.command}: finished")


if __name__ == "__main__":
    main()
