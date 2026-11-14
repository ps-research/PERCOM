"""P1-E01: pipeline check (Part A) and full-survey comparison (Part B).

    python -m p1.e1 gate    --out results/P1-E01
    python -m p1.e1 search  --out results/P1-E01 --configs HCXY-All --workers 3 --threads 12
    python -m p1.e1 final   --out results/P1-E01 --configs HCXY-All
    python -m p1.e1 partb   --out results/P1-E01 --configs HCXY-All --workers 3 --threads 12   (search, then final)
    python -m p1.e1 report  --out results/P1-E01

Every unit of work (one search, one fit-and-predict run) writes its own files and
is skipped when they already exist, so a stopped job can be started again.
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

from . import data as D
from .common import get_logger, git_commit, node_tag, now_utc, read_json, write_json
from .metrics import STAT_NAMES, bootstrap_mean_difference, error_stats, mae_per_coordinate, positioning_error
from .models import (ALL_MODELS, BASELINES, BLAS_THREADS, ENCODING, LGBM_THREADS, SEEDED, SVR_CACHE_MB, TFMS, TUNED,
                     is_gpu_model, is_out_of_memory, make_model, timed_fit_predict)
from .tuning import N_TRIALS, params_from_json, params_to_json, run_search

SEEDS = [0, 1, 2, 3, 4]
GATE_TOLERANCE_M = 0.05
# Table 5 of briefs/P1-E01.md: the dataset paper's kNN results.
PAPER_KNN = {
    "CETC331": dict(mean=2.876, p50=2.316, p75=3.803, p95=6.307),
    "HCXY-All": dict(mean=2.365, p50=1.470, p75=3.231, p95=6.627),
    "SYL-All": dict(mean=4.656, p50=3.842, p75=6.078, p95=8.521),
}


def run_id(config: str, model: str, seed: int) -> str:
    return f"{config}__{model}__seed{seed}"


def seeds_of(model: str) -> list[int]:
    return SEEDS if model in SEEDED else [0]


# --------------------------------------------------------------------------- Part A
def gate(data_root: str, out: Path) -> dict:
    """Steps 2 to 6: check the counts, then re-create the dataset paper's kNN numbers."""
    from sklearn.neighbors import KNeighborsRegressor

    counts = D.count_table(data_root)
    (out / "metrics").mkdir(parents=True, exist_ok=True)
    counts.to_csv(out / "metrics" / "e0_counts.csv", index=False)
    if not counts["ok"].all():
        result = dict(counts_ok=False, gate_passed=False, written_utc=now_utc())
        write_json(out / "logs" / "e0_gate.json", result)
        return result

    rows = []
    for config in D.MAIN_CONFIGS:
        s = D.load_config(config, data_root)
        for label, how in (("left as 100", "raw"), ("placeholder -105", "placeholder")):
            knn = KNeighborsRegressor(n_neighbors=5, weights="distance", metric="euclidean")
            pred = knn.fit(D.encode(s.X_train, how), s.y_train).predict(D.encode(s.X_test, how))
            err = positioning_error(s.y_test, pred)
            ours = dict(mean=err.mean(), p50=np.percentile(err, 50), p75=np.percentile(err, 75),
                        p95=np.percentile(err, 95))
            row = dict(config=config, not_detected=label)
            for k in ("mean", "p50", "p75", "p95"):
                row[f"{k}_m"] = float(ours[k])
                row[f"paper_{k}_m"] = PAPER_KNN[config][k]
                row[f"diff_{k}_m"] = float(ours[k] - PAPER_KNN[config][k])
            row["mae_per_coordinate_m"] = mae_per_coordinate(s.y_test, pred)
            row["mean_within_tolerance"] = bool(abs(row["diff_mean_m"]) <= GATE_TOLERANCE_M)
            rows.append(row)
    table = pd.DataFrame(rows)
    table.to_csv(out / "metrics" / "e0_check.csv", index=False)
    passed_by = [label for label, g in table.groupby("not_detected", sort=False) if g["mean_within_tolerance"].all()]
    result = dict(counts_ok=True, gate_passed=bool(passed_by), passed_with=passed_by, tolerance_m=GATE_TOLERANCE_M,
                  knn="KNeighborsRegressor(n_neighbors=5, weights='distance', metric='euclidean')",
                  dataset_commit=git_commit(data_root), code_commit=git_commit(), node=node_tag(),
                  written_utc=now_utc())
    write_json(out / "logs" / "e0_gate.json", result)
    return result


