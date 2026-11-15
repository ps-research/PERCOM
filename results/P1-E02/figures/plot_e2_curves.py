"""Draft figures of P1-E02: mean error against a share, one line per model, band over draws.

    python plot_e2_curves.py e2_reference_points.csv "Share of reference points kept (%)" log
    python plot_e2_curves.py e3_missing_aps.csv "Share of access points switched off (%)" linear

The CSV has columns config, share, draw, model, mean (mean positioning error in metres
of one run). One panel per configuration plus one panel averaged over the three: in
that panel each draw's value is the average over configurations of that draw's mean
error. Lines are the mean over draws; bands go from the lowest to the highest draw.
Writes <csv stem>.pdf and .png next to the CSV.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

MODELS = ["tabpfn-nan", "tabpfn-ph", "tabicl", "knn", "rf", "lgbm-ph", "lgbm-nan", "svr", "mlp", "gp"]
TFMS = {"tabpfn-nan", "tabpfn-ph", "tabicl"}
COLORS = {"tabpfn-nan": "#1f4e9c", "tabpfn-ph": "#4f8fe0", "tabicl": "#17becf", "knn": "#d62728", "rf": "#2ca02c",
          "lgbm-ph": "#ff7f0e", "lgbm-nan": "#bcbd22", "svr": "#8c564b", "mlp": "#9467bd", "gp": "#7f7f7f"}
CONFIGS = ["CETC331", "HCXY-All", "SYL-All"]


def main(csv_path: str, xlabel: str, xscale: str) -> None:
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    configs = [c for c in CONFIGS if c in set(df["config"])]
    avg = (df.groupby(["share", "draw", "model"])["mean"].mean().reset_index().assign(config="Average of the three"))
    n_cfg = df.groupby(["share", "draw", "model"])["config"].nunique()
    if (n_cfg < len(configs)).any():
        avg = avg.iloc[0:0]
    panels = configs + (["Average of the three"] if len(avg) else [])
    data = pd.concat([df, avg], ignore_index=True)
    fig, axes = plt.subplots(1, len(panels), figsize=(3.6 * len(panels), 3.3), squeeze=False)
    for ax, panel in zip(axes[0], panels):
        g = data[data["config"] == panel]
        for model in [m for m in MODELS if m in set(g["model"])]:
            gm = g[g["model"] == model].groupby("share")["mean"]
            x = gm.mean().index.to_numpy()
            ax.plot(x, gm.mean().to_numpy(), color=COLORS[model], lw=1.8 if model in TFMS else 1.0,
                    ls="-" if model in TFMS else "--", marker="o", ms=2.5, label=model)
            ax.fill_between(x, gm.min().to_numpy(), gm.max().to_numpy(), color=COLORS[model], alpha=0.12, lw=0)
        ax.set_xscale(xscale)
        if xscale == "log":
            ticks = sorted(set(g["share"]))
            ax.set_xticks(ticks)
            ax.set_xticklabels([str(t) for t in ticks])
            ax.minorticks_off()
        ax.set_title(panel, fontsize=9)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.grid(linewidth=0.3)
        ax.tick_params(labelsize=7)
    axes[0][0].set_ylabel("Mean positioning error (m)", fontsize=8)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=10, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    for ext in ("pdf", "png"):
        fig.savefig(csv_path.with_suffix(f".{ext}"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "Share (%)", sys.argv[3] if len(sys.argv) > 3 else "linear")
