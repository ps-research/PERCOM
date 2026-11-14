"""P1-E01 steps 13 to 17: summary, bootstrap, shared locations, figure, RESULTS.md, assets.md."""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from . import data as D
from .common import now_utc, read_json, write_json
from .e1 import GATE_TOLERANCE_M, SEEDS, bootstrap_table, load_runs, missing_runs
from .metrics import STAT_NAMES
from .models import ALL_MODELS, BASELINES, SEEDED, TFMS

STAT_LABELS = dict(mean="Mean", median="Median", p75="75th", p95="95th", rmse="RMS")


def _md(df: pd.DataFrame) -> str:
    """A plain markdown table (no dependency on tabulate)."""
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)


def _pm(mean: float, std: float, single: bool) -> str:
    return f"{mean:.3f}" if single else f"{mean:.3f} ± {std:.3f}"


def config_table(summary: pd.DataFrame, config: str) -> pd.DataFrame:
    rows = []
    for model in ALL_MODELS:
        g = summary[(summary["config"] == config) & (summary["model"] == model)]
        if g.empty:
            continue
        single = model not in SEEDED
        row = {"Model": f"`{model}`", "Group": "TFM" if model in TFMS else "baseline", "Runs": len(g)}
        for stat in STAT_NAMES:
            row[f"{STAT_LABELS[stat]} (m)"] = _pm(g[stat].mean(), g[stat].std(ddof=1) if len(g) > 1 else 0.0, single)
        rows.append(row)
    return pd.DataFrame(rows)


