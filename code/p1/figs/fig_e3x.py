"""P1-E03 figures (two columns each).

    python -m p1.figs.fig_e3x [--out results/figures]

fig_uncertainty: (a) empirical coverage of central predictive intervals against their nominal level,
    averaged over the two coordinates, seeds and the five configurations (band: range over configurations);
    (b) mean error of the test rows in each decile of predicted spread, relative to the model's mean error.
fig_scans: (a) mean error against scans per reference point, relative to the same model with all 30 scans,
    averaged over HCXY-All and SYL-All; (b) fit plus predict seconds against context rows, marker area
    proportional to peak GPU memory.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from . import figstyle as S
from .figdata import Results

UNC = ["tabpfn-nan", "tabpfn-ph", "tabicl", "gp"]
LEVELS = [50, 80, 90, 95]


def fig_uncertainty(R: Results, out: Path):
    import matplotlib.pyplot as plt

    A = R.a_uncertainty()
    if A.empty:
        print("  fig_uncertainty: no data yet")
        return
    for lv in LEVELS:
        A[f"cov{lv}"] = (A[f"cover{lv}_E"] + A[f"cover{lv}_N"]) / 2
    per_cfg = A.groupby(["model", "config"])[[f"cov{lv}" for lv in LEVELS] + ["width80_m", "spearman_spread80_error",
                                                                           "error_most_confident_10pct_m",
                                                                           "error_least_confident_10pct_m"]].mean()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(S.TWO_COL_W, 6.4), gridspec_kw=dict(wspace=0.24))
    ax.plot([45, 100], [45, 100], color=S.INK2, ls="--", lw=2.2, zorder=1)
    rows_a = {}
    models = [m for m in UNC if m in per_cfg.index.get_level_values(0)]
    for m in models:
        d = per_cfg.xs(m, level="model")
        mean = [100 * d[f"cov{lv}"].mean() for lv in LEVELS]
        lo = [100 * d[f"cov{lv}"].min() for lv in LEVELS]
        hi = [100 * d[f"cov{lv}"].max() for lv in LEVELS]
        kw = S.mark_kw(m, size=12)
        ax.fill_between(LEVELS, lo, hi, color=kw["color"], alpha=0.12, lw=0, zorder=2)
        ax.plot(LEVELS, mean, zorder=4, **kw)
        rows_a[m] = (mean[1], d["width80_m"].mean())
    ax.set_xlim(45, 100)
    ax.set_ylim(min(30, min(v[0] for v in rows_a.values()) - 5), 100)
    ax.set_xticks(LEVELS)
    ax.set_xlabel("Nominal level of the central interval (%)")
    ax.set_ylabel("Test rows inside the interval (%)")
    from matplotlib.lines import Line2D

    S.legend_box(ax, [S.handle(m) for m in models] + [Line2D([0], [0], color=S.INK2, ls="--", lw=2.2)],
                 [f"{S.MODEL[m]['label']}: 80% interval holds {rows_a[m][0]:.0f}% (width {rows_a[m][1]:.1f} m)" for m in models]
                 + ["calibrated: holds its nominal share"], title="Coverage, mean of 5 configs", loc="upper left")
    S.tag(ax, "a")

    # (b) error by decile of predicted spread
    pdir = R.e3 / "metrics" / "predictions" / "uncertainty"
    rows_b = {}
    for m in models:
        curves = []
        for f in sorted(pdir.glob(f"*__{m}__seed*.csv.gz")):
            p = pd.read_csv(f)
            spread = ((p["q0.9_E"] - p["q0.1_E"]) + (p["q0.9_N"] - p["q0.1_N"])) / 2
            dec = pd.qcut(spread.rank(method="first"), 10, labels=False)
            curves.append(p.groupby(dec)["error_m"].mean().to_numpy() / p["error_m"].mean())
        if not curves:
            continue
        c = np.vstack(curves)
        x = np.arange(1, 11)
        kw = S.mark_kw(m, size=11)
        bx.fill_between(x, c.min(axis=0), c.max(axis=0), color=kw["color"], alpha=0.10, lw=0, zorder=2)
        bx.plot(x, c.mean(axis=0), zorder=4, **kw)
        d = per_cfg.xs(m, level="model")
        rows_b[m] = (d["spearman_spread80_error"].mean(), c.mean(axis=0)[0], c.mean(axis=0)[-1])
    S.ref_line(bx, y=1.0, color=S.INK2, lw=2.0)
    bx.set_xticks(range(1, 11))
    bx.set_xlabel("Decile of predicted spread (1 = most confident)")
    bx.set_ylabel("Mean error of the decile / overall mean")
    bm = [m for m in models if m in rows_b]
    S.legend_box(bx, [S.handle(m) for m in bm],
                 [f"{S.MODEL[m]['label']}: Spearman {rows_b[m][0]:.2f}; decile 1 {rows_b[m][1]:.2f}×, decile 10 {rows_b[m][2]:.2f}×"
                  for m in bm], title="Does the spread flag bad fixes?", loc="upper left")
    S.tag(bx, "b")
    S.save(fig, out, "fig_uncertainty", panels={"a": ax, "b": bx})
    print("  uncertainty:", {m: f"80% holds {v[0]:.1f}%" for m, v in rows_a.items()},
          {m: f"rho {v[0]:.2f}" for m, v in rows_b.items()})


def fig_scans(R: Results, out: Path):
    import matplotlib.pyplot as plt

    B = R.b_scans()
    if B.empty:
        print("  fig_scans: no data yet")
        return
    models = [m for m in ["tabpfn-nan", "tabpfn-ph", "tabicl", "knn", "gp"] if m in set(B["model"])]
    g = B.groupby(["config", "model", "scans_per_point"])["mean"].mean()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(S.TWO_COL_W, 6.4), gridspec_kw=dict(wspace=0.24))
    rows = {}
    for m in models:
        rel = []
        for c in sorted(B["config"].unique()):
            s = g.xs((c, m), level=("config", "model"))
            if 30 in s.index:
                rel.append(s / s.loc[30])
        if not rel:
            continue
        r = pd.concat(rel, axis=1)
        ks = r.index.to_numpy()
        kw = S.mark_kw(m, size=11)
        ax.fill_between(ks, r.min(axis=1), r.max(axis=1), color=kw["color"], alpha=0.10, lw=0, zorder=2)
        ax.plot(ks, r.mean(axis=1), zorder=4 if m in S.TFMS else 3, **kw)
        rows[m] = (float(r.mean(axis=1).loc[ks[0]]), float(r.mean(axis=1).loc[10]) if 10 in r.index else np.nan)
    S.ref_line(ax, y=1.0, color=S.INK2, lw=2.0)
    S.ref_line(ax, x=26, color=S.GUIDE, ls=":", lw=2.0, label="HCXY cap (26)")
    ax.set_xscale("log")
    ks = sorted(B["scans_per_point"].unique())
    ax.set_xticks(ks)
    ax.set_xticklabels([str(k) for k in ks])
    ax.minorticks_off()
    ax.set_xlabel("Scans per reference point in the context")
    ax.set_ylabel("Mean error / same model with 30 scans")
    cap = B[(B["config"] == "HCXY-All") & B["model"].str.startswith("tabpfn")].groupby(["model", "scans_per_point"])["mean"].mean()
    S.legend_box(ax, [S.handle(m) for m in rows],
                 [f"{S.MODEL[m]['label']}: {rows[m][0]:.2f}× at 1 scan, {rows[m][1]:.2f}× at 10" for m in rows],
                 title="Mean of HCXY and SYL (band: the two)", loc="upper right")
    S.tag(ax, "a")
    # (b) cost against context rows
    cost = B[B["model"].isin(S.TFMS)].groupby(["model", "config", "context_rows"]).agg(
        t=("fit_s", "mean"), p=("predict_s", "mean"), mem=("peak_gpu_mem_mb", "mean")).reset_index()
    cost["total"] = cost["t"] + cost["p"]
    rows_b = {}
    for m in [m for m in S.TFMS if m in set(cost["model"])]:
        d = cost[cost["model"] == m].sort_values("context_rows")
        kw = S.mark_kw(m)
        for c, dc in d.groupby("config"):
            bx.plot(dc["context_rows"], dc["total"], color=kw["color"], ls=kw["ls"], lw=2.0, zorder=3)
            bx.scatter(dc["context_rows"], dc["total"], s=dc["mem"] / 25, marker=S.CONFIG_MARKER[c],
                       facecolors=kw["mfc"], edgecolors=kw["color"], linewidths=2.0, zorder=4)
        top = d.sort_values("context_rows").iloc[-1]
        rows_b[m] = (int(top["context_rows"]), float(top["total"]), float(top["mem"]) / 1024)
    S.ref_line(bx, x=10_000, color=S.GUIDE, ls=":", lw=2.0, label="10k rows (TabPFN v2 limit)")
    bx.set_xscale("log")
    bx.set_yscale("log")
    bx.set_xlabel("Context rows (reference-point scans)")
    bx.set_ylabel("Fit + predict, both coordinates (s)")
    hs = [S.handle(m) for m in rows_b]
    ls = [f"{S.MODEL[m]['label']}: {rows_b[m][1]:.1f} s, {rows_b[m][2]:.1f} GB at {rows_b[m][0]:,} rows" for m in rows_b]
    from matplotlib.lines import Line2D

    for c in sorted(cost["config"].unique()):
        hs.append(Line2D([0], [0], ls="none", marker=S.CONFIG_MARKER[c], ms=12, mfc="white", mec=S.INK2, mew=2))
        ls.append(f"{S.CONFIG_LABEL[c]} (marker area: peak GPU memory)")
    S.legend_box(bx, hs, ls, title="Cost of the context", loc="upper left")
    S.tag(bx, "b")
    S.save(fig, out, "fig_scans_cost", panels={"a": ax, "b": bx})
    print("  scans:", {m: (round(a, 2), round(b, 2)) for m, (a, b) in rows.items()}, "| cost at largest context:", rows_b)
    if len(cap):
        print("  HCXY TabPFN k=26 vs k=30:", {m: (round(cap.loc[(m, 26)], 3), round(cap.loc[(m, 30)], 3))
                                             for m in cap.index.get_level_values(0).unique()
                                             if (m, 26) in cap.index and (m, 30) in cap.index})


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(Path(__file__).resolve().parents[3] / "results" / "figures"))
    p.add_argument("--e1"), p.add_argument("--e2"), p.add_argument("--e3")
    a = p.parse_args(argv)
    S.FS.apply(1.0)
    R = Results(a.e1, a.e2, a.e3)
    fig_uncertainty(R, Path(a.out))
    fig_scans(R, Path(a.out))


if __name__ == "__main__":
    main()
