"""P1-E03 report: one CSV per option (A to E) and RESULTS.md.

Reads the merged P1-E03 folder, plus P1-E01 (seeds 0 to 4, best values, predictions)
and P1-E02 (Part B draws 0 to 9).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import data as D
from .common import now_utc, read_json
from .e3x import LEVELS, SCANS, SEEDS_C
from .metrics import STAT_NAMES, positioning_error
from .models import ALL_MODELS, TFMS
from .report_e1 import _md


def _ci(v: pd.Series) -> str:
    v = v.dropna()
    if len(v) < 2:
        return f"{v.mean():.3f}"
    h = 1.96 * v.std(ddof=1) / np.sqrt(len(v))
    return f"{v.mean():.3f} ± {h:.3f}"


def a_table(out: Path) -> pd.DataFrame:
    rows = []
    for p in sorted((out / "logs" / "uncertainty").glob("*.json")):
        r = read_json(p)
        rows.append(dict(config=r["config"], model=r["model"], seed=r["seed"], **r["stats"]))
    return pd.DataFrame(rows)


def b_table(out: Path) -> pd.DataFrame:
    rows = []
    for p in sorted((out / "logs" / "scans").glob("*.json")):
        r = read_json(p)
        rows.append(dict(config=r["config"], scans_per_point=r["scans_per_point"], seed=r["seed"], model=r["model"],
                         context_rows=r["context_rows"], **r["stats"], fit_s=r["cost"]["fit_s"],
                         predict_s=r["cost"]["predict_s"], peak_gpu_mem_mb=r["cost"]["peak_gpu_mem_mb"],
                         ignore_pretraining_limits=bool(r["info"].get("ignore_pretraining_limits", False))))
    return pd.DataFrame(rows)


def c_table(out: Path, e1_out: Path) -> pd.DataFrame:
    rows = []
    for config in D.ALL_CONFIGS:
        for model in TFMS:
            for seed in range(20):
                src = e1_out if seed < 5 else out
                p = src / "logs" / "runs" / f"{config}__{model}__seed{seed}.json"
                if p.exists():
                    r = read_json(p)
                    rows.append(dict(config=config, model=model, seed=seed, source="P1-E01" if seed < 5 else "P1-E03",
                                     **r["stats"], fit_s=r["cost"]["fit_s"], predict_s=r["cost"]["predict_s"],
                                     peak_gpu_mem_mb=r["cost"]["peak_gpu_mem_mb"]))
    return pd.DataFrame(rows)


def d_table(out: Path, e2_out: Path) -> pd.DataFrame:
    rows = []
    for config in D.MAIN_CONFIGS:
        for model in ALL_MODELS:
            for src, folder, label in ((e2_out, "e3", "P1-E02"), (out, "e3more", "P1-E03")):
                p = src / "logs" / folder / f"{config}__{model}.json"
                if p.exists():
                    for s in read_json(p)["per_set"]:
                        rows.append(dict(config=config, model=model, source=label, **s))
    return pd.DataFrame(rows)


def e_table(out: Path, e1_out: Path, data_root: str) -> pd.DataFrame:
    """Mean error per test-row phone and user, averaged over the available seeds."""
    rows = []
    for config in ("HCXY-All", "SYL-All"):
        meta = pd.read_csv(Path(data_root) / D.CONFIGS[config]["test"], usecols=["PhoneID", "UserID"])
        for model in ALL_MODELS:
            for seed in range(20):
                src = e1_out if seed < 5 else out
                f = src / "metrics" / "predictions" / f"{config}__{model}__seed{seed}.csv.gz"
                if not f.exists():
                    continue
                p = pd.read_csv(f)
                for group in ("PhoneID", "UserID"):
                    g = pd.DataFrame({"id": meta[group].to_numpy()[p["row"].to_numpy()], "err": p["error_m"]})
                    for gid, gg in g.groupby("id"):
                        rows.append(dict(config=config, model=model, seed=seed, group=group, id=int(gid),
                                         n_rows=len(gg), mean_error_m=float(gg["err"].mean())))
    return pd.DataFrame(rows)


def write_configs(out: Path) -> None:
    """config/run_configs.json: the exact configuration of every run of this brief."""
    from .common import write_json

    runs = {}
    for kind in ("uncertainty", "scans", "runs", "e3more"):
        for p in sorted((out / "logs" / kind).glob("*.json")) if (out / "logs" / kind).exists() else []:
            r = read_json(p)
            runs[f"{kind}/{p.stem}"] = {k: r.get(k) for k in (
                "config", "model", "seed", "scans_per_point", "context_rows", "params", "encoding", "info", "draws",
                "quantiles", "node", "code_commit", "finished_utc") if k in r}
    write_json(out / "config" / "run_configs.json", runs)


def write_report(out: Path, e1_out: Path, e2_out: Path, data_root: str) -> None:
    out = Path(out)
    (out / "metrics").mkdir(parents=True, exist_ok=True)
    write_configs(out)
    A, B, C, Dd, E = a_table(out), b_table(out), c_table(out, e1_out), d_table(out, e2_out), e_table(out, e1_out, data_root)
    for name, df in (("a_uncertainty", A), ("b_scans", B), ("c_seeds", C), ("d_e3_more", Dd), ("e_phone_user", E)):
        df.to_csv(out / "metrics" / f"{name}.csv", index=False)

    L: list[str] = []
    add = L.append
    add("# P1-E03 results: uncertainty, scans per point, more seeds, more missing-AP draws, phone and user\n")
    add(f"Brief: `briefs/P1-E03.md` on this branch (approved by the PI in chat on 2026-11-15, written by the compute "
        f"node; not on `main`). Report written {now_utc()}.\n")
    notes = out / "NOTES.md"
    if notes.exists():
        add(notes.read_text().strip() + "\n")

    add("## A. Uncertainty\n")
    if len(A):
        add("Mean over seeds (5 for the foundation models, 1 for `gp`). Coverage is the share of test rows whose true "
            "coordinate lies in the central interval; the nominal value is the interval level. For both coordinates at "
            "once, independent coordinates would give the square of the level (0.64 at 80%). Spearman: correlation "
            "between the predicted spread and the positioning error. Source: `metrics/a_uncertainty.csv`.\n")
        g = A.groupby(["config", "model"]).mean(numeric_only=True).reset_index()
        show = pd.DataFrame({
            "Config": g["config"], "Model": g["model"].map(lambda v: f"`{v}`"), "Mean (m)": g["mean"].map("{:.3f}".format),
            **{f"Cov. {lvl}% (E/N)": [f"{e:.2f}/{n:.2f}" for e, n in zip(g[f"cover{lvl}_E"], g[f"cover{lvl}_N"])]
               for lvl in LEVELS},
            "Cov. 80% both": g["cover80_both"].map("{:.2f}".format),
            "Width 80% (m)": g["width80_m"].map("{:.2f}".format),
            "Spearman": g["spearman_spread80_error"].map("{:.2f}".format),
            "Err. most / least confident 10% (m)": [f"{a:.2f} / {b:.2f}" for a, b in
                                                    zip(g["error_most_confident_10pct_m"], g["error_least_confident_10pct_m"])],
        })
        add(_md(show) + "\n")

    add("## B. Scans per reference point\n")
    if len(B):
        add("Mean error (m) averaged over the 5 scan draws (`knn` and `gp`: seed-0 draw only). `knn` uses its P1-E01 "
            "best values. Source: `metrics/b_scans.csv`.\n")
        for config in B["config"].unique():
            g = B[B["config"] == config]
            t = g.groupby(["model", "scans_per_point"])["mean"].mean().unstack("scans_per_point")
            t = t.reindex([m for m in ALL_MODELS if m in t.index])
            t.columns = [f"k={k}" for k in t.columns]
            t.insert(0, "Model", [f"`{m}`" for m in t.index])
            add(f"### {config}\n")
            add(_md(t.round(3).reset_index(drop=True)) + "\n")
            c = g.groupby(["model", "scans_per_point"])[["context_rows", "fit_s", "predict_s", "peak_gpu_mem_mb"]].mean()
            c = c.reset_index()
            c = c[c["model"].isin(TFMS)]
            add("Cost of the foundation models by context size:\n")
            c = pd.DataFrame({"Model": c["model"].map(lambda v: f"`{v}`"), "k": c["scans_per_point"].astype(int),
                              "Context rows": c["context_rows"].map(lambda v: f"{v:,.0f}"),
                              "Fit (s)": c["fit_s"].map("{:.2f}".format), "Predict (s)": c["predict_s"].map("{:.2f}".format),
                              "Peak GPU (MB)": c["peak_gpu_mem_mb"].map("{:,.0f}".format)})
            add(_md(c) + "\n")
        lim = B[B["ignore_pretraining_limits"]]
        if len(lim):
            add(f"{len(lim)} TabPFN runs (HCXY-All, k = 30, 11,370 rows) used `ignore_pretraining_limits=True`.\n")

    add("## C. Twenty seeds of the foundation models\n")
    if len(C):
        add("Mean error (m) with a 95% interval over seeds (normal approximation); seeds 0 to 4 are the P1-E01 runs. "
            "Source: `metrics/c_seeds.csv`.\n")
        rows = []
        for (config, model), g in C.groupby(["config", "model"], sort=False):
            g5 = g[g["seed"] < 5]
            rows.append({"Config": config, "Model": f"`{model}`", "Seeds": len(g), "Mean, 5 seeds": _ci(g5["mean"]),
                         "Mean, all seeds": _ci(g["mean"]), "95th, all seeds": _ci(g["p95"]),
                         "Range of means": f"{g['mean'].min():.3f} to {g['mean'].max():.3f}"})
        add(_md(pd.DataFrame(rows)) + "\n")

    add("## D. Part B with 30 draws\n")
    if len(Dd):
        add("Mean error (m) by share of access points switched off: mean ± std over draws 0 to 29 (draws 0 to 9 from "
            "P1-E02). Source: `metrics/d_e3_more.csv`.\n")
        for config in D.MAIN_CONFIGS:
            g = Dd[Dd["config"] == config]
            if g.empty:
                continue
            t = g.groupby(["model", "share"])["mean"].agg(lambda v: f"{v.mean():.2f} ± {v.std(ddof=1):.2f}" if len(v) > 1 else f"{v.mean():.2f}")
            t = t.unstack("share").reindex([m for m in ALL_MODELS if m in set(g["model"])])
            t.columns = [f"{s}%" for s in t.columns]
            t.insert(0, "Model", [f"`{m}`" for m in t.index])
            add(f"### {config}\n")
            add(_md(t.reset_index(drop=True)) + "\n")

    add("## E. Error by phone and by user\n")
    if len(E):
        add("Mean error (m) of the test rows of each phone and user, averaged over seeds (20 for the foundation "
            "models, 5 or 1 for the baselines). Every phone and user of the test files also appears in the training "
            "files, so this is not a cross-device test. Source: `metrics/e_phone_user.csv`.\n")
        for config in E["config"].unique():
            for group in ("PhoneID", "UserID"):
                g = E[(E["config"] == config) & (E["group"] == group)]
                t = g.groupby(["model", "id"])["mean_error_m"].mean().unstack("id")
                t = t.reindex([m for m in ALL_MODELS if m in t.index])
                n = g.groupby("id")["n_rows"].first()
                t.columns = [f"{group[:-2].lower()} {i} (n={n[i]})" for i in t.columns]
                t.insert(0, "Model", [f"`{m}`" for m in t.index])
                add(f"### {config}, by {group[:-2].lower()}\n")
                add(_md(t.round(2).reset_index(drop=True)) + "\n")
    (out / "RESULTS.md").write_text("\n".join(L).rstrip() + "\n")
