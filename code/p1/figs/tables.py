"""LaTeX tables (booktabs) for paper 1, generated from the result files (FIGURE_TASTE II, Part V).

    python -m p1.figs.tables [--out results/figures]

table1_full_survey.tex: one column; mean error (m) on the full survey, mean ± sd over seeds, for the
    three main buildings, their average, the average 95th percentile and the fit + predict time.
table_setup.tex: one column; the pipeline check against the dataset paper, and what the foundation
    models cost on the largest survey.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

from . import figstyle as S
from .figdata import Results

MAIN = ["CETC331", "HCXY-All", "SYL-All"]
TEX_LABEL = {m: S.MODEL[m]["label"].replace("$-$", "$-$") for m in S.ORDER}


def _best(series: pd.Series):
    return series.idxmin() if series.notna().any() else None


def table1(R: Results) -> str:
    e1 = R.e1_summary()
    g = e1.groupby(["model", "config"]).agg(mean=("mean", "mean"), sd=("mean", "std"), n=("seed", "count"),
                                            p95=("p95", "mean"), t=("fit_s", "mean"), tp=("predict_s", "mean"))
    models = [m for m in S.ORDER if m in g.index.get_level_values(0)]
    mean = g["mean"].unstack("config").reindex(models)[MAIN]
    sd = g["sd"].unstack("config").reindex(models)[MAIN]
    avg = mean.mean(axis=1)
    p95 = g["p95"].unstack("config").reindex(models)[MAIN].mean(axis=1)
    cost = (g["t"] + g["tp"]).unstack("config").reindex(models)[MAIN].median(axis=1)
    best = {c: _best(mean[c]) for c in MAIN}
    best_avg, best_p95 = _best(avg), _best(p95)
    lines = [r"\begin{table}[t]", r"\centering", r"\caption{Mean positioning error (m) with the full survey as "
             r"training data or context; mean with $\pm$sd over 5 seeds as subscript (one run for kNN, SVR, GP). Best per column in bold.}",
             r"\label{tab:full}", r"\setlength{\tabcolsep}{3pt}", r"\footnotesize",
             r"\begin{tabular}{@{}lcccccr@{}}", r"\toprule",
             r"Model & CETC & HCXY & SYL & Avg. & 95th & Time (s) \\", r"\midrule"]
    for i, m in enumerate(models):
        if i == 3:
            lines.append(r"\midrule")
        cells = []
        for c in MAIN:
            v, s = mean.loc[m, c], sd.loc[m, c]
            txt = f"{v:.2f}" + (f"\\textsubscript{{$\\pm$.{round(s * 100):02d}}}" if pd.notna(s) and s > 0 and s < 1 else
                                (f"\\textsubscript{{$\\pm${s:.1f}}}" if pd.notna(s) and s >= 1 else ""))
            cells.append(f"\\textbf{{{txt}}}" if best[c] == m else txt)
        a = f"{avg[m]:.2f}"
        q = f"{p95[m]:.1f}"
        cells += [f"\\textbf{{{a}}}" if m == best_avg else a, f"\\textbf{{{q}}}" if m == best_p95 else q, f"{cost[m]:.1f}"]
        lines.append(TEX_LABEL[m] + " & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines) + "\n"


def table_setup(R: Results) -> str:
    e0 = R.e0_check()
    ph = e0[e0["not_detected"].str.startswith("placeholder")].set_index("config")
    e1 = R.e1_summary()
    tfm = e1[e1["model"].isin(S.TFMS) & (e1["config"] == "HCXY-All")].groupby("model").agg(
        fit=("fit_s", "mean"), pred=("predict_s", "mean"), mem=("peak_gpu_mem_mb", "mean"))
    lines = [r"\begin{table}[t]", r"\centering",
             r"\caption{Pipeline check: untuned kNN ($k{=}5$) against the dataset paper, and the cost of the "
             r"foundation models on HCXY (11{,}370 training rows; TabPFN context capped at 9{,}854).}",
             r"\label{tab:setup}", r"\setlength{\tabcolsep}{3.5pt}", r"\footnotesize",
             r"\begin{tabular}{@{}lrrr@{}}", r"\toprule",
             r"Check & CETC & HCXY & SYL \\", r"\midrule"]
    for key, lbl in (("mean", "Mean, ours/paper (m)"), ("p95", "95th, ours/paper (m)")):
        cells = [f"{ph.loc[c, key + '_m']:.3f}/{ph.loc[c, 'paper_' + key + '_m']:.3f}" for c in MAIN]
        lines.append(lbl + " & " + " & ".join(cells) + r" \\")
    lines += [r"\midrule", r"Model (HCXY) & Fit (s) & Predict (s) & GPU (GB) \\", r"\midrule"]
    for m in [m for m in S.TFMS if m in tfm.index]:
        r = tfm.loc[m]
        lines.append(f"{TEX_LABEL[m]} & {r['fit']:.1f} & {r['pred']:.1f} & {r['mem'] / 1024:.1f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(Path(__file__).resolve().parents[3] / "results" / "figures"))
    p.add_argument("--e1"), p.add_argument("--e2"), p.add_argument("--e3")
    a = p.parse_args(argv)
    R = Results(a.e1, a.e2, a.e3)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("table1_full_survey.tex", table1), ("table_setup.tex", table_setup)):
        path = out / name
        path.unlink(missing_ok=True)
        tex = fn(R)
        if re.search(r"\\\\%", tex):  # FIGURE_TASTE II, E5
            raise RuntimeError(f"{name}: escaped percent sign would comment out the rest of the line")
        if "—" in tex:
            raise RuntimeError(f"{name}: em dash")
        path.write_text(tex)
        assert path.exists()
        print(f"  wrote {name} ({tex.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
