"""P1-E02 report: e2_summary, e2_crossing, e3_summary, predictions, figures, RESULTS.md.

Reads the merged P1-E02 output folder and the P1-E01 results folder (the 100% share
reuses P1-E01 where the model and the seed match).
"""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from . import data as D
from .common import now_utc, read_json, write_json
from .e2 import CONFIGS, DRAWS, KEPT_TABLE, REDUCED, SHARES_A, SHARES_B, check_kept_table, run_id
from .metrics import STAT_NAMES
from .models import ALL_MODELS, SEEDED, TFMS, TUNED
from .report_e1 import _md

STAT_LABELS = dict(mean="Mean", median="Median", p75="75th", p95="95th", rmse="RMS")


# ----------------------------------------------------------------------------- Part A table
def _e1_run(e1_out: Path, config: str, model: str, seed: int) -> dict:
    return read_json(e1_out / "logs" / "runs" / f"{config}__{model}__seed{seed}.json")


def e2_summary(out: Path, e1_out: Path) -> pd.DataFrame:
    rows, missing = [], []
    for config in CONFIGS:
        for share in SHARES_A:
            for draw in DRAWS:
                for model in ALL_MODELS:
                    source = "P1-E02"
                    if share == 100 and (model not in SEEDED or draw < 5):
                        seed = draw if model in SEEDED else 0
                        path = e1_out / "logs" / "runs" / f"{config}__{model}__seed{seed}.json"
                        source = f"P1-E01 seed {seed}" + ("" if model in SEEDED else " (no randomness; same run for every draw)")
                    else:
                        path = out / "logs" / "runs" / f"{run_id(config, share, draw, model)}.json"
                    if not path.exists():
                        missing.append(f"{config} {share}% draw {draw} {model}")
                        continue
                    r = read_json(path)
                    rows.append(dict(config=config, share=share, n_ref_points=KEPT_TABLE[config][share], draw=draw,
                                     model=model, seed=r["seed"], **r["stats"], fit_s=r["cost"]["fit_s"],
                                     predict_s=r["cost"]["predict_s"], source=source))
    df = pd.DataFrame(rows)
    df.attrs["missing"] = missing
    return df


def crossing(summary: pd.DataFrame) -> pd.DataFrame:
    """Smallest share at which each TFM's mean error (averaged over draws) is at or below tuned knn at 100%.

    Linear interpolation between neighbouring shares on a logarithmic share axis.
    """
    rows = []
    for config in CONFIGS:
        g = summary[summary["config"] == config]
        knn100 = g[(g["model"] == "knn") & (g["share"] == 100)]["mean"].mean()
        for model in TFMS:
            curve = g[g["model"] == model].groupby("share")["mean"].mean().reindex(SHARES_A)
            share_at, note = None, ""
            if curve.isna().any():
                note = "incomplete"
            elif curve.iloc[0] <= knn100:
                share_at, note = float(SHARES_A[0]), "already at or below at the smallest share"
            else:
                for i in range(1, len(SHARES_A)):
                    e0, e1 = curve.iloc[i - 1], curve.iloc[i]
                    if e1 <= knn100 < e0:
                        l0, l1 = np.log(SHARES_A[i - 1]), np.log(SHARES_A[i])
                        share_at = float(np.exp(l0 + (e0 - knn100) / (e0 - e1) * (l1 - l0)))
                        break
            above_after = bool(share_at is not None and (curve[[s for s in SHARES_A if s > share_at]] > knn100).any())
            rows.append(dict(config=config, model=model, knn_100_mean_m=float(knn100),
                             **{f"mean_at_{s}pct_m": float(curve[s]) for s in SHARES_A},
                             crossing_share_pct=round(share_at, 2) if share_at is not None else "not reached",
                             crossing_ref_points=(round(share_at / 100 * D.CONFIGS[config]["ref_points"], 1)
                                                  if share_at is not None else ""),
                             back_above_later=above_after, note=note))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- Part B table
def e3_summary(out: Path) -> pd.DataFrame:
    rows = []
    for config in CONFIGS:
        for model in ALL_MODELS:
            path = out / "logs" / "e3" / f"{config}__{model}.json"
            if not path.exists():
                continue
            r = read_json(path)
            for s in r["per_set"]:
                rows.append(dict(config=config, share=s["share"], n_off=s["n_off"], draw=s["draw"], model=model,
                                 **{k: s[k] for k in STAT_NAMES}))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- predictions
