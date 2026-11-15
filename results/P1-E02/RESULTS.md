# P1-E02 results: fewer reference points, and access points that go missing

Brief: `briefs/P1-E02.md`, revision 1. Report written 2026-11-15T02:54:06Z.

## How this brief was run

- **Machines and code.** The same three molab nodes as `P1-E01` (RTX PRO 6000, 20-core quota). Part A searches and refits ran from commit `4393db1`, the foundation-model runs, Part B and the 100% share from commit `0f526ea` of `exp/P1-E02`; both contain the same `P1-E01` and `P1-E02` model and search code. Every run file records its commit.
- **Part A split by draws.** Foundation-model runs: draws 0 to 2 on node A, 3 to 5 on node B, 6 to 9 on node C (GPU jobs, alongside the searches). Baseline searches and refits (CPU): node A draws 0, 1, 2 and 6; node B draws 3, 4, 5 and 7; node C draws 9 and 8. Draws were moved between nodes as nodes finished early. Draw 7 was started on node A; its 16 finished searches were copied to node B from node A's Drive checkpoint and node B ran the rest, so nothing was computed twice on purpose.
- **Part B and the 100% share** ran on the node that holds the configuration's `P1-E01` best values: HCXY-All on A, SYL-All on B, CETC331 on C.
- **Thread setting for Part A.** Several searches with 4-thread LightGBM at once oversubscribed the 20 cores, so Part A ran LightGBM with 1 thread per model and 6 searches in parallel (3 folds each). On a node, the same LightGBM model fitted with 1 and with 4 threads gave identical predictions (largest difference 0.0). The 5 Part A searches per node that finished before the change (kNN, MLP, RF, SVR of CETC331 at 50% and MLP of HCXY-All at 50%) involve no LightGBM. Part B and the 100% share use 4 threads, as in `P1-E01`. MLP and GP keep 4 BLAS threads everywhere.

## Deviations and things to know

1. **The 100% share** reuses `P1-E01`: seeds 0 to 4 of the seeded models are the `P1-E01` runs; seeds 5 to 9 were run here with the `P1-E01` best values; `knn`, `svr` and `gp` have no randomness, so their one `P1-E01` run stands for every draw (the band at 100% is the spread of the seeded models only).
2. **Draw shuffles** use `numpy.random.default_rng(d).permutation`, for reference points (Part A) and MAC columns (Part B).
3. **Part B prediction** stacked the 61 altered copies of each test file and predicted them in chunks of 20,000 rows. At 0% switched off, Part B reproduces the `P1-E01` seed-0 mean error: 19 of 30 configuration-model pairs agree to within 1e-9 m. The others: kNN differs by 0.0054 m (CETC331) and 0.0008 m (HCXY-All), probably from ties between equally distant neighbours when the test rows are queried in a different batch; TabICL by up to 0.0011 m and TabPFN by at most 5e-6 m, from predicting the rows in stacked chunks on the GPU (`metrics/e3_check_against_e1.csv`).
4. **Timings in this brief are not cost figures**: Part A ran several jobs per node at once. The clean costs are in `P1-E01`.
5. **Duplicates and restarts.** 25 files were produced on two nodes when draws moved (five draw-6 searches first started on node C, five draw-7 fits of SYL-All at 50% during a relaunch on node A); their parameters, cross-validated scores and predictions are identical (largest difference 0.0) and one copy is kept. Separately, **restarts:** On two occasions a Part A job was stopped and restarted (to change its thread setting, and to split draws 6 and 7); searches that were running were discarded and recomputed from the start; finished ones were kept.
6. **Per-row predictions** are consolidated into one compressed file per part, configuration and model (`metrics/predictions/e2_*` and `e3_*`).
7. **Wall-clock time**: 2 h 34 min (2026-11-15T00:11:36Z to 2026-11-15T02:46:18Z, three nodes in parallel and alongside `P1-E01` and `P1-E03`). No stop condition was triggered.

## Part A. Fewer reference points (E2)

Reference points kept, as in the brief's table: all counts match (share times the number of reference points, rounded up). Draw `d` shuffles the reference points with `numpy.random.default_rng(d).permutation` and keeps the first ones, so each smaller survey is inside the larger one. The baselines were re-tuned on every reduced survey (30 Optuna trials, 3-fold GroupKFold by reference point) and refitted with seed `d`; the tabular foundation models used the reduced survey as context with seed `d`. The full test file was always predicted.

