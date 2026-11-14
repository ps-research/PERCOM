"""Bar chart of mean positioning error per model and configuration (P1-E01).

    python plot_e1_mean_error.py e1_mean_error.csv

Reads the CSV next to it (config, model, mean_error_m, std_over_seeds_m, runs)
and writes e1_mean_error.png and e1_mean_error.pdf in the same folder.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MODELS = ["tabpfn-nan", "tabpfn-ph", "tabicl", "knn", "rf", "lgbm-ph", "lgbm-nan", "svr", "mlp", "gp"]
TFMS = {"tabpfn-nan", "tabpfn-ph", "tabicl"}
CONFIGS = ["CETC331", "HCXY-All", "HCXY-AP", "SYL-All", "SYL-AP"]


def main(csv_path: str) -> None:
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    configs = [c for c in CONFIGS if c in set(df["config"])]
    fig, axes = plt.subplots(1, len(configs), figsize=(3.1 * len(configs), 3.4), sharey=False)
    axes = np.atleast_1d(axes)
    for ax, config in zip(axes, configs):
        g = df[df["config"] == config].set_index("model").reindex([m for m in MODELS if m in set(df["model"])])
        g = g.dropna(subset=["mean_error_m"])
        colors = ["#1f77b4" if m in TFMS else "#b0b0b0" for m in g.index]
        ax.bar(range(len(g)), g["mean_error_m"], yerr=g["std_over_seeds_m"].fillna(0.0), color=colors, capsize=2)
        ax.set_xticks(range(len(g)))
        ax.set_xticklabels(g.index, rotation=60, ha="right", fontsize=8)
        ax.set_title(config, fontsize=10)
        ax.set_ylim(0, None)
        ax.grid(axis="y", linewidth=0.3)
    axes[0].set_ylabel("Mean positioning error (m)")
    fig.suptitle("Full survey: mean error per model (blue: tabular foundation models; bars: std over seeds)",
                 fontsize=9)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(csv_path.with_suffix(f".{ext}"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).with_name("e1_mean_error.csv")))