def require_gate(out: Path) -> None:
    path = out / "logs" / "e0_gate.json"
    if not path.exists() or not read_json(path).get("gate_passed"):
        raise SystemExit("The pipeline check (Part A) has not passed. Nothing else runs until it does.")


# --------------------------------------------------------------------------- Part B: search
def best_params_path(out: Path, config: str, model: str) -> Path:
    return out / "config" / "best_params" / f"{config}__{model}.json"


def search_unit(config: str, model: str, data_root: str, out: str, threads: int, n_trials: int) -> str:
    out = Path(out)
    path = best_params_path(out, config, model)
    if path.exists():
        return f"skip {config} {model}"
    log = get_logger(f"search.{config}.{model}", out / "logs" / "search" / f"{config}__{model}.log")
    s = D.load_config(config, data_root)
    log.info(f"start search config={config} model={model} rows={len(s.X_train)} cols={len(s.mac_cols)} "
             f"threads={threads} node={node_tag()}")
    started = now_utc()
    res = run_search(model, s.X_train, s.y_train, s.rp_train, n_trials=n_trials, n_jobs=threads, log=log.info)
    (out / "logs" / "optuna").mkdir(parents=True, exist_ok=True)
    res["trials"].to_csv(out / "logs" / "optuna" / f"{config}__{model}.csv", index=False)
    write_json(path, dict(
        config=config, model=model, best_params=params_to_json(res["best_params"]), best_value=res["best_value"],
        best_trial=res["best_trial"], n_trials=res["n_trials"], search_seconds=res["search_seconds"],
        settings=res["settings"], encoding=ENCODING[model], threads=threads, node=node_tag(),
        code_commit=git_commit(), started_utc=started, finished_utc=now_utc(),
    ))
    log.info(f"done search config={config} model={model} best={res['best_value']:.4f} "
             f"seconds={res['search_seconds']:.0f} params={res['best_params']}")
    return f"done {config} {model} best={res['best_value']:.4f} in {res['search_seconds']:.0f}s"


def search(configs, models, data_root, out: Path, workers: int, threads: int, n_trials: int = N_TRIALS) -> None:
    require_gate(out)
    log = get_logger("search", out / "logs" / f"search_{node_tag()}.log")
    # Costly searches first, so the pool stays busy.
    order = {"mlp": 0, "lgbm-ph": 1, "lgbm-nan": 2, "svr": 3, "rf": 4, "knn": 5}
    units = sorted(((c, m) for c in configs for m in models), key=lambda u: order[u[1]])
    log.info(f"search: {len(units)} units, workers={workers}, threads per unit={threads}, trials={n_trials}")
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(search_unit, c, m, data_root, str(out), threads, n_trials): (c, m) for c, m in units}
        for fut in as_completed(futures):
            log.info(fut.result())
    log.info("search: all units finished")


# --------------------------------------------------------------------------- Part B: fit and predict
def run_record_path(out: Path, rid: str) -> Path:
    return out / "logs" / "runs" / f"{rid}.json"


def predictions_frame(s: D.Survey, pred: np.ndarray, err: np.ndarray) -> pd.DataFrame:
    return pd.DataFrame(dict(
        row=np.arange(len(pred)), test_point=s.tp_test, ECoord=s.y_test[:, 0], NCoord=s.y_test[:, 1],
        pred_ECoord=pred[:, 0], pred_NCoord=pred[:, 1], error_m=err,
    ))


