"""Cost against accuracy on the full survey (one column): what a fix costs and what it buys.

    python -m p1.figs.fig_cost [--out results/figures]

x: seconds to fit and predict the test file (median over the five configurations, log axis).
y: mean error relative to tuned kNN in the same configuration (median over configurations);
   whiskers span the five configurations.
Tuned baselines also carry a thin arrow to the right: their median Optuna search time
(30 trials, 3 folds) added, the training step a foundation model does not have.
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

    fig, ax = plt.subplots(figsize=(S.ONE_COL_W, 6.4))
    rows = {}
    xmin, xmax, ymin, ymax = np.inf, 0.0, np.inf, 0.0
    for m in [m for m in S.ORDER if m in set(e1["model"])]:
        d = g.xs(m, level="model").dropna(subset=["rel"])
        if d.empty:
            continue
        x, y = d["cost"].median(), d["rel"].median()
        kw = S.mark_kw(m, size=17)
        ax.plot([x, x], [d["rel"].min(), d["rel"].max()], color=kw["color"], lw=2.2, alpha=0.6, zorder=2)
        ax.plot([d["cost"].min(), d["cost"].max()], [y, y], color=kw["color"], lw=2.2, alpha=0.6, zorder=2)
        if m in tune:  # with tuning: an open marker at fit + predict + median search time, joined by a dotted line
            xt = x + tune[m]
            ax.plot([x, xt], [y, y], color=kw["color"], ls=":", lw=2.4, zorder=2)
            ht, = ax.plot([xt], [y], ls="none", marker=kw["marker"], ms=13, mfc=S.PAPER, mec=kw["color"], mew=2.2, zorder=4)
            xmax = max(xmax, xt)
        xmax = max(xmax, d["cost"].max())
        xmin = min(xmin, d["cost"].min())
        ymin, ymax = min(ymin, d["rel"].min()), max(ymax, d["rel"].max())
        h, = ax.plot([x], [y], ls="none", marker=kw["marker"], ms=17, mfc=kw["mfc"], mec=kw["mec"], mew=2.6, zorder=5)
        S.halo(h, 5)
        rows[m] = (x, y, tune.get(m) if hasattr(tune, "get") else None)
    S.ref_line(ax, y=1.0, color=S.GUIDE, lw=1.6)
    ax.set_xscale("log")
    ax.set_xlim(xmin / 2.0, xmax * 2.0)
    pad = 0.08 * (ymax - ymin)
    ax.set_ylim(ymin - 3.8 * pad, ymax + 3.4 * pad)  # room above and below the data for the two legend boxes
    ax.set_xlabel("Fit + predict one test file (s); open marker: + baseline tuning")
    ax.set_ylabel("Mean error / tuned kNN")

    def fmt(m):
        x, y, t = rows[m]
        extra = f", +{t:.0f} s tuning" if t else (", no tuning" if m in S.TFMS or m == "gp" else "")
        return f"{S.MODEL[m]['label']}: {y:.2f}× in {x:.1f} s{extra}"

    tf = [m for m in rows if m in S.TFMS]
    bl = [m for m in rows if m not in S.TFMS]
    l1 = S.legend_box(ax, [S.handle(m, 13) for m in tf], [fmt(m) for m in tf], title="Foundation models (median of 5 configs)",
                      loc="upper left")
    ax.add_artist(l1)
    S.legend_box(ax, [S.handle(m, 13) for m in bl], [fmt(m) for m in bl], title="Tuned baselines", loc="lower right")
    S.save(fig, Path(a.out), "fig_cost_accuracy")
    for m, (x, y, t) in rows.items():
        print(f"  {m}: rel {y:.3f}, cost {x:.2f} s" + (f", tuning {t:.0f} s" if t else ""))


if __name__ == "__main__":
    main()