The 100% share reuses P1-E01: seeds 0 to 4 of the seeded models are the P1-E01 runs, seeds 5 to 9 were run here with the P1-E01 best values; `knn`, `svr` and `gp` have no randomness, so their one P1-E01 run stands for every draw.

### CETC331: mean positioning error (m), mean ± std over 10 draws

| Model | 5% | 10% | 25% | 50% | 100% |
|---|---|---|---|---|---|
| `tabpfn-nan` | 4.35 ± 0.45 | 3.47 ± 0.25 | 2.94 ± 0.06 | 2.77 ± 0.10 | 2.69 ± 0.02 |
| `tabpfn-ph` | 4.04 ± 0.35 | 3.45 ± 0.15 | 2.94 ± 0.10 | 2.78 ± 0.06 | 2.69 ± 0.02 |
| `tabicl` | 4.07 ± 0.28 | 3.25 ± 0.14 | 2.82 ± 0.11 | 2.69 ± 0.06 | 2.61 ± 0.02 |
| `knn` | 4.30 ± 0.27 | 3.50 ± 0.23 | 3.04 ± 0.10 | 2.86 ± 0.05 | 2.91 |
| `rf` | 5.93 ± 0.51 | 4.79 ± 0.34 | 4.12 ± 0.14 | 3.81 ± 0.12 | 3.52 ± 0.03 |
| `lgbm-ph` | 5.54 ± 0.62 | 4.61 ± 0.39 | 3.95 ± 0.21 | 3.69 ± 0.15 | 3.32 ± 0.04 |
| `lgbm-nan` | 5.70 ± 0.47 | 4.77 ± 0.41 | 4.11 ± 0.20 | 3.76 ± 0.16 | 3.42 ± 0.04 |
| `svr` | 4.30 ± 0.28 | 3.99 ± 0.26 | 3.84 ± 0.23 | 3.71 ± 0.23 | 3.64 ± 0.00 |
| `mlp` | 5.14 ± 0.87 | 4.37 ± 0.26 | 3.90 ± 0.16 | 3.63 ± 0.09 | 3.37 ± 0.12 |
| `gp` | 4.35 ± 0.31 | 3.81 ± 0.18 | 3.56 ± 0.12 | 3.31 ± 0.09 | 3.06 ± 0.00 |

### HCXY-All: mean positioning error (m), mean ± std over 10 draws

| Model | 5% | 10% | 25% | 50% | 100% |
|---|---|---|---|---|---|
| `tabpfn-nan` | 7.89 ± 2.19 | 4.07 ± 0.63 | 2.47 ± 0.33 | 2.10 ± 0.48 | 1.73 ± 0.25 |
| `tabpfn-ph` | 6.65 ± 1.57 | 3.70 ± 0.48 | 2.43 ± 0.24 | 1.84 ± 0.09 | 1.53 ± 0.06 |
| `tabicl` | 6.15 ± 1.33 | 3.40 ± 0.38 | 2.31 ± 0.17 | 1.99 ± 0.08 | 1.79 ± 0.04 |
| `knn` | 6.37 ± 1.01 | 3.90 ± 0.51 | 2.59 ± 0.17 | 2.17 ± 0.12 | 1.80 |
| `rf` | 7.87 ± 1.60 | 4.92 ± 1.52 | 3.14 ± 0.39 | 2.34 ± 0.20 | 1.88 ± 0.03 |
| `lgbm-ph` | 8.13 ± 1.32 | 5.10 ± 0.72 | 3.51 ± 0.31 | 2.70 ± 0.20 | 2.19 ± 0.05 |
| `lgbm-nan` | 8.37 ± 1.15 | 5.34 ± 0.67 | 3.72 ± 0.36 | 2.79 ± 0.25 | 2.09 ± 0.04 |
| `svr` | 10.78 ± 2.06 | 8.35 ± 0.91 | 7.59 ± 1.81 | 6.77 ± 1.70 | 4.93 |
| `mlp` | 10.62 ± 1.82 | 7.36 ± 1.79 | 5.39 ± 1.23 | 4.77 ± 0.90 | 4.52 ± 0.75 |
| `gp` | 24.27 ± 3.23 | 14.68 ± 2.40 | 12.56 ± 1.98 | 9.89 ± 1.95 | 7.59 |

