"""Table I drawn as a figure: full-survey comparison of the ten models in the five configurations.

    python -m p1.figs.fig_table1 [--out results/figures]

Each cell: mean positioning error (mean over seeds) on top; standard deviation over seeds and the
95th percentile below; a bar whose length is the cell's error relative to the column's largest; the
best cell of each column in bold. Right-hand columns: mean rank over the five configurations, and the
cost (fit plus predict seconds, median over configurations; search seconds of the tuned baselines).
Bottom row: best foundation model minus best baseline, seed 0 of each, with its 95% bootstrap interval.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Rectangle

from . import figstyle as S
from .figdata import Results

CONFIGS = ["CETC331", "HCXY-All", "HCXY-AP", "SYL-All", "SYL-AP"]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(Path(__file__).resolve().parents[3] / "results" / "figures"))
    p.add_argument("--e1"), p.add_argument("--e2"), p.add_argument("--e3")
    a = p.parse_args(argv)
    S.FS.apply(1.0)
    R = Results(a.e1, a.e2, a.e3)
    e1 = R.e1_summary()
    boot = R.e1_bootstrap().set_index("config") if len(R.e1_bootstrap()) else pd.DataFrame()
    search = R.e1_search()
    agg = e1.groupby(["config", "model"]).agg(mean=("mean", "mean"), sd=("mean", "std"), p95=("p95", "mean"),
                                              n=("seed", "count"), fit=("fit_s", "mean"), pred=("predict_s", "mean"))
    configs = [c for c in CONFIGS if c in set(e1["config"])]
    models = [m for m in S.ORDER if m in set(e1["model"])]
    rank = agg["mean"].unstack("config").reindex(columns=configs).rank(axis=0).mean(axis=1)
    cost = (agg["fit"] + agg["pred"]).unstack("config").reindex(columns=configs).median(axis=1)
    tune = search.groupby("model")["search_seconds"].median() if len(search) else pd.Series(dtype=float)

    import matplotlib.pyplot as plt

    widths = [3.3] + [1.85] * len(configs) + [1.15, 1.6, 1.45]
    xs = np.concatenate([[0], np.cumsum(widths)])
    n_rows = len(models) + 1
    row_h, head_h = 1.0, 1.25
    fig, ax = plt.subplots(figsize=(S.TWO_COL_W, 0.56 * (n_rows + 1.3)))
    ax.set_xlim(0, xs[-1])
    ax.set_ylim(-(n_rows * row_h) - 0.05, head_h)
    ax.axis("off")
    heads = ["Model"] + [S.CONFIG_LABEL[c].replace(" (", "\n(") for c in configs] + ["Mean\nrank", "Fit + pred.\n(s, median)",
                                                                                    "Tuning\n(s, upper bd.)"]
    for i, h in enumerate(heads):
        ax.text(xs[i] + (0.15 if i == 0 else widths[i] / 2), head_h / 2, h, ha="left" if i == 0 else "center",
                va="center", fontsize=S.FS.legend, fontweight="bold", color=S.INK)
    ax.plot([0, xs[-1]], [0, 0], color=S.INK, lw=1.6)
    col_max = {c: agg.loc[(c, slice(None)), "mean"].max() for c in configs}
    best = {c: agg.loc[(c, slice(None)), "mean"].droplevel(0).idxmin() for c in configs}
    best_rank, best_cost = rank.idxmin(), cost.idxmin()
    for r, m in enumerate(models):
        y0 = -(r + 1) * row_h
        if r % 2 == 0:
            ax.add_patch(Rectangle((0, y0), xs[-1], row_h, color="#f6f5f2", lw=0, zorder=0))
        st = S.MODEL[m]
        ax.plot([0.32], [y0 + row_h / 2], marker=st["marker"], ms=15, mfc=st["color"] if st["filled"] else S.PAPER,
                mec=st["color"], mew=2.4, ls="none")
        ax.text(0.62, y0 + row_h / 2, st["label"], va="center", fontsize=S.FS.legend + 0.5, color=S.INK,
                fontweight="bold" if m in S.TFMS else "normal")
        for j, c in enumerate(configs):
            x0 = xs[j + 1]
            if (c, m) not in agg.index:
                ax.text(x0 + widths[j + 1] / 2, y0 + row_h / 2, "n/a", ha="center", va="center", fontsize=S.FS.legend,
                        color=S.GUIDE)
                continue
            v = agg.loc[(c, m)]
            frac = v["mean"] / col_max[c]
            ax.add_patch(Rectangle((x0 + 0.14, y0 + 0.07), (widths[j + 1] - 0.28) * frac, 0.11, color=S.MODEL[m]["color"],
                                   alpha=0.6, lw=0))
            ax.text(x0 + widths[j + 1] / 2, y0 + 0.71, f"{v['mean']:.2f}", ha="center", va="center",
                    fontsize=S.FS.legend + 1.5, color=S.INK, fontweight="bold" if best[c] == m else "normal")
            sd = f"±{v['sd']:.2f}" if v["n"] > 1 else "1 run"
            ax.text(x0 + widths[j + 1] / 2, y0 + 0.38, f"{sd} · 95th {v['p95']:.1f}", ha="center", va="center",
                    fontsize=S.FS.legend - 2.5, color=S.INK2)
        x0 = xs[len(configs) + 1]
        ax.text(x0 + widths[len(configs) + 1] / 2, y0 + row_h / 2, f"{rank[m]:.1f}", ha="center", va="center",
                fontsize=S.FS.legend + 1, color=S.INK, fontweight="bold" if m == best_rank else "normal")
        x0 = xs[len(configs) + 2]
        ax.text(x0 + widths[len(configs) + 2] / 2, y0 + row_h / 2, f"{cost[m]:.2f}", ha="center", va="center",
                fontsize=S.FS.legend + 1, color=S.INK, fontweight="bold" if m == best_cost else "normal")
        x0 = xs[len(configs) + 3]
        tv = "none" if m in S.TFMS or m == "gp" else (f"{tune[m]:.0f}" if m in tune.index else "n/a")
        ax.text(x0 + widths[len(configs) + 3] / 2, y0 + row_h / 2, tv, ha="center", va="center",
                fontsize=S.FS.legend + 1, color=S.INK, style="italic" if tv == "none" else "normal")
    # bottom row: bootstrap difference
    y0 = -n_rows * row_h
    ax.plot([0, xs[-1]], [y0 + row_h, y0 + row_h], color=S.INK, lw=1.2)
    ax.text(0.15, y0 + row_h / 2, "Best TFM $-$ best baseline\n(seed 0, 95% bootstrap CI)", va="center",
            fontsize=S.FS.legend - 0.5, color=S.INK)
    for j, c in enumerate(configs):
        if c not in boot.index:
            continue
        b = boot.loc[c]
        x0 = xs[j + 1]
        sig = b["ci95_high"] < 0 or b["ci95_low"] > 0
        ax.text(x0 + widths[j + 1] / 2, y0 + 0.66, f"{b['diff_tfm_minus_baseline']:+.2f}", ha="center", va="center",
                fontsize=S.FS.legend + 1.5, color=S.INK, fontweight="bold" if sig else "normal")
        ax.text(x0 + widths[j + 1] / 2, y0 + 0.36, f"[{b['ci95_low']:+.2f}, {b['ci95_high']:+.2f}]", ha="center",
                va="center", fontsize=S.FS.legend - 2.5, color=S.INK2)
    ax.plot([0, xs[-1]], [y0, y0], color=S.INK, lw=1.6)
    S.save(fig, Path(a.out), "table1_full_survey")
    for c in configs:
        b = boot.loc[c] if c in boot.index else None
        print(f"  {c}: best {best[c]} {agg.loc[(c, best[c]), 'mean']:.3f} m"
              + (f"; {b['tfm']} - {b['baseline']} = {b['diff_tfm_minus_baseline']:+.3f} [{b['ci95_low']:+.3f}, {b['ci95_high']:+.3f}]" if b is not None else ""))
    print(f"  best mean rank: {best_rank} ({rank[best_rank]:.1f}); cheapest: {best_cost} ({cost[best_cost]:.2f} s)")


if __name__ == "__main__":
    main()
