"""Cost against accuracy on the full survey (one column): what a fix costs and what it buys.

    python -m p1.figs.fig_cost [--out results/figures]

x: seconds to fit and predict one test file (log axis). y: mean error relative to tuned kNN in the
same configuration (log axis). Small marks: every model in every configuration (mean over seeds);
large haloed marks: each model's median over the five configurations. Tuned baselines also carry an
open mark joined by a dotted line at fit + predict + median search time: the training step a
foundation model does not have. Search times are upper bounds (other jobs shared the nodes).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from . import figstyle as S
from .figdata import Results


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(Path(__file__).resolve().parents[3] / "results" / "figures"))
    p.add_argument("--e1"), p.add_argument("--e2"), p.add_argument("--e3")
    a = p.parse_args(argv)
    S.FS.apply(1.0)
    R = Results(a.e1, a.e2, a.e3)
    e1 = R.e1_summary()
    search = R.e1_search()
    g = e1.groupby(["config", "model"]).agg(mean=("mean", "mean"), fit=("fit_s", "mean"), pred=("predict_s", "mean"))
    knn = g.xs("knn", level="model")["mean"]
    g["rel"] = g["mean"] / g.index.get_level_values("config").map(knn).to_numpy()
    g["cost"] = g["fit"] + g["pred"]
    tune = search.groupby("model")["search_seconds"].median() if len(search) else {}
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(S.ONE_COL_W, 8.4))
    rows = {}
    lo_x, hi_x, hi_y = np.inf, 0.0, 0.0
    for m in [m for m in S.ORDER if m in set(e1["model"])]:
        d = g.xs(m, level="model").dropna(subset=["rel"])
        if d.empty:
            continue
        kw = S.mark_kw(m)
        ax.plot(d["cost"], d["rel"], ls="none", marker=kw["marker"], ms=8, mfc=kw["mfc"], mec=kw["mec"], mew=1.6,
                alpha=0.55, zorder=3)
        x, y = float(d["cost"].median()), float(d["rel"].median())
        t = float(tune[m]) if hasattr(tune, "index") and m in tune.index else None
        if t:
            ax.plot([x, x + t], [y, y], color=kw["color"], ls=":", lw=2.4, zorder=2)
            ax.plot([x + t], [y], ls="none", marker=kw["marker"], ms=13, mfc=S.PAPER, mec=kw["color"], mew=2.2, zorder=4)
        h, = ax.plot([x], [y], ls="none", marker=kw["marker"], ms=18, mfc=kw["mfc"], mec=kw["mec"], mew=2.6, zorder=5)
        S.halo(h, 5)
        rows[m] = (x, y, t)
        lo_x, hi_x = min(lo_x, d["cost"].min()), max(hi_x, d["cost"].max(), x + (t or 0))
        hi_y = max(hi_y, d["rel"].max())
    S.ref_line(ax, y=1.0, color=S.GUIDE, lw=1.8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo_x / 2.5, hi_x * 2.5)
    ax.set_ylim(0.75, hi_y * 9.0)  # head room above every point for the legend box
    ticks = [t for t in (0.8, 1, 1.5, 2, 3, 4, 6) if t <= hi_y * 1.2]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{t:g}" for t in ticks])
    ax.minorticks_off()
    ax.set_xlabel("Fit + predict one test file (s)")
    ax.set_ylabel("Mean error / tuned kNN (log)")

    def fmt(m):
        x, y, t = rows[m]
        return f"{S.SHORT[m]}: {y:.2f}×, {x:.1f} s" + (f" (+{t:.0f})" if t else "")

    order = [m for m in rows if m in S.TFMS] + [m for m in rows if m not in S.TFMS]
    S.legend_box(ax, [S.handle(m, 12) for m in order], [fmt(m) for m in order],
                 title="Median of 5 configs (+ search s, upper bound)", loc="upper right")
    S.save(fig, Path(a.out), "fig_cost_accuracy")
    for m, (x, y, t) in rows.items():
        print(f"  {m}: rel {y:.3f}, cost {x:.2f} s" + (f", tuning {t:.0f} s" if t else ""))


if __name__ == "__main__":
    main()
