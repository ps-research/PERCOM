"""P1-E02: fewer reference points (Part A, E2) and access points that go missing (Part B, E3).

    python -m p1.e2 parta  --out OUT --configs HCXY-All --draws 0 1 2 --workers 4 --threads 6
    python -m p1.e2 full   --out OUT --e1-out E1_OUT --configs HCXY-All     (100% share, seeds 5 to 9)
    python -m p1.e2 e3     --out OUT --e1-out E1_OUT --configs HCXY-All
    python -m p1.e2 report --out results/P1-E02 --e1-out results/P1-E01

Everything not stated in the brief is as in P1-E01 and uses its code. Every unit
of work writes its own files and is skipped when they exist, so a stopped job can
be started again.
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import threading
import time
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

import numpy as np
import pandas as pd

from . import data as D
from .common import get_logger, git_commit, node_tag, now_utc, read_json, register_session, usable_cpus, write_json
from .metrics import error_stats, positioning_error
from .models import (ALL_MODELS, BASELINES, BLAS_THREADS, ENCODING, LGBM_THREADS, SEEDED, TFMS, TUNED, is_gpu_model,
                     make_model, timed_fit_predict)
from .tuning import N_TRIALS, params_from_json, params_to_json, run_search

CONFIGS = D.MAIN_CONFIGS
SHARES_A = [5, 10, 25, 50, 100]  # percent of reference points kept
REDUCED = [5, 10, 25, 50]
DRAWS = list(range(10))
SHARES_B = [0, 10, 20, 30, 40, 50, 60]  # percent of MAC columns switched off
# Table of briefs/P1-E02.md, step 1.
KEPT_TABLE = {
    "CETC331": {5: 48, 10: 96, 25: 239, 50: 478, 100: 955},
    "HCXY-All": {5: 19, 10: 38, 25: 95, 50: 190, 100: 379},
    "SYL-All": {5: 15, 10: 30, 25: 74, 50: 148, 100: 296},
}
E3_CHUNK_ROWS = 20_000  # rows per predict call when the altered test files are stacked


# ----------------------------------------------------------------------------- draws
def ceil_share(share: int, n: int) -> int:
    """share percent of n, rounded up, in integer arithmetic."""
    return -(-share * n // 100)


def kept_points(n_rp: int, share: int, draw: int) -> np.ndarray:
    """Reference points kept in draw ``draw``: shuffle with seed ``draw``, keep the first ones.

    The shuffle is ``numpy.random.default_rng(draw).permutation``. A smaller share keeps a
    prefix of the same order, so within a draw each smaller survey is inside the larger one.
    """
    order = np.random.default_rng(draw).permutation(n_rp)
    return np.sort(order[: ceil_share(share, n_rp)])


def switched_off(n_cols: int, share: int, draw: int) -> np.ndarray:
    """MAC columns switched off in draw ``draw`` (same nesting rule as ``kept_points``)."""
    order = np.random.default_rng(draw).permutation(n_cols)
    return np.sort(order[: ceil_share(share, n_cols)])


def check_kept_table() -> pd.DataFrame:
    rows = []
    for config, row in KEPT_TABLE.items():
        n = D.CONFIGS[config]["ref_points"]
        for share, expected in row.items():
            rows.append(dict(config=config, share=share, expected=expected, found=ceil_share(share, n)))
    df = pd.DataFrame(rows)
    df["ok"] = df["expected"] == df["found"]
    return df


def unit_id(config: str, share: int, draw: int) -> str:
    return f"{config}__s{share:03d}__d{draw}"


def run_id(config: str, share: int, draw: int, model: str) -> str:
    return f"{unit_id(config, share, draw)}__{model}"


def reduced_survey(s: D.Survey, share: int, draw: int):
    """Training rows of the kept reference points, and which test rows sit at a kept location."""
    kept = kept_points(s.n_ref_points, share, draw)
    rows = np.isin(s.rp_train, kept)
    kept_loc = set(map(tuple, s.rp_table.loc[s.rp_table["id"].isin(kept), D.POINT_COLS].to_numpy()))
    tp_loc = s.tp_table[D.POINT_COLS].to_numpy()
    tp_in = np.array([tuple(t) in kept_loc for t in tp_loc])
    return s.X_train[rows], s.y_train[rows], s.rp_train[rows], kept, tp_in[s.tp_test]


# ----------------------------------------------------------------------------- one fit and predict
def _save_run(out: Path, rid: str, s: D.Survey, pred: np.ndarray, in_kept: np.ndarray, record: dict,
              subdir: str = "parta") -> dict:
    err = positioning_error(s.y_test, pred)
    pdir = out / "metrics" / "predictions" / subdir
    pdir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(dict(
        row=np.arange(len(pred)), test_point=s.tp_test, ECoord=s.y_test[:, 0], NCoord=s.y_test[:, 1],
        pred_ECoord=pred[:, 0], pred_NCoord=pred[:, 1], error_m=err, in_kept=in_kept.astype(int),
    )).to_csv(pdir / f"{rid}.csv.gz", index=False, float_format="%.6f", compression="gzip")
    record.update(stats=error_stats(err), in_kept_rows=int(in_kept.sum()),
                  mean_error_in_kept=float(err[in_kept].mean()) if in_kept.any() else None,
                  mean_error_not_in_kept=float(err[~in_kept].mean()) if (~in_kept).any() else None,
                  node=node_tag(), code_commit=git_commit(), finished_utc=now_utc())
    write_json(out / "logs" / "runs" / f"{rid}.json", record)
    return record


def fit_one(config: str, share: int, draw: int, model: str, params: dict, data_root: str, out: Path,
            n_jobs: int, device: str, s: D.Survey | None = None) -> dict | None:
    """Fit ``model`` on the survey of (config, share, draw) with seed ``draw``; predict the full test file."""
    rid = run_id(config, share, draw, model)
    if (out / "logs" / "runs" / f"{rid}.json").exists():
        return None
    s = s or D.load_config(config, data_root)
    if share == 100:
        X, y, rp = s.X_train, s.y_train, s.rp_train
        kept = np.arange(s.n_ref_points)
        _, _, _, _, in_kept = reduced_survey(s, 100, 0)
    else:
        X, y, rp, kept, in_kept = reduced_survey(s, share, draw)
    started = now_utc()
    m = make_model(model, params, seed=draw, n_jobs=n_jobs, device=device)
    pred, cost = timed_fit_predict(m, X, y, rp, s.X_test)
    record = dict(run_id=rid, config=config, share=share, draw=draw, seed=draw, model=model,
                  n_ref_points=int(len(kept)), train_rows=int(len(X)), n_features=len(s.mac_cols),
                  test_rows=len(s.X_test), params=params_to_json(params), encoding=m.encoding, info=m.info,
                  cost=cost, device=device if is_gpu_model(model) else "cpu", n_jobs=n_jobs,
                  lgbm_threads=LGBM_THREADS, blas_threads=BLAS_THREADS, started_utc=started)
    return _save_run(out, rid, s, pred, in_kept, record)


# ----------------------------------------------------------------------------- Part A tasks (run in workers)
def params_path(out: Path, config: str, share: int, draw: int, model: str) -> Path:
    return out / "config" / "e2_params" / f"{run_id(config, share, draw, model)}.json"


def search_task(config, share, draw, model, data_root, out, threads, n_trials) -> str:
    out = Path(out)
    path = params_path(out, config, share, draw, model)
    if path.exists():
        return f"skip search {run_id(config, share, draw, model)}"
    rid = run_id(config, share, draw, model)
    log = get_logger(f"e2s.{rid}", out / "logs" / "search" / f"{rid}.log")
    s = D.load_config(config, data_root)
    X, y, rp, kept, _ = reduced_survey(s, share, draw)
    log.info(f"start search {rid} ref_points={len(kept)} rows={len(X)} threads={threads} node={node_tag()}")
    started = now_utc()
    res = run_search(model, X, y, rp, n_trials=n_trials, n_jobs=threads, log=log.info)
    (out / "logs" / "optuna").mkdir(parents=True, exist_ok=True)
    res["trials"].to_csv(out / "logs" / "optuna" / f"{rid}.csv", index=False)
    write_json(path, dict(config=config, share=share, draw=draw, model=model, n_ref_points=int(len(kept)),
                          train_rows=int(len(X)), best_params=params_to_json(res["best_params"]),
                          best_value=res["best_value"], best_trial=res["best_trial"], n_trials=res["n_trials"],
                          search_seconds=res["search_seconds"], settings=res["settings"], encoding=ENCODING[model],
                          threads=threads, lgbm_threads=LGBM_THREADS, blas_threads=BLAS_THREADS, node=node_tag(),
                          code_commit=git_commit(), started_utc=started,
                          finished_utc=now_utc()))
    log.info(f"done search {rid} best={res['best_value']:.4f} seconds={res['search_seconds']:.0f}")
    return f"done search {rid} best={res['best_value']:.4f} in {res['search_seconds']:.0f}s"


def baseline_fit_task(config, share, draw, data_root, out, threads) -> str:
    """Refit the tuned baselines with seed ``draw`` and fit ``gp``, all on the reduced survey."""
    out = Path(out)
    s = D.load_config(config, data_root)
    done = []
    for model in BASELINES:
        params = {}
        if model in TUNED:
            params = params_from_json(read_json(params_path(out, config, share, draw, model))["best_params"])
        r = fit_one(config, share, draw, model, params, data_root, out, n_jobs=threads, device="cpu", s=s)
        if r:
            done.append(f"{model}={r['stats']['mean']:.3f}")
    return f"done fits {unit_id(config, share, draw)} " + " ".join(done)


def _unit_complete(out: Path, config: str, share: int, draw: int) -> bool:
    return all((out / "logs" / "runs" / f"{run_id(config, share, draw, m)}.json").exists() for m in ALL_MODELS)


def _mark_unit(out: Path, config: str, share: int, draw: int) -> None:
    if _unit_complete(out, config, share, draw):
        write_json(out / "logs" / "units" / f"{unit_id(config, share, draw)}.json",
                   dict(config=config, share=share, draw=draw, node=node_tag(), finished_utc=now_utc()))


def tfm_lane(units, data_root: str, out: Path, device: str, log) -> None:
    """GPU lane: the tabular foundation models need no search, so they run alongside the searches."""
    cache: dict[str, D.Survey] = {}
    for config, share, draw in units:
        s = cache.setdefault(config, D.load_config(config, data_root))
        for model in TFMS:
            try:
                r = fit_one(config, share, draw, model, {}, data_root, out, n_jobs=1, device=device, s=s)
            except Exception as exc:  # noqa: BLE001
                log.info(f"ERROR tfm {run_id(config, share, draw, model)}: {type(exc).__name__}: {exc}")
                raise
            if r:
                log.info(f"done tfm {r['run_id']} mean={r['stats']['mean']:.3f} fit={r['cost']['fit_s']:.1f}s "
                         f"gpu={r['cost']['peak_gpu_mem_mb']:.0f}MB")
        _mark_unit(out, config, share, draw)
    log.info("tfm lane finished")


def parta(configs, draws, shares, data_root, out: Path, workers: int, threads: int, n_trials: int, device: str,
          with_tfm: bool = True):
    register_session("e2")
    log = get_logger("e2a", out / "logs" / f"parta_{node_tag()}.log")
    bad = check_kept_table()
    if not bad["ok"].all():
        raise SystemExit(f"kept-point counts differ from the brief:\n{bad[~bad['ok']]}")
    # Costly units first (larger surveys), so the tail of the job is short.
    units = sorted(((c, sh, d) for c in configs for d in draws for sh in shares), key=lambda u: (-u[1], u[2], u[0]))
    log.info(f"parta: {len(units)} units, configs={configs} draws={draws} shares={shares} workers={workers} "
             f"threads={threads} trials={n_trials} cpus={usable_cpus()} node={node_tag()}")
    errors: list[BaseException] = []

    def _gpu():
        try:
            tfm_lane(units, data_root, out, device, log)
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    gpu = threading.Thread(target=_gpu if with_tfm else (lambda: None), name="tfm-lane")
    gpu.start()
    order = {"mlp": 0, "lgbm-ph": 1, "lgbm-nan": 2, "svr": 3, "rf": 4, "knn": 5}
    searches = deque((u, m) for u in units for m in sorted(TUNED, key=order.get))
    remaining = {u: set(TUNED) for u in units}
    fits: deque = deque()
    in_flight = {}
    with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("spawn")) as pool:
        def submit_next():
            if fits:
                u = fits.popleft()
                f = pool.submit(baseline_fit_task, *u, data_root, str(out), threads)
                in_flight[f] = ("fit", u, None)
                return True
            if searches:
                u, m = searches.popleft()
                f = pool.submit(search_task, *u, m, data_root, str(out), threads, n_trials)
                in_flight[f] = ("search", u, m)
                return True
            return False

        while len(in_flight) < workers and submit_next():
            pass
        while in_flight:
            finished, _ = wait(list(in_flight), return_when=FIRST_COMPLETED)
            for f in finished:
                kind, u, m = in_flight.pop(f)
                msg = f.result()  # an exception here stops the job, as the brief asks
                log.info(msg)
                if kind == "search":
                    remaining[u].discard(m)
                    if not remaining[u]:
                        fits.append(u)
                else:
                    _mark_unit(out, *u)
            while len(in_flight) < workers and submit_next():
                pass
    gpu.join()
    if errors:
        raise errors[0]
    for u in units:
        _mark_unit(out, *u)
    log.info("parta: all units finished")


def tfm_only(configs, draws, shares, data_root, out: Path, device: str) -> None:
    """Part A runs of the tabular foundation models only (GPU); the baselines come from ``parta``."""
    register_session("e2")
    log = get_logger("e2t", out / "logs" / f"tfm_{node_tag()}.log")
    units = sorted(((c, sh, d) for c in configs for d in draws for sh in shares), key=lambda u: (-u[1], u[2], u[0]))
    log.info(f"tfm: {len(units)} units, configs={configs} draws={draws} shares={shares} node={node_tag()}")
    tfm_lane(units, data_root, out, device, log)


# ----------------------------------------------------------------------------- 100% share, seeds 5 to 9
def full(configs, data_root, out: Path, e1_out: Path, device: str, models=None) -> None:
    """The 100% share: P1-E01 has seeds 0 to 4; draws 5 to 9 need seeds 5 to 9 of the seeded models."""
    register_session("e2")
    log = get_logger("e2f", out / "logs" / f"full_{node_tag()}.log")
    for config in configs:
        s = D.load_config(config, data_root)
        for model in (m for m in SEEDED if models is None or m in models):
            params = {}
            if model in TUNED:
                params = params_from_json(read_json(e1_out / "config" / "best_params" / f"{config}__{model}.json")["best_params"])
            for draw in DRAWS[5:]:
                r = fit_one(config, 100, draw, model, params, data_root, out, n_jobs=usable_cpus(), device=device, s=s)
                if r:
                    log.info(f"done {r['run_id']} mean={r['stats']['mean']:.3f}")
    log.info("full: finished")


# ----------------------------------------------------------------------------- Part B (E3)
def altered_sets(s: D.Survey) -> list[tuple[int, int, np.ndarray]]:
    """(share, draw, switched-off column indices): the 0% share once, every other share for every draw."""
    sets = [(0, 0, np.array([], dtype=int))]
    for share in SHARES_B[1:]:
        for draw in DRAWS:
            sets.append((share, draw, switched_off(len(s.mac_cols), share, draw)))
    return sets


def e3(configs, data_root, out: Path, e1_out: Path, device: str, models=None) -> None:
    register_session("e2")
    log = get_logger("e3", out / "logs" / f"e3_{node_tag()}.log")
    for config in configs:
        s = D.load_config(config, data_root)
        sets = altered_sets(s)
        stacked = []
        for share, draw, off in sets:
            X = s.X_test.copy()
            X[:, off] = D.NOT_DETECTED  # the model then writes it as NaN or -105, as it expects
            stacked.append(X)
        X_all = np.vstack(stacked)
        for model in (m for m in ALL_MODELS if models is None or m in models):
            rid = f"{config}__{model}"
            path = out / "logs" / "e3" / f"{rid}.json"
            if path.exists():
                log.info(f"skip e3 {rid}")
                continue
            params = {}
            if model in TUNED:
                params = params_from_json(read_json(e1_out / "config" / "best_params" / f"{config}__{model}.json")["best_params"])
            m = make_model(model, params, seed=0, n_jobs=usable_cpus(), device=device)
            t0 = time.perf_counter()
            m.fit(s.X_train, s.y_train, s.rp_train)
            t1 = time.perf_counter()
            chunk = E3_CHUNK_ROWS
            while True:
                try:
                    pred = np.vstack([np.asarray(m.predict(X_all[i:i + chunk]), dtype=float)
                                      for i in range(0, len(X_all), chunk)])
                    break
                except Exception as exc:  # noqa: BLE001
                    from .models import is_out_of_memory

                    if not is_out_of_memory(exc) or chunk <= len(s.X_test):
                        raise
                    chunk //= 2
                    log.info(f"{rid}: out of memory, predicting in chunks of {chunk} rows")
                    import torch

                    torch.cuda.empty_cache()
            t2 = time.perf_counter()
            n = len(s.X_test)
            frames, per_set = [], []
            for k, (share, draw, off) in enumerate(sets):
                p = pred[k * n:(k + 1) * n]
                err = positioning_error(s.y_test, p)
                per_set.append(dict(share=share, draw=draw, n_off=int(len(off)), **error_stats(err)))
                frames.append(pd.DataFrame(dict(
                    share=share, draw=draw, n_off=len(off), row=np.arange(n), test_point=s.tp_test,
                    ECoord=s.y_test[:, 0], NCoord=s.y_test[:, 1], pred_ECoord=p[:, 0], pred_NCoord=p[:, 1],
                    error_m=err)))
            pdir = out / "metrics" / "predictions" / "e3"
            pdir.mkdir(parents=True, exist_ok=True)
            pd.concat(frames).to_csv(pdir / f"{rid}.csv.gz", index=False, float_format="%.6f", compression="gzip")
            write_json(path, dict(config=config, model=model, seed=0, params=params_to_json(params),
                                  encoding=m.encoding, info=m.info, n_sets=len(sets), test_rows=n,
                                  stacked_rows=int(len(X_all)), chunk_rows=chunk, fit_s=t1 - t0,
                                  predict_s=t2 - t1, per_set=per_set, node=node_tag(), code_commit=git_commit(),
                                  finished_utc=now_utc()))
            log.info(f"done e3 {rid} share0_mean={per_set[0]['mean']:.3f} share60_mean="
                     f"{np.mean([r['mean'] for r in per_set if r['share'] == 60]):.3f} predict={t2 - t1:.1f}s")
    log.info("e3: finished")


# ----------------------------------------------------------------------------- command line
def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["parta", "tfm", "gpu", "own", "full", "e3", "report"])
    p.add_argument("--out", default="results/P1-E02")
    p.add_argument("--e1-out", default="results/P1-E01")
    p.add_argument("--data", default=D.DEFAULT_ROOT)
    p.add_argument("--configs", nargs="+", default=CONFIGS, choices=CONFIGS)
    p.add_argument("--draws", nargs="+", type=int, default=DRAWS)
    p.add_argument("--shares", nargs="+", type=int, default=REDUCED, choices=REDUCED)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--threads", type=int, default=6)
    p.add_argument("--trials", type=int, default=N_TRIALS)
    p.add_argument("--device", default="cuda")
    p.add_argument("--models", nargs="+", default=None, help="full and e3: only these models")
    p.add_argument("--no-tfm", action="store_true", help="parta: leave the foundation models to the gpu job")
    p.add_argument("--own", nargs="+", default=[], choices=CONFIGS,
                   help="gpu: configurations whose P1-E01 results are on this node (for e3 and full)")
    a = p.parse_args(argv)
    out, e1_out = Path(a.out), Path(a.e1_out)
    if a.command == "parta":
        parta(a.configs, a.draws, a.shares, a.data, out, a.workers, a.threads, a.trials, a.device,
              with_tfm=not a.no_tfm)
    elif a.command == "gpu":
        # Every GPU part of P1-E02 that needs no baseline search: Part A foundation-model runs
        # for the given draws, then Part B and the 100% seeds 5 to 9 of the foundation models
        # for the configurations whose P1-E01 results are on this node.
        tfm_only(a.configs, a.draws, a.shares, a.data, out, a.device)
        if a.own:
            e3(a.own, a.data, out, e1_out, a.device, models=list(TFMS))
            full(a.own, a.data, out, e1_out, a.device, models=list(TFMS))
    elif a.command == "own":
        # The baseline parts that need this node's P1-E01 best values: Part B, then the
        # 100% share with seeds 5 to 9.
        e3(a.configs, a.data, out, e1_out, a.device, models=list(BASELINES))
        full(a.configs, a.data, out, e1_out, a.device, models=[m for m in SEEDED if m in BASELINES])
    elif a.command == "tfm":
        tfm_only(a.configs, a.draws, a.shares, a.data, out, a.device)
    elif a.command == "full":
        full(a.configs, a.data, out, e1_out, a.device, models=a.models)
    elif a.command == "e3":
        e3(a.configs, a.data, out, e1_out, a.device, models=a.models)
    else:
        from .report_e2 import write_report

        write_report(out, e1_out, a.data)


if __name__ == "__main__":
    main()
