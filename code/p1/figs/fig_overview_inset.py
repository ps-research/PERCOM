"""Inset of the overview figure (Fig. 1): mean error as access points go missing after the survey.

Reads the 30 draws behind Fig. 2 (results/P1-E03/metrics/d_e3_more.csv, all-MAC sheets of the
three buildings). Each curve is the mean over draws in each building, then the mean over the three
buildings. The grey band is the range of the six tuned baselines (seven variants: LightGBM is run
with NaN and with -105). Type follows the IEEE template: Times (TeX Gyre Termes), 8 pt at print size.

Writes, at print size, for the designer who builds Fig. 1 around it:
  inset_plot.pdf / .svg / .png   axes, curves and band, no legend
  inset_legend.pdf / .svg / .png the legend block
  inset_values.csv               every plotted value, with the per-building means

    python3 code/p1/figs/fig_overview_inset.py --out paper1/figures/fig1_overview
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "results" / "P1-E03" / "metrics" / "d_e3_more.csv"
BUILDINGS = ["CETC331", "HCXY-All", "SYL-All"]
TFM = {"tabpfn-nan": ("#2a78d6", "o", "TabPFN v2, missing as NaN"),
       "tabicl": ("#eb6834", "D", "TabICLv2, missing as NaN")}
KNN = ("#1baf7a", "s", "kNN, tuned")
BASELINES = ["knn", "rf", "lgbm-nan", "lgbm-ph", "svr", "mlp", "gp"]
INK, INK2, GUIDE, GRID = "#1d1d1b", "#52514e", "#9a9893", "#e6e5e1"
PT = 8.0  # template: "Use 8 point Times New Roman for Figure labels"


def style():
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["TeX Gyre Termes", "Nimbus Roman"],
        "font.size": PT, "axes.labelsize": PT, "xtick.labelsize": PT, "ytick.labelsize": PT, "legend.fontsize": PT,
        "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
        "pdf.fonttype": 42, "svg.fonttype": "none", "savefig.facecolor": "white", "figure.facecolor": "white",
    })


def curves() -> tuple[pd.DataFrame, pd.DataFrame]:
    d = pd.read_csv(SOURCE)
    d = d[d["config"].isin(BUILDINGS)]
    draws = d.groupby(["config", "model", "share"])["draw"].nunique()
    at_zero = set(draws[draws.index.get_level_values("share") == 0])
    elsewhere = set(draws[draws.index.get_level_values("share") > 0])
    if at_zero != {1} or elsewhere != {30}:  # nothing is switched off at 0%, so it has one draw
        raise SystemExit(f"expected 1 draw at 0% and 30 elsewhere, found {sorted(at_zero)} and {sorted(elsewhere)}")
    per_building = d.groupby(["config", "model", "share"])["mean"].mean().unstack("config")
    avg = per_building.mean(axis=1).rename("mean_over_buildings")
    return per_building, avg.unstack("model")


def save(fig, out: Path, stem: str):
    for ext in ("pdf", "svg"):
        fig.savefig(out / f"{stem}.{ext}")
    fig.savefig(out / f"{stem}.png", dpi=600)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    style()
    per_building, avg = curves()
    shares = avg.index.to_numpy()
    lo, hi = avg[BASELINES].min(axis=1), avg[BASELINES].max(axis=1)

    fig = plt.figure(figsize=(1.62, 1.20))
    ax = fig.add_axes([0.22, 0.27, 0.74, 0.69])
    ax.fill_between(shares, lo, hi, color=GUIDE, alpha=0.28, lw=0, zorder=1)
    ax.plot(shares, lo, color=GUIDE, lw=0.6, zorder=2)
    ax.plot(shares, hi, color=GUIDE, lw=0.6, zorder=2)
    ax.plot(shares, avg["knn"], color=KNN[0], ls="--", lw=1.0, marker=KNN[1], ms=2.6, zorder=3)
    for model, (color, marker, _) in TFM.items():
        ax.plot(shares, avg[model], color=color, lw=1.4, marker=marker, ms=3.0, mec="white", mew=0.4, zorder=4)
    ax.set_xlim(-2, 62)
    ax.set_xticks([0, 20, 40, 60])
    ax.set_ylim(0, 16)
    ax.set_yticks([0, 5, 10, 15])
    ax.set_xlabel("Access points missing (%)", labelpad=1.5)
    ax.set_ylabel("Mean error (m)", labelpad=1.5)
    save(fig, args.out, "inset_plot")

    handles = [Line2D([], [], color=c, lw=1.4, marker=m, ms=3.0, mec="white", mew=0.4) for c, m, _ in TFM.values()]
    handles += [Line2D([], [], color=KNN[0], ls="--", lw=1.0, marker=KNN[1], ms=2.6),
                Patch(facecolor=GUIDE, alpha=0.28, edgecolor=GUIDE, lw=0.6)]
    labels = [lab for _, _, lab in TFM.values()] + [KNN[2], "Six tuned baselines, range"]
    fig = plt.figure(figsize=(1.80, 0.78))
    fig.legend(handles, labels, loc="center", frameon=True, fancybox=False, edgecolor="#b9b7b0",
               handlelength=2.2, borderpad=0.45, labelspacing=0.3, handletextpad=0.5)
    save(fig, args.out, "inset_legend")

    rows = []
    for share in shares:
        for model in list(TFM) + BASELINES:
            row = {"share": int(share), "model": model, "mean_over_buildings": round(float(avg.loc[share, model]), 4)}
            row.update({b: round(float(per_building.loc[(model, share), b]), 4) for b in BUILDINGS})
            rows.append(row)
    pd.DataFrame(rows).to_csv(args.out / "inset_values.csv", index=False)

    top = shares.max()
    print(f"source: {SOURCE.relative_to(ROOT)} (30 draws per point)")
    for model in TFM:
        print(f"  {model:11s} mean over buildings at 0%: {avg.loc[0, model]:.2f} m, at {top}%: {avg.loc[top, model]:.2f} m")
    print(f"  kNN          at 0%: {avg.loc[0, 'knn']:.2f} m, at {top}%: {avg.loc[top, 'knn']:.2f} m")
    print(f"  baselines band at {top}%: {lo.loc[top]:.2f} to {hi.loc[top]:.2f} m")


if __name__ == "__main__":
    main()