def consolidate_predictions(out: Path, e1_out: Path, report_dir: Path) -> list[str]:
    """One compressed CSV per (part, configuration, model) instead of one per run.

    Needs the per-run files; if they are gone (already consolidated and removed), the existing
    consolidated files are kept untouched rather than rewritten from the 100% rows alone.
    """
    pdir = report_dir / "metrics" / "predictions"
    pdir.mkdir(parents=True, exist_ok=True)
    if not (out / "metrics" / "predictions" / "parta").exists():
        kept = sorted(p.name for p in pdir.glob("e[23]_*.csv.gz"))
        print(f"  per-run predictions not present; keeping {len(kept)} consolidated files as they are")
        return kept
    written = []
    for config in CONFIGS:
        for model in ALL_MODELS:
            frames = []
            for share in SHARES_A:
                for draw in DRAWS:
                    if share == 100 and (model not in SEEDED or draw < 5):
                        seed = draw if model in SEEDED else 0
                        f = e1_out / "metrics" / "predictions" / f"{config}__{model}__seed{seed}.csv.gz"
                        if not f.exists():
                            continue
                        df = pd.read_csv(f)
                        df["in_kept"] = 1 if config == "CETC331" else 0  # filled exactly below
                    else:
                        f = out / "metrics" / "predictions" / "parta" / f"{run_id(config, share, draw, model)}.csv.gz"
                        if not f.exists():
                            continue
                        df = pd.read_csv(f)
                    df.insert(0, "draw", draw)
                    df.insert(0, "share", share)
                    frames.append(df)
            if frames:
                allp = pd.concat(frames, ignore_index=True)
                if (allp["share"] == 100).any():  # in_kept at 100%: the location is any reference point
                    s = D.load_config(config, "data/SODIndoorLoc") if Path("data/SODIndoorLoc").exists() else None
                    if s is not None:
                        ref = set(map(tuple, s.rp_table[D.POINT_COLS].to_numpy()))
                        tp_in = np.array([tuple(t) in ref for t in s.tp_table[D.POINT_COLS].to_numpy()])
                        mask = allp["share"] == 100
                        allp.loc[mask, "in_kept"] = tp_in[allp.loc[mask, "test_point"].to_numpy()].astype(int)
                name = pdir / f"e2_{config}__{model}.csv.gz"
                allp.to_csv(name, index=False, float_format="%.4f", compression="gzip")
                written.append(name.name)
            f3 = out / "metrics" / "predictions" / "e3" / f"{config}__{model}.csv.gz"
            if f3.exists():
                shutil.copyfile(f3, pdir / f"e3_{config}__{model}.csv.gz")
                written.append(f"e3_{config}__{model}.csv.gz")
    return written


# ----------------------------------------------------------------------------- figures
def write_figures(report_dir: Path, s2: pd.DataFrame, s3: pd.DataFrame) -> None:
    fig_dir = report_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    s2[["config", "share", "draw", "model", "mean"]].to_csv(fig_dir / "e2_reference_points.csv", index=False)
    s3[["config", "share", "draw", "model", "mean"]].to_csv(fig_dir / "e3_missing_aps.csv", index=False)
    script = Path(__file__).with_name("plot_e2_curves.py")
    shutil.copyfile(script, fig_dir / "plot_e2_curves.py")
    import runpy
    import sys

    argv = sys.argv
    try:
        for name, xlabel, logx in (("e2_reference_points", "Share of reference points kept (%)", "log"),
                                   ("e3_missing_aps", "Share of access points switched off (%)", "linear")):
            sys.argv = [str(script), str(fig_dir / f"{name}.csv"), xlabel, logx]
            runpy.run_path(str(fig_dir / "plot_e2_curves.py"), run_name="__main__")
    finally:
        sys.argv = argv


# ----------------------------------------------------------------------------- tables for RESULTS.md
def _pm(v: pd.Series) -> str:
    return f"{v.mean():.2f} ± {v.std(ddof=1):.2f}" if len(v) > 1 and v.std(ddof=1) > 0 else f"{v.mean():.2f}"