### SYL-All: mean positioning error (m), mean ± std over 10 draws

| Model | 5% | 10% | 25% | 50% | 100% |
|---|---|---|---|---|---|
| `tabpfn-nan` | 10.13 ± 1.42 | 6.21 ± 0.94 | 4.23 ± 0.35 | 3.66 ± 0.21 | 3.39 ± 0.07 |
| `tabpfn-ph` | 8.14 ± 1.75 | 5.58 ± 0.74 | 3.91 ± 0.28 | 3.42 ± 0.15 | 3.22 ± 0.04 |
| `tabicl` | 6.32 ± 0.68 | 4.76 ± 0.47 | 3.52 ± 0.17 | 3.29 ± 0.09 | 3.25 ± 0.02 |
| `knn` | 6.85 ± 1.05 | 4.87 ± 0.50 | 4.19 ± 0.27 | 4.11 ± 0.24 | 4.09 |
| `rf` | 7.37 ± 1.04 | 5.67 ± 0.62 | 4.21 ± 0.17 | 3.70 ± 0.15 | 3.56 ± 0.03 |
| `lgbm-ph` | 8.27 ± 1.45 | 5.94 ± 0.69 | 4.39 ± 0.26 | 3.72 ± 0.11 | 3.50 ± 0.08 |
| `lgbm-nan` | 8.17 ± 1.04 | 6.26 ± 0.75 | 4.55 ± 0.35 | 3.91 ± 0.15 | 3.66 ± 0.06 |
| `svr` | 8.98 ± 1.00 | 7.24 ± 0.94 | 6.21 ± 0.40 | 5.96 ± 0.47 | 6.89 |
| `mlp` | 7.89 ± 1.18 | 6.67 ± 1.13 | 5.32 ± 0.30 | 4.79 ± 0.32 | 4.52 ± 0.30 |
| `gp` | 17.74 ± 1.69 | 12.90 ± 2.08 | 8.01 ± 1.09 | 6.91 ± 0.69 | 6.27 |

### Smallest share at which each tabular foundation model reaches tuned kNN at 100%

Mean error averaged over draws, against the mean error of tuned `knn` on the full survey; linear interpolation between shares on a logarithmic share axis. Source: `metrics/e2_crossing.csv`.

| Config | Model | kNN at 100% (m) | 5% (m) | 10% (m) | 25% (m) | 50% (m) | 100% (m) | Crossing share (%) | Crossing ref. points | Above kNN again later |
|---|---|---|---|---|---|---|---|---|---|---|
| CETC331 | `tabpfn-nan` | 2.910 | 4.350 | 3.474 | 2.940 | 2.773 | 2.689 | 28.33 | 270.6 | False |
| CETC331 | `tabpfn-ph` | 2.910 | 4.035 | 3.445 | 2.942 | 2.777 | 2.686 | 28.58 | 273.0 | False |
| CETC331 | `tabicl` | 2.910 | 4.068 | 3.248 | 2.823 | 2.686 | 2.605 | 20.72 | 197.8 | False |
| HCXY-All | `tabpfn-nan` | 1.805 | 7.887 | 4.072 | 2.468 | 2.098 | 1.735 | 87.51 | 331.7 | False |
| HCXY-All | `tabpfn-ph` | 1.805 | 6.652 | 3.697 | 2.433 | 1.845 | 1.534 | 54.7 | 207.3 | False |
| HCXY-All | `tabicl` | 1.805 | 6.151 | 3.405 | 2.309 | 1.994 | 1.792 | 95.62 | 362.4 | False |
| SYL-All | `tabpfn-nan` | 4.091 | 10.131 | 6.207 | 4.233 | 3.660 | 3.388 | 29.69 | 87.9 | False |
| SYL-All | `tabpfn-ph` | 4.091 | 8.142 | 5.584 | 3.908 | 3.417 | 3.221 | 22.62 | 67.0 | False |
| SYL-All | `tabicl` | 4.091 | 6.318 | 4.759 | 3.519 | 3.286 | 3.250 | 16.39 | 48.5 | False |

In CETC331 every test location is also a reference-point location. Per-row predictions record whether the test row's location is among the kept reference points (`in_kept`).

## Part B. Access points that go missing after the survey (E3)

