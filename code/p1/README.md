# code/p1

Experiment code for paper 1, written for `briefs/P1-E01.md` and reused by `briefs/P1-E02.md`.

| File | What it holds |
|---|---|
| `data.py` | Loading SODIndoorLoc, the count check, the two ways of writing "not detected", the TabPFN context cap |
| `metrics.py` | Positioning error, its five statistics, the bootstrap over test points |
| `models.py` | One wrapper per model (`tabpfn-nan`, `tabpfn-ph`, `tabicl`, `knn`, `rf`, `lgbm-ph`, `lgbm-nan`, `svr`, `mlp`, `gp`) and the timed fit-and-predict |
| `tuning.py` | Search spaces and the Optuna search (TPE, seed 0, 30 trials, 3-fold GroupKFold by reference point) |
| `e1.py` | P1-E01 command line: `gate`, `search`, `final`, `partb` (search then final), `report` |
| `report_e1.py`, `plot_e1_mean_error.py` | Summary tables, bootstrap, figure and `RESULTS.md` of P1-E01 |
| `assets.py` | Weight files with SHA-256, licences, `assets.md` |
| `nb.py` | Tables and plots shown in the notebook that runs a brief on a compute node |
| `notebook/` | The cells of that notebook and the script that sends them to a node |

Run from the repository root with `PYTHONPATH=code`, after cloning the dataset into `data/SODIndoorLoc`:

```
python -m p1.e1 gate   --out results/P1-E01
python -m p1.e1 partb  --out results/P1-E01 --configs CETC331 HCXY-All HCXY-AP SYL-All SYL-AP
python -m p1.assets    --out results/P1-E01
python -m p1.e1 report --out results/P1-E01
```

Every search and every fit-and-predict run writes its own files and is skipped when they exist, so a stopped job can be started again.
