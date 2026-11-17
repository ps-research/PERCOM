"""Write the paper's Table I (full survey) from the merged results, in the IEEE template's style.

Builds on the results package's generator (code/p1/figs/tables.py) and changes, for the paper:
  * a zero before every decimal point (template: "Use a zero before decimal points");
  * bold group heads for the three groups of rows (PI ruling: group heads are bold);
  * a row for Locaris with the numbers its paper reports, marked with a lettered table footnote
    (template: "Use letters for table footnotes") and never counted when the best value is bolded;
  * a caption that only says what the reader is looking at.

    PYTHONPATH=code python3 code/p1/paper/make_tables.py --out <overleaf clone>/ASSETS/TABLES
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd

from p1.figs import figstyle as S
from p1.figs.figdata import Results

ROOT = Path(__file__).resolve().parents[3]
MAIN = ["CETC331", "HCXY-All", "SYL-All"]
TFM = ["tabpfn-nan", "tabpfn-ph", "tabicl"]

# Published numbers, quoted as reported (full-text source only, CONTEXT.md).
# P001:E007, Locaris WiP Table III: "AVERAGE STATISTICS OF REGRESSION METHODS ACROSS CETC331, SYL, AND HCXY".
LOCARIS = {"pid": "P001", "evidence": "E007", "avg": 2.840, "p95": 10.280}


def fmt(v: float, nd: int) -> str:
    return f"{v:.{nd}f}"


def sd_tex(s: float) -> str:
    if pd.isna(s) or s <= 0:
        return ""
    return f"\\textsubscript{{$\\pm${s:.2f}}}" if s < 1 else f"\\textsubscript{{$\\pm${s:.1f}}}"


def check_source():
    with (ROOT / "litreview/p1-tabular-localization/sources/index.csv").open(newline="") as f:
        level = {r["pid"]: r["access_level"] for r in csv.DictReader(f)}[LOCARIS["pid"]]
    if level != "FULLTEXT":
        raise SystemExit(f"Locaris numbers need a full-text source, {LOCARIS['pid']} is {level}")
    with (ROOT / "litreview/p1-tabular-localization/evidence.csv").open(newline="") as f:
        row = {r["eid"]: r for r in csv.DictReader(f)}[LOCARIS["evidence"]]
    for v in ("2.840", "10.280"):
        if v not in row["statement"]:
            raise SystemExit(f"evidence {LOCARIS['evidence']} does not state {v}")


def table1(R: Results) -> str:
    check_source()
    e1 = R.e1_summary()
    g = e1.groupby(["model", "config"]).agg(mean=("mean", "mean"), sd=("mean", "std"), n=("seed", "count"),
                                            p95=("p95", "mean"))
    models = [m for m in S.ORDER if m in g.index.get_level_values(0)]
    mean = g["mean"].unstack("config").reindex(models)[MAIN]
    sd = g["sd"].unstack("config").reindex(models)[MAIN]
    avg = mean.mean(axis=1)
    p95 = g["p95"].unstack("config").reindex(models)[MAIN].mean(axis=1)
    n_seeds = int(g.loc[(models[0], MAIN[0]), "n"])
    best = {c: mean[c].idxmin() for c in MAIN}
    best_avg, best_p95 = avg.idxmin(), p95.idxmin()

    lines = [
        r"\begin{table}[t]",
        # IEEEtran sets table captions in small caps; units go in \upshape (IEEEtran HOWTO, table captions)
        r"\caption{Mean positioning error ({\upshape m}) with the full survey. Subscripts: standard deviation over "
        r"\numSeedsMain{} seeds. Avg.: mean of the three buildings. 95th: 95th-percentile error averaged over the "
        r"buildings. Best in bold.}",
        r"\label{tab:full}",
        r"\centering",
        r"\setlength{\tabcolsep}{3.4pt}",
        r"\footnotesize",
        r"\begin{tabular}{@{}lccccc@{}}",
        r"\toprule",
        r"Model & CETC331 & HCXY & SYL & Avg. & 95th \\",
        r"\midrule",
        r"\multicolumn{6}{@{}l}{\textbf{Tabular foundation models, no training}} \\",
    ]
    for m in models:
        if m == models[len(TFM)]:
            lines.append(r"\multicolumn{6}{@{}l}{\textbf{Tuned baselines}} \\")
        cells = []
        for c in MAIN:
            txt = fmt(mean.loc[m, c], 2) + sd_tex(sd.loc[m, c])
            cells.append(f"\\textbf{{{txt}}}" if best[c] == m else txt)
        a, q = fmt(avg[m], 2), fmt(p95[m], 1)
        cells += [f"\\textbf{{{a}}}" if m == best_avg else a, f"\\textbf{{{q}}}" if m == best_p95 else q]
        lines.append(S.MODEL[m]["label"] + " & " + " & ".join(cells) + r" \\")
    lines += [
        r"\multicolumn{6}{@{}l}{\textbf{As reported, different protocol}} \\",
        rf"Locaris$^{{\mathrm{{a}}}}$~\cite{{bhatia2026locaris}} & -- & -- & -- & {fmt(LOCARIS['avg'], 2)} & {fmt(LOCARIS['p95'], 1)} \\",
        r"\bottomrule",
        # P004 (long version): "appending valid RSSI values together with vendor identifiers, scene descriptions, and building labels"
        r"\multicolumn{6}{@{}p{0.97\columnwidth}@{}}{\scriptsize $^{\mathrm{a}}$Average over the three buildings as "
        r"reported in~\cite{bhatia2026locaris}, from a fine-tuned language model whose input also includes vendor "
        r"identifiers, scene descriptions and building labels as text~\cite{bhatia2025locaris_arxiv}.} \\",
        r"\end{tabular}",
        r"\end{table}",
    ]
    assert n_seeds == 5, n_seeds
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    text = "% Generated by code/p1/paper/make_tables.py from merged results. Do not edit by hand.\n" + table1(Results())
    (args.out / "table1_full_survey.tex").write_text(text)
    print(f"wrote {args.out / 'table1_full_survey.tex'}")


if __name__ == "__main__":
    main()
