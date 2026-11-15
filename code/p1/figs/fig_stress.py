"""Fig. 2 (two columns): (a) fewer reference points; (b) access points switched off after the survey.

    python -m p1.figs.fig_stress [--out results/figures]

(a) Mean error relative to tuned kNN on the full survey of the same building, averaged over the
    three buildings; band from the lowest to the highest draw; markers where each foundation model
    reaches the kNN level. (b) Mean error in metres averaged over the three buildings against the share
    of MAC columns switched off; the gap between the NaN and the -105 version of the same model is shaded.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from . import figstyle as S
from .figdata import Results, interp_crossing

MAX_SERIES = 6  # FIGURE_TASTE II, B3


def panel_a(ax, R: Results, log=print) -> dict:
    e2 = R.e2_summary()
    configs = sorted(e2["config"].unique())
    knn100 = e2[(e2["model"] == "knn") & (e2["share"] == 100)].groupby("config")["mean"].mean()
    e2 = e2.assign(rel=e2["mean"] / e2["config"].map(knn100))
    per_draw = e2.groupby(["model", "share", "draw"])["rel"].mean().reset_index()  # average of the buildings
    shares = sorted(per_draw["share"].unique())
    curve = per_draw.groupby(["model", "share"])["rel"].agg(["mean", "min", "max"]).reset_index()
    smallest = curve[curve["share"] == shares[0]].set_index("model")["mean"]
    baselines = [m for m in S.ORDER if m not in S.TFMS and m != "knn" and m in smallest.index]
    best_other = sorted(baselines, key=lambda m: smallest[m])[: MAX_SERIES - 4]
    shown = list(S.TFMS) + ["knn"] + best_other
    dropped = [m for m in S.ORDER if m not in shown]
    log(f"  (a) shown {shown}; not drawn (logged, FIGURE_TASTE II A6): {dropped}")
    cr = R.e2_crossing()
    out = {}
    for m in shown:
        c = curve[curve["model"] == m].sort_values("share")
        kw = S.mark_kw(m)
        ax.fill_between(c["share"], c["min"], c["max"], color=kw["color"], alpha=0.11, lw=0, zorder=2)
        ax.plot(c["share"], c["mean"], zorder=4 if m in S.TFMS else 3, **kw)
        out[m] = dict(at5=float(c["mean"].iloc[0]), at100=float(c["mean"].iloc[-1]))
        if m in S.TFMS:
            x = interp_crossing(c["share"], c["mean"], 1.0)
            out[m]["cross"] = x
            if x is not None:
                h, = ax.plot([x], [1.0], marker=S.MODEL[m]["marker"], ms=19, mfc=kw["mfc"], mec=kw["color"], mew=3.2,
                             ls="none", zorder=6)
                S.halo(h, 6)
            per = cr[cr["model"] == m].set_index("config")["crossing_share_pct"] if len(cr) else pd.Series(dtype=object)
            out[m]["per_config"] = {k: v for k, v in per.items()}
    S.ref_line(ax, y=1.0, label=None, color=S.INK2, lw=2.4)
    ax.set_xscale("log")
    ax.set_xticks(shares)
    ax.set_xticklabels([f"{s}%" for s in shares])
    ax.minorticks_off()
    ax.set_xlabel("Share of reference points surveyed")
    ax.set_ylabel("Mean error / tuned kNN on the full survey")
    ax.set_xlim(shares[0] * 0.85, shares[-1] * 1.15)
    sub = curve[curve["model"].isin(shown)]
    ax.set_ylim(min(0.6, sub["min"].min() * 0.92), sub["max"].max() * 1.5)  # never clip a band; head room for legends

    def pct(v):
        try:
            return f"{float(v):.0f}%"
        except (TypeError, ValueError):
            return "never"

    def num(v, suffix="×"):
        return "n/a" if v is None or not np.isfinite(v) else f"{v:.2f}{suffix}"

    def fmt(m):
        o = out[m]
        if m in S.TFMS:
            x = o.get("cross")
            per = o.get("per_config", {})
            head = f"{x:.0f}% (mean)" if x is not None else "never (mean)"
            per_s = " · ".join(f"{S.CONFIG_SHORT[c]} {pct(v)}" for c, v in per.items() if c in configs)
            return f"{S.MODEL[m]['label']}: {head}" + (f"\n{per_s}" if per_s else "")
        return f"{S.SHORT[m]}: {num(o['at5'])} → {num(o['at100'])}"

    from matplotlib.lines import Line2D

    l1 = S.legend_box(ax, [S.handle(m) for m in S.TFMS], [fmt(m) for m in S.TFMS],
                      title="Survey share to match tuned kNN", loc="upper right")
    ax.add_artist(l1)
    rest = ["knn"] + best_other
    S.legend_box(ax, [S.handle(m) for m in rest] + [Line2D([0], [0], color=S.INK2, ls="--", lw=2.4)],
                 [fmt(m) for m in rest] + ["1.0: kNN, full survey"],
                 title="Re-tuned, 5% → 100%", loc="upper right", bbox_to_anchor=(1.0, 0.66))
    return out


def panel_b(ax, R: Results, log=print) -> dict:
    e3 = R.e3_all_draws()
    n_draws = e3[e3["share"] > 0]["draw"].nunique()
    per_draw = e3.groupby(["model", "share", "draw"])["mean"].mean().reset_index()
    zero = per_draw[per_draw["share"] == 0]
    if len(zero):  # the 0% share is one run per building; repeat it for every draw so the band starts at a point
        draws = sorted(per_draw[per_draw["share"] > 0]["draw"].unique())
        per_draw = pd.concat([per_draw[per_draw["share"] > 0]] + [zero.assign(draw=d) for d in draws])
    curve = per_draw.groupby(["model", "share"])["mean"].agg(["mean", "min", "max"]).reset_index()
    shown = ["tabpfn-nan", "tabpfn-ph", "tabicl", "knn", "lgbm-nan", "lgbm-ph"]
    log(f"  (b) shown {shown}; not drawn: {[m for m in S.ORDER if m not in shown]}; draws per share: {n_draws}")
    out = {}
    get = lambda m: curve[curve["model"] == m].sort_values("share")
    for a, b in (("tabpfn-nan", "tabpfn-ph"), ("lgbm-nan", "lgbm-ph")):
        ca, cb = get(a), get(b)
        ax.fill_between(ca["share"], ca["mean"].to_numpy(), cb["mean"].to_numpy(), color=S.MODEL[a]["color"],
                        alpha=0.20, lw=0, zorder=2)
    for m in shown:
        c = get(m)
        kw = S.mark_kw(m)
        ax.fill_between(c["share"], c["min"], c["max"], color=kw["color"], alpha=0.07, lw=0, zorder=1)
        ax.plot(c["share"], c["mean"], zorder=4 if m in S.TFMS else 3, **kw)
        out[m] = dict(at0=float(c["mean"].iloc[0]), at60=float(c["mean"].iloc[-1]))
    ax.set_xlabel("Share of access points switched off after the survey")
    ax.set_ylabel("Mean error, mean of 3 buildings (m)")
    xs = sorted(curve["share"].unique())
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{x}%" for x in xs])
    ax.set_xlim(-2, xs[-1] + 2)
    top = curve[curve["model"].isin(shown)]["max"].max()
    ax.set_ylim(0, top * 2.0)  # head room for the legend, above every band

    def fmt(m):
        o = out[m]
        return f"{S.SHORT[m]}: {o['at0']:.2f}→{o['at60']:.2f}"

    from matplotlib.patches import Patch

    gap = [Patch(facecolor=S.BLUE, alpha=0.20, lw=0), Patch(facecolor=S.MAGENTA, alpha=0.20, lw=0)]
    sgn = lambda v: f"{v:+.2f}".replace("-", "\u2212")
    gap_lbl = [f"shaded, TabPFN $-$105 minus NaN: {sgn(out['tabpfn-ph']['at60'] - out['tabpfn-nan']['at60'])} at 60%",
               f"shaded, LightGBM $-$105 minus NaN: {sgn(out['lgbm-ph']['at60'] - out['lgbm-nan']['at60'])} at 60%"]
    S.legend_box(ax, [S.handle(m) for m in shown] + gap, [fmt(m) for m in shown] + gap_lbl,
                 title=f"Mean error (m), 0%→60% off, {n_draws} draws", loc="upper left")
    return out


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(Path(__file__).resolve().parents[3] / "results" / "figures"))
    p.add_argument("--e1"), p.add_argument("--e2"), p.add_argument("--e3")
    a = p.parse_args(argv)
    S.FS.apply(1.0)
    R = Results(a.e1, a.e2, a.e3)
    import matplotlib.pyplot as plt

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(S.TWO_COL_W, 7.4), gridspec_kw=dict(wspace=0.26))
    oa = panel_a(axa, R)
    ob = panel_b(axb, R)
    S.tag(axa, "a")
    S.tag(axb, "b")
    S.save(fig, Path(a.out), "fig2_stress", panels={"a": axa, "b": axb})
    print("  headline (a):", {m: (round(v["cross"], 1) if v.get("cross") else None) for m, v in oa.items() if m in S.TFMS})
    print("  headline (b):", {m: (round(v["at0"], 2), round(v["at60"], 2)) for m, v in ob.items()})


if __name__ == "__main__":
    main()
