"""Check every table and figure in the real IEEE two-column template (FIGURE_TASTE II, D2 and D4).

    python -m p1.figs.fit_check --figs results/figures --cls <dir with IEEEtran.cls> --build <dir>

Builds a conference-mode IEEEtran document that places each figure at its intended width
(two-column figures with figure*, the others at column width) and inputs each LaTeX table.
Deletes the old PDF first, asserts the new one exists, prints the measured text and column
widths and every overfull box. Honesty boundary: fonts are the TeX Live defaults of this machine.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path

TWO_COL = ["fig2_stress", "table1_full_survey", "fig_uncertainty", "fig_scans_cost"]
ONE_COL = ["fig_cost_accuracy"]
TABLES = ["table1_full_survey.tex", "table_setup.tex"]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--figs", required=True)
    p.add_argument("--cls", required=True)
    p.add_argument("--build", required=True)
    a = p.parse_args(argv)
    figs, build = Path(a.figs).resolve(), Path(a.build).resolve()
    build.mkdir(parents=True, exist_ok=True)
    body = [r"\documentclass[conference]{IEEEtran}", r"\usepackage{graphicx,booktabs,amsmath}",
            r"\begin{document}", r"\title{Fit check}", r"\maketitle",
            r"\typeout{TEXTWIDTH=\the\textwidth}", r"\typeout{COLUMNWIDTH=\the\columnwidth}"]
    for t in TABLES:
        if (figs / t).exists():
            body.append(r"\input{" + str(figs / t) + "}")
    for f in TWO_COL:
        if (figs / f"{f}.pdf").exists():
            body += [r"\begin{figure*}[t]", r"\centering", r"\includegraphics[width=\textwidth]{" + str(figs / f) + ".pdf}",
                     r"\caption{" + f.replace("_", " ") + "}", r"\end{figure*}"]
    for f in ONE_COL:
        if (figs / f"{f}.pdf").exists():
            body += [r"\begin{figure}[t]", r"\centering", r"\includegraphics[width=\columnwidth]{" + str(figs / f) + ".pdf}",
                     r"\caption{" + f.replace("_", " ") + "}", r"\end{figure}"]
    body += [r"\section{Text}", "Filler text. " * 200, r"\end{document}"]
    tex = build / "fitcheck.tex"
    tex.write_text("\n".join(body))
    pdf = build / "fitcheck.pdf"
    pdf.unlink(missing_ok=True)
    env = dict(os.environ, TEXINPUTS=f"{Path(a.cls).resolve()}:")
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name], cwd=build, env=env,
                       capture_output=True, text=True)
    log = (build / "fitcheck.log").read_text(errors="replace")
    if not pdf.exists():
        print("BUILD FAILED:", [l for l in log.splitlines() if l.startswith("!")][:5])
        raise SystemExit(1)
    tw = re.search(r"TEXTWIDTH=([\d.]+pt)", log).group(1)
    cw = re.search(r"COLUMNWIDTH=([\d.]+pt)", log).group(1)
    over = re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)[^\n]*\n?[^\n]*", log)
    print(f"  BUILD OK: {pdf.name} ({pdf.stat().st_size // 1024} KB); textwidth {tw}, columnwidth {cw}")
    print(f"  overfull boxes: {len(over)}" + (f" (widths {over})" if over else ""))


if __name__ == "__main__":
    main()