def cost_table(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for config in D.ALL_CONFIGS:
        for model in ALL_MODELS:
            g = summary[(summary["config"] == config) & (summary["model"] == model)]
            if g.empty:
                continue
            gpu = g["peak_gpu_mem_mb"].dropna()
            rows.append({
                "Config": config, "Model": f"`{model}`", "Runs": len(g),
                "Fit (s)": f"{g['fit_s'].mean():.2f}", "Predict (s)": f"{g['predict_s'].mean():.2f}",
                "Peak GPU memory (MB)": f"{gpu.mean():.0f}" if len(gpu) else "n/a",
            })
    return pd.DataFrame(rows)


def write_figure(out: Path, summary: pd.DataFrame) -> None:
    fig_dir = out / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    agg = (summary.groupby(["config", "model"], observed=True)["mean"].agg(["mean", "std", "count"]).reset_index()
           .rename(columns={"mean": "mean_error_m", "std": "std_over_seeds_m", "count": "runs"}))
    agg.to_csv(fig_dir / "e1_mean_error.csv", index=False)
    script = Path(__file__).with_name("plot_e1_mean_error.py")
    shutil.copyfile(script, fig_dir / "plot_e1_mean_error.py")
    import runpy
    import sys

    argv, sys.argv = sys.argv, [str(script), str(fig_dir / "e1_mean_error.csv")]
    try:
        runpy.run_path(str(fig_dir / "plot_e1_mean_error.py"), run_name="__main__")
    finally:
        sys.argv = argv


def write_report(out: Path, data_root: str) -> None:
    out = Path(out)
    gate = read_json(out / "logs" / "e0_gate.json")
    e0 = pd.read_csv(out / "metrics" / "e0_check.csv")
    summary = load_runs(out)
    summary.to_csv(out / "metrics" / "e1_summary.csv", index=False)
    missing = missing_runs(out)

    # config/best_params.json and the exact configuration of every run
    best, search_info = {}, {}
    for path in sorted((out / "config" / "best_params").glob("*.json")):
        r = read_json(path)
        best.setdefault(r["config"], {})[r["model"]] = r["best_params"]
        search_info.setdefault(r["config"], {})[r["model"]] = {k: r[k] for k in (
            "best_value", "best_trial", "n_trials", "search_seconds", "settings", "encoding", "threads", "node",
            "code_commit", "started_utc", "finished_utc")}
    write_json(out / "config" / "best_params.json", best)
    write_json(out / "config" / "search_runs.json", search_info)
    runs = {}
    for path in sorted((out / "logs" / "runs").glob("*.json")):
        r = read_json(path)
        runs[r["run_id"]] = {k: r[k] for k in ("config", "model", "seed", "single_run", "params", "encoding", "info",
                                               "notes", "train_rows", "n_features", "test_rows", "device", "threads",
                                               "node", "code_commit", "started_utc", "finished_utc")}
    write_json(out / "config" / "run_configs.json", runs)

    boot = bootstrap_table(out, summary)
    boot.to_csv(out / "metrics" / "e1_bootstrap.csv", index=False)
    shared = pd.DataFrame([D.shared_locations(D.load_config(c, data_root)) for c in D.ALL_CONFIGS])
    shared.to_csv(out / "metrics" / "e1_shared_locations.csv", index=False)
    write_figure(out, summary)

    L: list[str] = []
    add = L.append
    add("# P1-E01 results: pipeline check and full-survey comparison\n")
    add(f"Brief: `briefs/P1-E01.md`, revision 1. Report written {now_utc()}.\n")
    notes = out / "NOTES.md"
    if notes.exists():
        add(notes.read_text().strip() + "\n")

    add("## 1. Pipeline check (Part A, the gate)\n")
    add(f"Dataset commit `{gate.get('dataset_commit')}`. All counts of the brief's data table match "
        "(`metrics/e0_counts.csv`).\n" if gate["counts_ok"] else "**A dataset count differs from the brief.**\n")
    add(f"kNN as in the brief: `{gate.get('knn')}`, both coordinates as targets.\n")
    show = e0[["config", "not_detected", "mean_m", "paper_mean_m", "diff_mean_m", "p50_m", "paper_p50_m", "p75_m",
               "paper_p75_m", "p95_m", "paper_p95_m", "mae_per_coordinate_m", "mean_within_tolerance"]].copy()
    for c in show.columns:
        if c.endswith("_m"):
            show[c] = show[c].map(lambda v: f"{v:.3f}")
    show.columns = ["Config", "Not detected", "Mean", "Paper mean", "Diff", "50th", "Paper 50th", "75th", "Paper 75th",
                    "95th", "Paper 95th", "MAE per coord.", f"Mean within {GATE_TOLERANCE_M} m"]
    add(_md(show) + "\n")
    if gate["gate_passed"]:
        add(f"**The gate passes** with \"not detected\" written as **{', '.join(gate['passed_with'])}**: the mean "
            f"positioning error is within {GATE_TOLERANCE_M} m of the dataset paper in all three configurations. "
            "All values are in metres. Full comparison: `metrics/e0_check.csv`.\n")
    else:
        add("**The gate does not pass.** Part B was not run.\n")

    add("## 2. Full-survey comparison (Part B)\n")
    add(f"{len(summary)} runs: seeds {SEEDS[0]} to {SEEDS[-1]} for the models with randomness, one run for `knn`, "
        "`svr` and `gp`. Entries are mean ± standard deviation over seeds, in metres. "
        "Per-run numbers: `metrics/e1_summary.csv`.\n")
    if missing:
        add(f"**{len(missing)} runs are missing:** " + ", ".join(f"`{m}`" for m in missing) + "\n")
    for config in D.ALL_CONFIGS:
        t = config_table(summary, config)
        if t.empty:
            continue
        spec = D.CONFIGS[config]
        add(f"### {config}\n")
        add(f"{spec['train_rows']:,} training rows, {spec['ref_points']} reference points, {spec['rss_cols']} RSS "
            f"columns, {spec['test_rows']:,} test rows at {spec['test_points']} test points.\n")
        add(_md(t) + "\n")

    add("## 3. Best tabular foundation model against best baseline\n")
    add("Per configuration: the tabular foundation model and the baseline with the lowest mean error averaged over "
        "seeds. The difference uses seed 0 of each, with a 95% bootstrap interval from 10,000 resamples of test "
        "points; a resampled test point brings all 10 of its rows. Negative means the tabular foundation model is "
        "better. Source: `metrics/e1_bootstrap.csv`.\n")
    b = boot.copy()
    bshow = pd.DataFrame() if b.empty else pd.DataFrame({
        "Config": b["config"], "Best TFM": b["tfm"].map(lambda v: f"`{v}`"),
        "Best baseline": b["baseline"].map(lambda v: f"`{v}`"),
        "TFM mean, seed 0 (m)": b["tfm_mean_seed0"].map(lambda v: f"{v:.3f}"),
        "Baseline mean, seed 0 (m)": b["baseline_mean_seed0"].map(lambda v: f"{v:.3f}"),
        "Difference (m)": b["diff_tfm_minus_baseline"].map(lambda v: f"{v:+.3f}"),
        "95% interval (m)": [f"[{lo:+.3f}, {hi:+.3f}]" for lo, hi in zip(b["ci95_low"], b["ci95_high"])],
    })
    add((_md(bshow) if len(bshow) else "(no configuration has both a tabular foundation model and a baseline yet)")
        + "\n")

    add("## 4. Cost\n")
    add("Wall-clock seconds to fit and to predict the test file, and peak GPU memory "
        "(`torch.cuda.max_memory_allocated`), averaged over seeds. Fitting covers both coordinates. Search time of "
        "the tuned baselines is not included here; it is in `config/search_runs.json`.\n")
    add(_md(cost_table(summary)) + "\n")
    st = []
    for config, models in search_info.items():
        for model, r in models.items():
            st.append({"Config": config, "Baseline": f"`{model}`", "Trials": r["n_trials"],
                       "Search (s)": f"{r['search_seconds']:.0f}", "Best CV mean error (m)": f"{r['best_value']:.3f}"})
    if st:
        add("Search time of the tuned baselines (30 trials, 3 folds each):\n")
        add(_md(pd.DataFrame(st)) + "\n")

    add("## 5. Test points that share their location with a reference point\n")
    s2 = shared.rename(columns={"config": "Config", "test_points": "Test points",
                                "shared_with_floor": "Shared (ECoord, NCoord, FloorID)",
                                "shared_ignoring_floor": "Shared (ECoord, NCoord)"})
    add(_md(s2) + "\n")

    tfm_info = []
    for rid, r in runs.items():
        if r["model"] in TFMS and r["seed"] == 0:
            tfm_info.append({"Config": r["config"], "Model": f"`{r['model']}`", "Not detected as": r["encoding"],
                             "Context rows": r["info"].get("context_rows"),
                             "Context capped": r["info"].get("context_capped"),
                             "Weights": Path(str(r["info"].get("model_path") or r["info"].get("checkpoint"))).name})
    if tfm_info:
        add("## 6. Tabular foundation models: weights, context and missing values\n")
        add(_md(pd.DataFrame(tfm_info)) + "\n")

    (out / "RESULTS.md").write_text("\n".join(L).rstrip() + "\n")