def final_unit(config: str, model: str, seed: int, data_root: str, out: Path, device: str, log) -> dict | None:
    rid = run_id(config, model, seed)
    path = run_record_path(out, rid)
    if path.exists():
        log.info(f"skip {rid}")
        return None
    s = D.load_config(config, data_root)
    params = {}
    if model in TUNED:
        params = params_from_json(read_json(best_params_path(out, config, model))["best_params"])
    n_jobs = os.cpu_count() or 1
    started = now_utc()
    notes = []
    m = make_model(model, params, seed=seed, n_jobs=n_jobs, device=device)
    try:
        pred, cost = timed_fit_predict(m, s.X_train, s.y_train, s.rp_train, s.X_test)
    except Exception as exc:  # noqa: BLE001
        if model == "tabicl" and is_out_of_memory(exc):
            # Fallback written in the brief: the same capped context as TabPFN.
            notes.append(f"out of memory with every row as context ({type(exc).__name__}); context capped as for TabPFN")
            log.info(f"{rid}: out of memory, retrying with the capped context")
            del m
            m = make_model(model, params, seed=seed, n_jobs=n_jobs, device=device, cap_context=True)
            pred, cost = timed_fit_predict(m, s.X_train, s.y_train, s.rp_train, s.X_test)
        else:
            raise
    err = positioning_error(s.y_test, pred)
    (out / "metrics" / "predictions").mkdir(parents=True, exist_ok=True)
    predictions_frame(s, pred, err).to_csv(out / "metrics" / "predictions" / f"{rid}.csv.gz", index=False,
                                          float_format="%.6f", compression="gzip")
    record = dict(
        run_id=rid, config=config, model=model, seed=seed, single_run=model not in SEEDED,
        params=params_to_json(params), encoding=m.encoding, info=m.info, notes=notes,
        train_rows=len(s.X_train), n_features=len(s.mac_cols), test_rows=len(s.X_test),
        stats=error_stats(err), cost=cost, device=device if is_gpu_model(model) else "cpu",
        threads=dict(n_jobs=n_jobs, lgbm=LGBM_THREADS, blas=BLAS_THREADS, svr_cache_mb=SVR_CACHE_MB),
        node=node_tag(), code_commit=git_commit(), started_utc=started, finished_utc=now_utc(),
    )
    write_json(path, record)
    log.info(f"done {rid} mean={record['stats']['mean']:.3f} fit={cost['fit_s']:.1f}s predict={cost['predict_s']:.1f}s"
             + (f" gpu={cost['peak_gpu_mem_mb']:.0f}MB" if cost["peak_gpu_mem_mb"] is not None else ""))
    return record


def warm_up(models, data_root: str, device: str, log) -> None:
    """One small untimed call per tabular foundation model.

    Loads the weights from disk and starts CUDA, so that neither is counted in the
    first timed run. Nothing from this call is saved.
    """
    s = D.load_config("CETC331", data_root)
    for model in models:
        if not is_gpu_model(model):
            continue
        t0 = time.perf_counter()
        m = make_model(model, seed=0, device=device)
        m.fit(s.X_train[:64], s.y_train[:64], s.rp_train[:64])
        m.predict(s.X_test[:8])
        log.info(f"warm-up {model}: {time.perf_counter() - t0:.1f}s info={m.info}")


def final(configs, models, seeds, data_root, out: Path, device: str) -> None:
    require_gate(out)
    log = get_logger("final", out / "logs" / f"final_{node_tag()}.log")
    log.info(f"final: configs={configs} models={models} seeds={seeds} device={device} node={node_tag()}")
    warm_up(models, data_root, device, log)
    for config in configs:
        for model in models:
            for seed in (s for s in seeds_of(model) if s in seeds):
                final_unit(config, model, seed, data_root, out, device, log)
    log.info("final: all units finished")


# --------------------------------------------------------------------------- report
def load_runs(out: Path) -> pd.DataFrame:
    rows = []
    for path in sorted((out / "logs" / "runs").glob("*.json")):
        r = read_json(path)
        rows.append(dict(config=r["config"], model=r["model"], seed=r["seed"], **r["stats"],
                         fit_s=r["cost"]["fit_s"], predict_s=r["cost"]["predict_s"],
                         peak_gpu_mem_mb=r["cost"]["peak_gpu_mem_mb"]))
    df = pd.DataFrame(rows)
    df["config"] = pd.Categorical(df["config"], D.ALL_CONFIGS)
    df["model"] = pd.Categorical(df["model"], list(ALL_MODELS))
    return df.sort_values(["config", "model", "seed"]).reset_index(drop=True)