Each model was fitted once per configuration on the whole training file, with seed 0 and, for the baselines, the P1-E01 best values. In every test row, the switched-off columns were set to "not detected" and then written the way the model expects (NaN or -105). Draw `d` shuffles the MAC columns with `numpy.random.default_rng(d).permutation` and switches off the first ones. The altered copies of a test file were stacked and predicted in chunks of 20,000 rows.

### CETC331 (52 MAC columns): mean positioning error (m), mean ± std over 10 draws

| Model | 0% | 10% | 20% | 30% | 40% | 50% | 60% |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | 2.70 | 2.88 ± 0.20 | 3.13 ± 0.34 | 3.43 ± 0.36 | 3.89 ± 0.57 | 4.34 ± 0.70 | 5.19 ± 0.82 |
| `tabpfn-ph` | 2.68 | 3.13 ± 0.32 | 3.72 ± 0.76 | 4.42 ± 0.61 | 5.35 ± 0.98 | 6.30 ± 1.01 | 7.97 ± 0.96 |
| `tabicl` | 2.60 | 2.92 ± 0.21 | 3.19 ± 0.28 | 3.45 ± 0.34 | 3.77 ± 0.30 | 4.06 ± 0.22 | 4.86 ± 0.42 |
| `knn` | 2.92 | 3.21 ± 0.16 | 3.52 ± 0.21 | 3.90 ± 0.32 | 4.59 ± 0.60 | 5.62 ± 0.74 | 8.23 ± 1.48 |
| `rf` | 3.49 | 5.56 ± 1.47 | 6.58 ± 1.76 | 7.49 ± 1.44 | 8.38 ± 1.63 | 9.30 ± 1.57 | 10.35 ± 1.86 |
| `lgbm-ph` | 3.32 | 5.19 ± 1.28 | 6.21 ± 1.59 | 7.12 ± 1.27 | 7.87 ± 1.55 | 8.69 ± 1.45 | 9.62 ± 1.48 |
| `lgbm-nan` | 3.46 | 5.54 ± 1.46 | 6.52 ± 1.77 | 7.50 ± 1.49 | 8.41 ± 1.75 | 9.19 ± 1.54 | 10.21 ± 1.66 |
| `svr` | 3.64 | 7.40 ± 1.09 | 9.43 ± 0.94 | 11.23 ± 0.87 | 12.29 ± 0.69 | 13.05 ± 0.57 | 13.88 ± 0.44 |
| `mlp` | 3.23 | 5.10 ± 0.84 | 6.53 ± 0.95 | 8.11 ± 1.07 | 8.86 ± 1.29 | 9.53 ± 1.18 | 11.01 ± 0.89 |
| `gp` | 3.06 | 5.54 ± 0.86 | 7.00 ± 0.91 | 8.42 ± 1.20 | 9.35 ± 0.91 | 10.22 ± 1.04 | 11.60 ± 0.94 |

### HCXY-All (347 MAC columns): mean positioning error (m), mean ± std over 10 draws

| Model | 0% | 10% | 20% | 30% | 40% | 50% | 60% |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | 1.77 | 1.75 ± 0.22 | 1.91 ± 0.33 | 2.07 ± 0.31 | 2.48 ± 0.37 | 3.35 ± 0.48 | 4.47 ± 0.79 |
| `tabpfn-ph` | 1.46 | 1.77 ± 0.21 | 2.37 ± 0.67 | 3.17 ± 0.80 | 4.06 ± 0.92 | 6.05 ± 1.05 | 8.46 ± 1.33 |
| `tabicl` | 1.75 | 1.87 ± 0.09 | 2.07 ± 0.19 | 2.34 ± 0.24 | 2.80 ± 0.35 | 3.32 ± 0.43 | 4.24 ± 0.73 |
| `knn` | 1.80 | 1.91 ± 0.08 | 2.23 ± 0.19 | 2.66 ± 0.24 | 3.37 ± 0.59 | 5.17 ± 1.56 | 8.21 ± 3.15 |
| `rf` | 1.86 | 3.92 ± 1.54 | 6.72 ± 2.46 | 9.12 ± 2.72 | 11.22 ± 2.04 | 15.16 ± 2.27 | 18.85 ± 2.96 |
| `lgbm-ph` | 2.20 | 4.10 ± 1.10 | 6.80 ± 2.53 | 9.18 ± 2.82 | 11.70 ± 2.36 | 15.18 ± 2.58 | 19.16 ± 2.82 |
| `lgbm-nan` | 2.10 | 3.78 ± 1.03 | 6.50 ± 2.27 | 8.77 ± 2.63 | 11.25 ± 2.19 | 14.54 ± 2.06 | 18.54 ± 3.05 |
| `svr` | 4.93 | 4.62 ± 0.94 | 5.59 ± 1.30 | 6.71 ± 1.31 | 8.78 ± 1.11 | 11.92 ± 1.61 | 15.07 ± 1.87 |
| `mlp` | 5.41 | 5.31 ± 1.15 | 6.24 ± 1.43 | 6.92 ± 1.47 | 8.60 ± 1.28 | 10.73 ± 1.81 | 13.58 ± 1.89 |
| `gp` | 7.59 | 7.57 ± 0.96 | 9.78 ± 2.37 | 11.87 ± 2.50 | 14.96 ± 2.30 | 18.34 ± 2.61 | 21.30 ± 2.72 |

