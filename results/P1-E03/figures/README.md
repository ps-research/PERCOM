# Figures and tables for paper 1

Every file here is generated from the result files of `P1-E01`, `P1-E02` and `P1-E03` by the scripts in `code/p1/figs/` (one shared style module, `figstyle.py`); no number is typed by hand. Regenerate from the repository root with:

```
PYTHONPATH=code python -m p1.figs.fig_stress   --out results/P1-E03/figures   # Fig. 2: survey effort and missing access points
PYTHONPATH=code python -m p1.figs.fig_table1   --out results/P1-E03/figures   # Table I drawn as a figure (five configurations)
PYTHONPATH=code python -m p1.figs.fig_cost     --out results/P1-E03/figures   # cost against accuracy
PYTHONPATH=code python -m p1.figs.fig_e3x      --out results/P1-E03/figures   # uncertainty; scans per point and context cost
PYTHONPATH=code python -m p1.figs.tables       --out results/P1-E03/figures   # LaTeX: table1_full_survey.tex, table_setup.tex
PYTHONPATH=code python -m p1.figs.fit_check    --figs results/P1-E03/figures --cls <dir with IEEEtran.cls> --build <tmp>
```

| File | What it is | Data |
|---|---|---|
| `fig2_stress.{pdf,png}` (+ `panels/fig2_stress{a,b}`) | Fig. 2, two columns: (a) error relative to tuned kNN against share of reference points surveyed; (b) error against share of access points switched off (30 draws) | P1-E02 `e2_summary.csv`, `e2_crossing.csv`; P1-E03 `d_e3_more.csv` |
| `table1_full_survey.{pdf,png}` | Table I drawn as a figure: ten models, five configurations, rank, cost, bootstrap row | P1-E01 `e1_summary.csv`, `e1_bootstrap.csv`, `config/search_runs.json` |
| `table1_full_survey.tex`, `table_setup.tex` | The same data as one-column booktabs tables; `typeset_tables.png` shows them in the IEEE template | P1-E01 `e1_summary.csv`, `e0_check.csv` |
| `fig_cost_accuracy.{pdf,png}` | Cost against accuracy, one column | P1-E01 `e1_summary.csv`, `config/search_runs.json` |
| `fig_uncertainty.{pdf,png}` (+ panels) | Calibration of predictive intervals; error by decile of predicted spread | P1-E03 `a_uncertainty.csv`, `predictions/uncertainty/` |
| `fig_scans_cost.{pdf,png}` (+ panels) | Error against scans per reference point; fit plus predict time and GPU memory against context rows | P1-E03 `b_scans.csv` |
| `figure_notes.json` | Per figure: what it shows, defects found and fixed before showing, limits of the checks | |

PNGs are 900 dpi at the printed size (figures are drawn at twice the IEEE size and shrink to 7.16 in or 3.5 in); PDFs are vector with embedded fonts (TeX Gyre Pagella). `preview_hi/` holds the copies used on the review page.