def missing_runs(out: Path, configs=D.ALL_CONFIGS) -> list[str]:
    want = [run_id(c, m, s) for c in configs for m in ALL_MODELS for s in seeds_of(m)]
    return [rid for rid in want if not run_record_path(out, rid).exists()]


def bootstrap_table(out: Path, summary: pd.DataFrame) -> pd.DataFrame:
    """Step 14: best tabular foundation model against best baseline, seed 0 of each."""
    mean_by = summary.groupby(["config", "model"], observed=True)["mean"].mean()
    rows = []
    for config in summary["config"].cat.categories:
        if config not in mean_by.index.get_level_values(0):
            continue
        m = mean_by.loc[config]
        tfms, bases = [x for x in m.index if x in TFMS], [x for x in m.index if x in BASELINES]
        if not tfms or not bases:
            continue  # nothing to compare yet (a partial run)
        tfm, base = m[tfms].idxmin(), m[bases].idxmin()
        pa = pd.read_csv(out / "metrics" / "predictions" / f"{run_id(config, tfm, 0)}.csv.gz")
        pb = pd.read_csv(out / "metrics" / "predictions" / f"{run_id(config, base, 0)}.csv.gz")
        assert (pa["test_point"].to_numpy() == pb["test_point"].to_numpy()).all()
        b = bootstrap_mean_difference(pa["error_m"].to_numpy(), pb["error_m"].to_numpy(), pa["test_point"].to_numpy(),
                                      n_resamples=10_000, seed=0)
        rows.append(dict(config=config, tfm=tfm, baseline=base, tfm_mean_over_seeds=float(m[tfm]),
                         baseline_mean_over_seeds=float(m[base]), tfm_mean_seed0=b["mean_a"],
                         baseline_mean_seed0=b["mean_b"], diff_tfm_minus_baseline=b["diff"], ci95_low=b["ci_low"],
                         ci95_high=b["ci_high"], n_resamples=b["n_resamples"], n_test_points=b["n_points"],
                         bootstrap_seed=b["bootstrap_seed"]))
    return pd.DataFrame(rows)


def report(out: Path, data_root: str) -> None:
    from .report_e1 import write_report

    write_report(out, data_root)


# --------------------------------------------------------------------------- command line
def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["gate", "search", "final", "partb", "report"])
    p.add_argument("--out", default="results/P1-E01")
    p.add_argument("--data", default=D.DEFAULT_ROOT)
    p.add_argument("--configs", nargs="+", default=D.ALL_CONFIGS, choices=D.ALL_CONFIGS)
    p.add_argument("--models", nargs="+", default=None)
    p.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    p.add_argument("--workers", type=int, default=2, help="searches that run at the same time")
    p.add_argument("--threads", type=int, default=6, help="threads of one search (its three folds run in parallel)")
    p.add_argument("--trials", type=int, default=N_TRIALS)
    p.add_argument("--device", default="cuda")
    a = p.parse_args(argv)
    out = Path(a.out)
    if a.command == "gate":
        result = gate(a.data, out)
        print(pd.read_csv(out / "metrics" / "e0_check.csv").to_string(index=False) if result["counts_ok"] else
              pd.read_csv(out / "metrics" / "e0_counts.csv").to_string(index=False))
        print(result)
        if not result["gate_passed"]:
            raise SystemExit(1)
    elif a.command == "search":
        search(a.configs, a.models or list(TUNED), a.data, out, a.workers, a.threads, a.trials)
    elif a.command == "final":
        final(a.configs, a.models or list(BASELINES + TFMS), a.seeds, a.data, out, a.device)
    elif a.command == "partb":
        # Part B for the given configurations: every search first, then the timed runs
        # one after the other, with nothing else running on the machine.
        search(a.configs, list(TUNED), a.data, out, a.workers, a.threads, a.trials)
        final(a.configs, a.models or list(BASELINES + TFMS), a.seeds, a.data, out, a.device)
    else:
        report(out, a.data)


if __name__ == "__main__":
    main()