### SYL-All (363 MAC columns): mean positioning error (m), mean ± std over 10 draws

| Model | 0% | 10% | 20% | 30% | 40% | 50% | 60% |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | 3.49 | 3.49 ± 0.04 | 3.61 ± 0.17 | 3.76 ± 0.31 | 3.98 ± 0.36 | 4.44 ± 0.57 | 5.23 ± 0.89 |
| `tabpfn-ph` | 3.31 | 3.34 ± 0.08 | 3.64 ± 0.28 | 3.84 ± 0.35 | 4.23 ± 0.74 | 5.04 ± 1.01 | 6.33 ± 1.85 |
| `tabicl` | 3.24 | 3.26 ± 0.09 | 3.39 ± 0.10 | 3.47 ± 0.12 | 3.61 ± 0.14 | 3.83 ± 0.27 | 4.50 ± 0.66 |
| `knn` | 4.09 | 4.22 ± 0.17 | 4.37 ± 0.21 | 5.13 ± 0.97 | 6.33 ± 1.31 | 9.43 ± 4.15 | 14.14 ± 5.01 |
| `rf` | 3.53 | 3.95 ± 0.34 | 5.20 ± 1.42 | 6.07 ± 1.84 | 6.62 ± 1.97 | 8.18 ± 2.30 | 10.38 ± 2.84 |
| `lgbm-ph` | 3.60 | 4.00 ± 0.36 | 5.46 ± 1.50 | 6.21 ± 1.67 | 6.70 ± 1.76 | 8.14 ± 2.00 | 10.46 ± 2.43 |
| `lgbm-nan` | 3.72 | 4.13 ± 0.39 | 5.67 ± 1.50 | 6.53 ± 1.68 | 7.07 ± 1.78 | 8.64 ± 2.05 | 10.97 ± 2.35 |
| `svr` | 6.89 | 7.09 ± 0.33 | 7.80 ± 0.97 | 8.25 ± 1.38 | 8.95 ± 1.54 | 10.02 ± 1.67 | 12.03 ± 2.46 |
| `mlp` | 4.52 | 4.59 ± 0.16 | 5.05 ± 0.33 | 5.55 ± 0.62 | 6.16 ± 0.64 | 7.10 ± 0.92 | 8.75 ± 1.15 |
| `gp` | 6.27 | 6.44 ± 0.31 | 7.44 ± 0.78 | 8.25 ± 1.03 | 9.52 ± 1.27 | 11.04 ± 1.42 | 12.94 ± 1.91 |

Check: at 0% switched off, the Part B fits reproduce the P1-E01 seed-0 mean error with a largest absolute difference of 0.0054 m over 30 configuration-model pairs (`metrics/e3_check_against_e1.csv`).

## Figures

- `figures/e2_reference_points.pdf` / `.png`: mean error against share of reference points kept (logarithmic axis), one line per model, band from the lowest to the highest draw; one panel per configuration and one averaged over the three.

- `figures/e3_missing_aps.pdf` / `.png`: mean error against share of access points switched off, same style.

Each figure is produced by `figures/plot_e2_curves.py` from the CSV next to it.

Per-row predictions: 60 files in `metrics/predictions/` (one per part, configuration and model; Part A files carry `share`, `draw` and `in_kept`, Part B files carry `share`, `draw` and `n_off`).