def share_table(df: pd.DataFrame, config: str, shares, label: str) -> pd.DataFrame:
    g = df[df["config"] == config]
    rows = []
    for model in ALL_MODELS:
        gm = g[g["model"] == model]
        if gm.empty:
            continue
        row = {"Model": f"`{model}`"}
        for s in shares:
            v = gm[gm["share"] == s]["mean"]
            row[f"{s}{label}"] = _pm(v) if len(v) else "-"
        rows.append(row)
    return pd.DataFrame(rows)


def stats_table(df: pd.DataFrame, config: str, share: int) -> pd.DataFrame:
    g = df[(df["config"] == config) & (df["share"] == share)]
    rows = []
    for model in ALL_MODELS:
        gm = g[g["model"] == model]
        if gm.empty:
            continue
        rows.append({"Model": f"`{model}`", "Draws": len(gm),
                     **{f"{STAT_LABELS[s]} (m)": _pm(gm[s]) for s in STAT_NAMES}})
    return pd.DataFrame(rows)


def write_report(out: Path, e1_out: Path, data_root: str) -> None:
    out, e1_out = Path(out), Path(e1_out)
    report_dir = out
    s2 = e2_summary(out, e1_out)
    s2.to_csv(report_dir / "metrics" / "e2_summary.csv", index=False)
    cr = crossing(s2)
    cr.to_csv(report_dir / "metrics" / "e2_crossing.csv", index=False)
    s3 = e3_summary(out)
    s3.to_csv(report_dir / "metrics" / "e3_summary.csv", index=False)
    written = consolidate_predictions(out, e1_out, report_dir)
    write_figures(report_dir, s2, s3)

    # config/: every search's best values and the exact configuration of every run
    best = {}
    for path in sorted((out / "config" / "e2_params").glob("*.json")):
        r = read_json(path)
        best.setdefault(r["config"], {}).setdefault(f"{r['share']}%", {}).setdefault(f"draw {r['draw']}", {})[r["model"]] = \
            dict(best_params=r["best_params"], best_cv_mean_error_m=r["best_value"], n_trials=r["n_trials"],
                 search_seconds=r["search_seconds"])
    write_json(report_dir / "config" / "e2_best_params.json", best)
    runs = {}
    for path in sorted((out / "logs" / "runs").glob("*.json")):
        r = read_json(path)
        runs[r["run_id"]] = {k: r.get(k) for k in ("config", "share", "draw", "seed", "model", "n_ref_points",
                                                   "train_rows", "params", "encoding", "info", "device", "n_jobs",
                                                   "node", "code_commit", "started_utc", "finished_utc")}
    for path in sorted((out / "logs" / "e3").glob("*.json")):
        r = read_json(path)
        runs[f"e3__{r['config']}__{r['model']}"] = {k: r.get(k) for k in (
            "config", "model", "seed", "params", "encoding", "info", "n_sets", "stacked_rows", "chunk_rows",
            "node", "code_commit", "finished_utc")}
    write_json(report_dir / "config" / "run_configs.json", runs)

    L: list[str] = []
    add = L.append
    add("# P1-E02 results: fewer reference points, and access points that go missing\n")
    add(f"Brief: `briefs/P1-E02.md`, revision 1. Report written {now_utc()}.\n")
    notes = out / "NOTES.md"
    if notes.exists():
        add(notes.read_text().strip() + "\n")

    kt = check_kept_table()
    add("## Part A. Fewer reference points (E2)\n")
    add(f"Reference points kept, as in the brief's table: {'all counts match' if kt['ok'].all() else 'MISMATCH'} "
        "(share times the number of reference points, rounded up). Draw `d` shuffles the reference points with "
        "`numpy.random.default_rng(d).permutation` and keeps the first ones, so each smaller survey is inside the "
        "larger one. The baselines were re-tuned on every reduced survey (30 Optuna trials, 3-fold GroupKFold by "
        "reference point) and refitted with seed `d`; the tabular foundation models used the reduced survey as "
        "context with seed `d`. The full test file was always predicted.\n")
    add("The 100% share reuses P1-E01: seeds 0 to 4 of the seeded models are the P1-E01 runs, seeds 5 to 9 were run "
        "here with the P1-E01 best values; `knn`, `svr` and `gp` have no randomness, so their one P1-E01 run stands "
        "for every draw.\n")
    if s2.attrs.get("missing"):
        add(f"**Missing runs ({len(s2.attrs['missing'])}):** " + "; ".join(s2.attrs["missing"][:40]) + "\n")
    for config in CONFIGS:
        add(f"### {config}: mean positioning error (m), mean ± std over 10 draws\n")
        add(_md(share_table(s2, config, SHARES_A, "%")) + "\n")
    add("### Smallest share at which each tabular foundation model reaches tuned kNN at 100%\n")
    add("Mean error averaged over draws, against the mean error of tuned `knn` on the full survey; linear "
        "interpolation between shares on a logarithmic share axis. Source: `metrics/e2_crossing.csv`.\n")
    show = cr[["config", "model", "knn_100_mean_m"] + [f"mean_at_{s}pct_m" for s in SHARES_A]
              + ["crossing_share_pct", "crossing_ref_points", "back_above_later"]].copy()
    for c in show.columns:
        if c.endswith("_m"):
            show[c] = show[c].map(lambda v: f"{v:.3f}")
    show.columns = ["Config", "Model", "kNN at 100% (m)"] + [f"{s}% (m)" for s in SHARES_A] + \
                   ["Crossing share (%)", "Crossing ref. points", "Above kNN again later"]
    show["Model"] = show["Model"].map(lambda v: f"`{v}`")
    add(_md(show) + "\n")
    if (s2["config"] == "CETC331").any():
        g = s2
        add("In CETC331 every test location is also a reference-point location. Per-row predictions record "
            "whether the test row's location is among the kept reference points (`in_kept`).\n")

    add("## Part B. Access points that go missing after the survey (E3)\n")
    add("Each model was fitted once per configuration on the whole training file, with seed 0 and, for the "
        "baselines, the P1-E01 best values. In every test row, the switched-off columns were set to \"not "
        "detected\" and then written the way the model expects (NaN or -105). Draw `d` shuffles the MAC columns with "
        "`numpy.random.default_rng(d).permutation` and switches off the first ones. The altered copies of a test "
        f"file were stacked and predicted in chunks of {20_000:,} rows.\n")
    for config in CONFIGS:
        if s3.empty or not (s3["config"] == config).any():
            continue
        ncols = D.CONFIGS[config]["rss_cols"]
        add(f"### {config} ({ncols} MAC columns): mean positioning error (m), mean ± std over 10 draws\n")
        add(_md(share_table(s3, config, SHARES_B, "%")) + "\n")
    if not s3.empty:
        chk = []
        for config in CONFIGS:
            for model in ALL_MODELS:
                a = s3[(s3["config"] == config) & (s3["model"] == model) & (s3["share"] == 0)]["mean"]
                p = e1_out / "logs" / "runs" / f"{config}__{model}__seed0.json"
                if len(a) and p.exists():
                    chk.append(dict(config=config, model=model, e3_0pct=float(a.iloc[0]),
                                    e1_seed0=read_json(p)["stats"]["mean"]))
        chk = pd.DataFrame(chk)
        if len(chk):
            chk["abs_diff"] = (chk["e3_0pct"] - chk["e1_seed0"]).abs()
            chk.to_csv(report_dir / "metrics" / "e3_check_against_e1.csv", index=False)
            add(f"Check: at 0% switched off, the Part B fits reproduce the P1-E01 seed-0 mean error with a largest "
                f"absolute difference of {chk['abs_diff'].max():.4f} m over {len(chk)} configuration-model pairs "
                "(`metrics/e3_check_against_e1.csv`).\n")

    add("## Figures\n")
    add("- `figures/e2_reference_points.pdf` / `.png`: mean error against share of reference points kept "
        "(logarithmic axis), one line per model, band from the lowest to the highest draw; one panel per "
        "configuration and one averaged over the three.\n")
    add("- `figures/e3_missing_aps.pdf` / `.png`: mean error against share of access points switched off, same "
        "style.\n")
    add("Each figure is produced by `figures/plot_e2_curves.py` from the CSV next to it.\n")
    add(f"Per-row predictions: {len(written)} files in `metrics/predictions/` (one per part, configuration and "
        "model; Part A files carry `share`, `draw` and `in_kept`, Part B files carry `share`, `draw` and `n_off`).\n")
    (report_dir / "RESULTS.md").write_text("\n".join(L).rstrip() + "\n")
