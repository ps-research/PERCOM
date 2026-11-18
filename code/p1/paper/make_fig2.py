"""Fig. 2 of the paper (two columns, three panels), in the IEEE template's type: Times, 8 pt or larger.

(a) Access points switched off after the survey: mean error (m), averaged over the three buildings,
    30 draws; band: lowest to highest draw; shaded: the gap between the -105 and the missing-value
    version of TabPFN v2 and of LightGBM.
(b) Reference points surveyed: mean error relative to tuned kNN on the full survey of the same
    building, averaged over the buildings, 10 draws; large markers where a foundation model reaches 1.0.
(c) Scans per reference point (HCXY and SYL): mean error relative to tuned kNN on the full survey of
    the same building, averaged over the two buildings; band: lowest to highest draw.
(b) and (c) share the scale, so below 1.0 means better than tuned kNN with the whole survey.
One legend serves all three panels (the models keep the colours and markers of every paper figure).

    PYTHONPATH=code python3 code/p1/paper/make_fig2.py --out <overleaf clone>/ASSETS/IMAGES --preview <dir>
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from p1.figs import figstyle as S
from p1.figs.figdata import Results, interp_crossing

MAIN = ["CETC331", "HCXY-All", "SYL-All"]
SCAN_CONFIGS = ["HCXY-All", "SYL-All"]
PT = 16.0  # on the 2x canvas: 8 pt at print size, the template's minimum


def style():
    S.FS.apply(1.0)
    for k in ("tick", "label", "legend", "legend_title", "ref"):
        setattr(S.FS, k, PT)
    S.FS.tag = 22.0
    times = "TeX Gyre Termes"
    plt.rcParams.update({
        "font.family": "serif", "font.serif": [times, "Nimbus Roman"],
        "mathtext.fontset": "custom", "mathtext.rm": times, "mathtext.it": f"{times}:italic",
        "mathtext.bf": f"{times}:bold", "mathtext.sf": times, "mathtext.tt": times, "mathtext.cal": f"{times}:italic",
        "font.size": PT, "axes.labelsize": PT, "xtick.labelsize": PT, "ytick.labelsize": PT,
        "legend.fontsize": PT, "legend.title_fontsize": PT,
    })


def panel_missing(ax, R: Results, log) -> set:
    e3 = R.e3_all_draws()
    e3 = e3[e3["config"].isin(MAIN)]
    per_draw = e3.groupby(["model", "share", "draw"])["mean"].mean().reset_index()  # average of the buildings
    zero = per_draw[per_draw["share"] == 0]
    draws = sorted(per_draw[per_draw["share"] > 0]["draw"].unique())
    per_draw = pd.concat([per_draw[per_draw["share"] > 0]] + [zero.assign(draw=d) for d in draws])
    curve = per_draw.groupby(["model", "share"])["mean"].agg(["mean", "min", "max"]).reset_index()
    get = lambda m: curve[curve["model"] == m].sort_values("share")
    shown = ["tabpfn-nan", "tabpfn-ph", "tabicl", "knn", "lgbm-nan", "lgbm-ph"]
    for a, b in (("tabpfn-nan", "tabpfn-ph"), ("lgbm-nan", "lgbm-ph")):
        ca, cb = get(a), get(b)
        ax.fill_between(ca["share"], ca["mean"].to_numpy(), cb["mean"].to_numpy(), color=S.MODEL[a]["color"],
                        alpha=0.22, lw=0, zorder=2)
    for m in shown:
        c = get(m)
        kw = S.mark_kw(m)
        ax.fill_between(c["share"], c["min"], c["max"], color=kw["color"], alpha=0.08, lw=0, zorder=1)
        ax.plot(c["share"], c["mean"], zorder=4 if m in S.TFMS else 3, **kw)
    xs = sorted(curve["share"].unique())
    ax.set_xticks(xs)
    ax.set_xticklabels([str(x) for x in xs])
    ax.set_xlim(-2, xs[-1] + 2)
    ax.set_ylim(0, curve[curve["model"].isin(shown)]["max"].max() * 1.05)
    ax.set_xlabel("Access points switched off after the survey (%)")
    ax.set_ylabel("Mean error (m)")
    log(f"(a) {len(draws)} draws; at {xs[-1]}%: " + ", ".join(f"{m} {get(m)['mean'].iloc[-1]:.2f}" for m in shown))
    return set(shown)


def knn_full(R: Results) -> pd.Series:
    e1 = R.e1_summary()
    return e1[e1["model"] == "knn"].groupby("config")["mean"].mean()


def panel_refpoints(ax, R: Results, log) -> set:
    e2 = R.e2_summary()
    e2 = e2[e2["config"].isin(MAIN)]
    ref = knn_full(R)
    e2 = e2.assign(rel=e2["mean"] / e2["config"].map(ref))
    per_draw = e2.groupby(["model", "share", "draw"])["rel"].mean().reset_index()
    shares = sorted(per_draw["share"].unique())
    curve = per_draw.groupby(["model", "share"])["rel"].agg(["mean", "min", "max"]).reset_index()
    at_small = curve[curve["share"] == shares[0]].set_index("model")["mean"]
    others = sorted([m for m in S.ORDER if m not in S.TFMS and m != "knn" and m in at_small.index], key=lambda m: at_small[m])[:2]
    shown = list(S.TFMS) + ["knn"] + others
    for m in shown:
        c = curve[curve["model"] == m].sort_values("share")
        kw = S.mark_kw(m)
        ax.fill_between(c["share"], c["min"], c["max"], color=kw["color"], alpha=0.10, lw=0, zorder=2)
        ax.plot(c["share"], c["mean"], zorder=4 if m in S.TFMS else 3, **kw)
        if m in S.TFMS:
            x = interp_crossing(c["share"], c["mean"], 1.0)
            if x is not None:
                h, = ax.plot([x], [1.0], marker=S.MODEL[m]["marker"], ms=17, mfc=kw["mfc"], mec=kw["color"], mew=3.0,
                             ls="none", zorder=6)
                S.halo(h, 5)
    S.ref_line(ax, y=1.0, color=S.INK2, lw=2.2)
    ax.set_xscale("log")
    ax.set_xticks(shares)
    ax.set_xticklabels([str(s) for s in shares])
    ax.minorticks_off()
    ax.set_xlim(shares[0] * 0.85, shares[-1] * 1.15)
    sub = curve[curve["model"].isin(shown)]
    ax.set_ylim(min(0.6, sub["min"].min() * 0.92), sub["max"].max() * 1.04)
    ax.set_xlabel("Reference points surveyed (%)")
    ax.set_ylabel("Error relative to tuned kNN")
    log(f"(b) shown {shown}; at {shares[1]}%: " + ", ".join(f"{m} {curve[(curve.model == m) & (curve.share == shares[1])]['mean'].iloc[0]:.2f}" for m in shown))
    return set(shown)


def panel_scans(ax, R: Results, log) -> set:
    B = R.b_scans()
    B = B[B["config"].isin(SCAN_CONFIGS)]
    ref = knn_full(R)
    B = B.assign(rel=B["mean"] / B["config"].map(ref))
    shown = ["tabpfn-nan", "tabpfn-ph", "tabicl", "knn"]
    per_draw = B.groupby(["model", "scans_per_point", "seed"])["rel"].mean().reset_index()  # average of the two buildings
    curve = per_draw.groupby(["model", "scans_per_point"])["rel"].agg(["mean", "min", "max"]).reset_index()
    for m in shown:
        c = curve[curve["model"] == m].sort_values("scans_per_point")
        kw = S.mark_kw(m)
        if m in S.TFMS:
            ax.fill_between(c["scans_per_point"], c["min"], c["max"], color=kw["color"], alpha=0.10, lw=0, zorder=2)
        ax.plot(c["scans_per_point"], c["mean"], zorder=4 if m in S.TFMS else 3, **kw)
    S.ref_line(ax, y=1.0, color=S.INK2, lw=2.2)
    ks = sorted(curve["scans_per_point"].unique())
    ax.set_xscale("log")
    ax.set_xticks([k for k in ks if k != 26])
    ax.set_xticklabels([str(k) for k in ks if k != 26])
    ax.minorticks_off()
    ax.set_xlim(ks[0] * 0.85, ks[-1] * 1.15)
    sub = curve[curve["model"].isin(shown)]
    ax.set_ylim(min(0.6, sub["min"].min() * 0.92), sub["max"].max() * 1.06)
    ax.set_xlabel("Scans per reference point")
    ax.set_ylabel("Error relative to tuned kNN")
    log(f"(c) at 1 scan: " + ", ".join(f"{m} {curve[(curve.model == m) & (curve.scans_per_point == ks[0])]['mean'].iloc[0]:.2f}" for m in shown))
    return set(shown)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--preview", type=Path)
    args = ap.parse_args()
    style()
    R = Results()
    fig, axes = plt.subplots(1, 3, figsize=(S.TWO_COL_W, 4.7), gridspec_kw=dict(wspace=0.30))
    used = set()
    for ax, fn, tag in zip(axes, (panel_missing, panel_refpoints, panel_scans), "abc"):
        used |= fn(ax, R, print)
        S.tag(ax, tag, x=-0.20, y=1.02)
    order = [m for m in S.ORDER if m in used]
    handles = [S.handle(m) for m in order]
    labels = [S.MODEL[m]["label"] for m in order]
    handles += [Line2D([0], [0], color=S.INK2, ls="--", lw=2.2),
                Patch(facecolor=S.BLUE, alpha=0.22, lw=0)]
    labels += ["tuned kNN, full survey", "$-$105 against NaN"]
    fig.legend(handles, labels, loc="upper center", ncol=5, frameon=True, fancybox=False, edgecolor="#b9b7b0",
               bbox_to_anchor=(0.5, 0.995), handlelength=2.2, columnspacing=1.1, handletextpad=0.5, borderpad=0.45)
    fig.subplots_adjust(top=0.70, bottom=0.20, left=0.065, right=0.99)  # shorter canvas for the page budget [D-068]
    args.out.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out / "fig2_stress.pdf", bbox_inches="tight", pad_inches=0.03)  # no white padding (PI ruling)
    if args.preview:
        args.preview.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.preview / "fig2_stress.png", dpi=S.PNG_DPI, bbox_inches="tight", pad_inches=0.03)
    print(f"wrote {args.out / 'fig2_stress.pdf'}; legend: {labels}")


if __name__ == "__main__":
    main()
