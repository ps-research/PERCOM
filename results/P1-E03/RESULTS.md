# P1-E03 results: uncertainty, scans per point, more seeds, more missing-AP draws, phone and user

Brief: `briefs/P1-E03.md` on this branch (approved by the PI in chat on 2026-11-15, written by the compute node; not on `main`). Report written 2026-11-15T02:58:12Z.

## How this brief came about and how it was run

- **Origin.** The PI asked on 2026-11-15 for all five options (A to E) the compute node had proposed while the GPUs were idle. The brief `briefs/P1-E03.md` was written by the compute node on that instruction and lives on this branch, not on `main`; the planning session has not reviewed it. Nothing here should enter the paper before this pull request is merged.
- **Machines and code.** The same three molab nodes. Runs record their code commit: `6d16af4` (573 runs).
- **Placement.** A (uncertainty): HCXY-All and HCXY-AP on node A, SYL-All and SYL-AP on node B, CETC331 on node C. B (scans): HCXY-All on node A, SYL-All on node B. C (seeds 5 to 19): HCXY-All on A, SYL-All on B, CETC331, HCXY-AP and SYL-AP on C (the two AP configurations were moved to node C when its GPU fell idle). D (Part B draws 10 to 29): on the node holding the configuration's `P1-E01` best values. E: computed here from the saved predictions.

## Things to know

1. **Quantiles.** TabPFN: `predict(output_type="main", quantiles=...)`; TabICL: `predict(output_type=["mean", "quantiles"], alphas=...)`; GP: Gaussian quantiles from `predict(return_std=True)` of each coordinate's GP (fitted with `normalize_y=True`, so the standard deviation is in metres). The point prediction is the mean, as in `P1-E01`; coverage is per coordinate, and for both coordinates at once.
2. **Scans per point.** k scans of every reference point were drawn without replacement with seed s. At k = 30 on HCXY-All (11,370 rows) TabPFN ran with `ignore_pretraining_limits=True` (10 runs). `knn` used its `P1-E01` best values without re-tuning; `knn` and `gp` ran on the seed-0 draw only.
3. **Seeds 5 to 19** used the `P1-E01` code path unchanged (including the HCXY context cap drawn with the run seed). Their timings were measured while other jobs shared the nodes; the clean costs are in `P1-E01`.
4. **Part B draws 10 to 29** predicted the stacked altered test files in chunks of 10,000 rows; draws 0 to 9 come from `P1-E02`.
5. **Phone and user.** Every phone and user of the test files also appears in the training files, so E is a breakdown, not a cross-device test. CETC331 has one phone and one user and is left out.
6. **Wall-clock time**: 1 h 37 min (2026-11-15T00:38:41Z to 2026-11-15T02:16:32Z, alongside `P1-E02`). No stop condition was triggered.

## A. Uncertainty

Mean over seeds (5 for the foundation models, 1 for `gp`). Coverage is the share of test rows whose true coordinate lies in the central interval; the nominal value is the interval level. For both coordinates at once, independent coordinates would give the square of the level (0.64 at 80%). Spearman: correlation between the predicted spread and the positioning error. Source: `metrics/a_uncertainty.csv`.

| Config | Model | Mean (m) | Cov. 50% (E/N) | Cov. 80% (E/N) | Cov. 90% (E/N) | Cov. 95% (E/N) | Cov. 80% both | Width 80% (m) | Spearman | Err. most / least confident 10% (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| CETC331 | `gp` | 3.064 | 0.58/0.40 | 0.80/0.58 | 0.86/0.70 | 0.90/0.78 | 0.48 | 4.47 | -0.04 | 2.91 / 3.62 |
| CETC331 | `tabicl` | 2.596 | 0.45/0.30 | 0.68/0.58 | 0.81/0.71 | 0.87/0.81 | 0.38 | 3.19 | 0.20 | 2.34 / 3.78 |
| CETC331 | `tabpfn-nan` | 2.682 | 0.41/0.32 | 0.72/0.54 | 0.84/0.65 | 0.90/0.74 | 0.39 | 2.97 | 0.30 | 2.05 / 4.37 |
| CETC331 | `tabpfn-ph` | 2.693 | 0.45/0.31 | 0.75/0.57 | 0.88/0.67 | 0.92/0.75 | 0.43 | 3.24 | 0.25 | 1.96 / 2.98 |
| HCXY-AP | `gp` | 9.327 | 0.51/0.46 | 0.76/0.74 | 0.90/0.85 | 0.93/0.90 | 0.60 | 15.86 | 0.70 | 2.83 / 31.54 |
| HCXY-AP | `tabicl` | 2.827 | 0.48/0.47 | 0.74/0.75 | 0.83/0.87 | 0.91/0.93 | 0.56 | 4.21 | 0.38 | 1.74 / 4.91 |
| HCXY-AP | `tabpfn-nan` | 2.704 | 0.50/0.42 | 0.72/0.70 | 0.82/0.83 | 0.90/0.89 | 0.53 | 5.06 | 0.49 | 1.27 / 7.54 |
| HCXY-AP | `tabpfn-ph` | 3.414 | 0.48/0.45 | 0.76/0.65 | 0.85/0.71 | 0.92/0.76 | 0.52 | 5.01 | 0.47 | 2.44 / 9.92 |
| HCXY-All | `gp` | 7.585 | 0.60/0.55 | 0.85/0.92 | 0.92/0.95 | 0.98/0.98 | 0.79 | 19.09 | 0.49 | 3.78 / 21.40 |
| HCXY-All | `tabicl` | 1.781 | 0.43/0.44 | 0.71/0.72 | 0.82/0.85 | 0.89/0.91 | 0.53 | 2.78 | 0.19 | 1.23 / 3.32 |
| HCXY-All | `tabpfn-nan` | 1.835 | 0.46/0.41 | 0.77/0.76 | 0.84/0.87 | 0.88/0.92 | 0.62 | 4.08 | 0.40 | 1.11 / 4.62 |
| HCXY-All | `tabpfn-ph` | 1.558 | 0.50/0.39 | 0.76/0.70 | 0.85/0.83 | 0.89/0.88 | 0.56 | 2.76 | 0.26 | 1.05 / 2.95 |
| SYL-AP | `gp` | 4.671 | 0.55/0.61 | 0.77/0.79 | 0.90/0.86 | 0.92/0.88 | 0.63 | 8.85 | -0.09 | 8.44 / 5.21 |
| SYL-AP | `tabicl` | 3.492 | 0.25/0.41 | 0.44/0.67 | 0.60/0.75 | 0.72/0.83 | 0.30 | 3.41 | 0.01 | 5.87 / 2.81 |
| SYL-AP | `tabpfn-nan` | 3.428 | 0.35/0.49 | 0.61/0.62 | 0.79/0.74 | 0.89/0.80 | 0.38 | 4.27 | 0.10 | 6.17 / 4.33 |
| SYL-AP | `tabpfn-ph` | 3.305 | 0.42/0.46 | 0.71/0.61 | 0.82/0.71 | 0.88/0.77 | 0.42 | 4.14 | 0.24 | 5.36 / 3.00 |
| SYL-All | `gp` | 6.268 | 0.65/0.56 | 0.80/0.80 | 0.85/0.89 | 0.90/0.94 | 0.69 | 13.99 | 0.21 | 8.35 / 12.50 |
| SYL-All | `tabicl` | 3.258 | 0.20/0.43 | 0.44/0.61 | 0.59/0.71 | 0.73/0.83 | 0.27 | 3.19 | 0.12 | 5.82 / 3.20 |
| SYL-All | `tabpfn-nan` | 3.404 | 0.38/0.47 | 0.71/0.71 | 0.85/0.81 | 0.91/0.88 | 0.54 | 5.45 | 0.14 | 6.31 / 4.21 |
| SYL-All | `tabpfn-ph` | 3.217 | 0.36/0.49 | 0.66/0.64 | 0.78/0.72 | 0.86/0.81 | 0.45 | 4.32 | 0.14 | 6.09 / 3.12 |

## B. Scans per reference point

Mean error (m) averaged over the 5 scan draws (`knn` and `gp`: seed-0 draw only). `knn` uses its P1-E01 best values. Source: `metrics/b_scans.csv`.

### HCXY-All

| Model | k=1 | k=2 | k=5 | k=10 | k=20 | k=26 | k=30 |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | 1.695 | 1.556 | 1.766 | 1.585 | 1.932 | 1.835 | 1.982 |
| `tabpfn-ph` | 1.714 | 1.6 | 1.571 | 1.537 | 1.523 | 1.558 | 1.535 |
| `tabicl` | 1.792 | 1.658 | 1.627 | 1.715 | 1.753 | 1.739 | 1.781 |
| `knn` | 3.108 | 2.373 | 1.969 | 1.803 | 1.795 | 1.805 | 1.805 |
| `gp` | 7.474 | 8.29 | 8.248 | 7.766 | 7.727 | 7.539 | 7.585 |

Cost of the foundation models by context size:

| Model | k | Context rows | Fit (s) | Predict (s) | Peak GPU (MB) |
|---|---|---|---|---|---|
| `tabicl` | 1 | 379 | 3.33 | 1.27 | 4,335 |
| `tabicl` | 2 | 758 | 4.02 | 1.80 | 5,948 |
| `tabicl` | 5 | 1,895 | 4.66 | 2.48 | 10,494 |
| `tabicl` | 10 | 3,790 | 5.22 | 3.79 | 17,944 |
| `tabicl` | 20 | 7,580 | 6.60 | 6.41 | 32,725 |
| `tabicl` | 26 | 9,854 | 7.03 | 7.87 | 41,647 |
| `tabicl` | 30 | 11,370 | 8.18 | 8.94 | 53,693 |
| `tabpfn-nan` | 1 | 379 | 4.34 | 1.91 | 1,112 |
| `tabpfn-nan` | 2 | 758 | 6.47 | 2.30 | 1,419 |
| `tabpfn-nan` | 5 | 1,895 | 10.37 | 3.70 | 2,348 |
| `tabpfn-nan` | 10 | 3,790 | 11.69 | 5.98 | 3,883 |
| `tabpfn-nan` | 20 | 7,580 | 19.11 | 13.62 | 6,994 |
| `tabpfn-nan` | 26 | 9,854 | 25.46 | 19.20 | 8,861 |
| `tabpfn-nan` | 30 | 11,370 | 29.53 | 24.25 | 10,188 |
| `tabpfn-ph` | 1 | 379 | 4.89 | 1.76 | 1,112 |
| `tabpfn-ph` | 2 | 758 | 7.60 | 2.31 | 1,419 |
| `tabpfn-ph` | 5 | 1,895 | 11.91 | 3.64 | 2,348 |
| `tabpfn-ph` | 10 | 3,790 | 15.06 | 6.07 | 3,883 |
| `tabpfn-ph` | 20 | 7,580 | 22.77 | 13.69 | 6,994 |
| `tabpfn-ph` | 26 | 9,854 | 28.77 | 19.12 | 8,861 |
| `tabpfn-ph` | 30 | 11,370 | 31.14 | 24.03 | 10,222 |

### SYL-All

| Model | k=1 | k=2 | k=5 | k=10 | k=20 | k=26 | k=30 |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | 3.202 | 3.179 | 3.246 | 3.328 | 3.322 | 3.399 | 3.404 |
| `tabpfn-ph` | 3.197 | 3.113 | 3.098 | 3.214 | 3.187 | 3.208 | 3.217 |
| `tabicl` | 3.185 | 3.195 | 3.246 | 3.221 | 3.237 | 3.247 | 3.258 |
| `knn` | 3.767 | 4.083 | 4.208 | 4.05 | 3.992 | 4.107 | 4.091 |
| `gp` | 6.622 | 6.717 | 6.309 | 5.976 | 6.413 | 6.071 | 6.268 |

Cost of the foundation models by context size:

| Model | k | Context rows | Fit (s) | Predict (s) | Peak GPU (MB) |
|---|---|---|---|---|---|
| `tabicl` | 1 | 296 | 3.42 | 1.30 | 4,395 |
| `tabicl` | 2 | 592 | 3.33 | 1.37 | 5,465 |
| `tabicl` | 5 | 1,480 | 3.32 | 1.81 | 8,460 |
| `tabicl` | 10 | 2,960 | 4.53 | 3.02 | 13,560 |
| `tabicl` | 20 | 5,920 | 5.13 | 4.86 | 23,627 |
| `tabicl` | 26 | 7,696 | 5.48 | 5.74 | 29,670 |
| `tabicl` | 30 | 8,880 | 5.34 | 5.76 | 33,691 |
| `tabpfn-nan` | 1 | 296 | 3.72 | 2.19 | 1,084 |
| `tabpfn-nan` | 2 | 592 | 5.59 | 2.18 | 1,288 |
| `tabpfn-nan` | 5 | 1,480 | 8.00 | 3.09 | 1,933 |
| `tabpfn-nan` | 10 | 2,960 | 10.18 | 4.54 | 2,824 |
| `tabpfn-nan` | 20 | 5,920 | 14.43 | 8.99 | 4,841 |
| `tabpfn-nan` | 26 | 7,696 | 16.77 | 12.24 | 6,040 |
| `tabpfn-nan` | 30 | 8,880 | 17.27 | 14.68 | 6,840 |
| `tabpfn-ph` | 1 | 296 | 3.80 | 1.87 | 1,084 |
| `tabpfn-ph` | 2 | 592 | 6.17 | 2.12 | 1,288 |
| `tabpfn-ph` | 5 | 1,480 | 8.76 | 3.05 | 1,933 |
| `tabpfn-ph` | 10 | 2,960 | 11.86 | 4.49 | 2,824 |
| `tabpfn-ph` | 20 | 5,920 | 15.92 | 8.96 | 4,841 |
| `tabpfn-ph` | 26 | 7,696 | 17.32 | 12.19 | 6,040 |
| `tabpfn-ph` | 30 | 8,880 | 19.42 | 14.64 | 6,840 |

10 TabPFN runs (HCXY-All, k = 30, 11,370 rows) used `ignore_pretraining_limits=True`.

## C. Twenty seeds of the foundation models

Mean error (m) with a 95% interval over seeds (normal approximation); seeds 0 to 4 are the P1-E01 runs. Source: `metrics/c_seeds.csv`.

| Config | Model | Seeds | Mean, 5 seeds | Mean, all seeds | 95th, all seeds | Range of means |
|---|---|---|---|---|---|---|
| CETC331 | `tabpfn-nan` | 20 | 2.682 ± 0.020 | 2.688 ± 0.008 | 6.380 ± 0.076 | 2.662 to 2.717 |
| CETC331 | `tabpfn-ph` | 20 | 2.693 ± 0.019 | 2.671 ± 0.011 | 6.441 ± 0.051 | 2.627 to 2.717 |
| CETC331 | `tabicl` | 20 | 2.596 ± 0.020 | 2.603 ± 0.007 | 5.742 ± 0.072 | 2.571 to 2.639 |
| HCXY-All | `tabpfn-nan` | 20 | 1.835 ± 0.261 | 1.801 ± 0.122 | 4.812 ± 0.842 | 1.445 to 2.530 |
| HCXY-All | `tabpfn-ph` | 20 | 1.558 ± 0.063 | 1.525 ± 0.023 | 3.967 ± 0.117 | 1.445 to 1.646 |
| HCXY-All | `tabicl` | 20 | 1.781 ± 0.047 | 1.791 ± 0.015 | 4.153 ± 0.091 | 1.711 to 1.863 |
| HCXY-AP | `tabpfn-nan` | 20 | 2.704 ± 0.315 | 2.822 ± 0.113 | 10.963 ± 1.197 | 2.229 to 3.337 |
| HCXY-AP | `tabpfn-ph` | 20 | 3.414 ± 0.584 | 3.505 ± 0.146 | 12.138 ± 0.821 | 2.228 to 3.784 |
| HCXY-AP | `tabicl` | 20 | 2.827 ± 0.026 | 2.808 ± 0.033 | 9.180 ± 0.281 | 2.655 to 2.980 |
| SYL-All | `tabpfn-nan` | 20 | 3.404 ± 0.064 | 3.391 ± 0.027 | 7.073 ± 0.097 | 3.290 to 3.494 |
| SYL-All | `tabpfn-ph` | 20 | 3.217 ± 0.047 | 3.229 ± 0.017 | 6.811 ± 0.109 | 3.163 to 3.306 |
| SYL-All | `tabicl` | 20 | 3.258 ± 0.018 | 3.257 ± 0.012 | 5.993 ± 0.081 | 3.219 to 3.308 |
| SYL-AP | `tabpfn-nan` | 20 | 3.428 ± 0.047 | 3.422 ± 0.019 | 7.292 ± 0.104 | 3.346 to 3.499 |
| SYL-AP | `tabpfn-ph` | 20 | 3.305 ± 0.026 | 3.309 ± 0.016 | 6.591 ± 0.129 | 3.251 to 3.379 |
| SYL-AP | `tabicl` | 20 | 3.492 ± 0.047 | 3.508 ± 0.024 | 7.266 ± 0.141 | 3.408 to 3.622 |

## D. Part B with 30 draws

Mean error (m) by share of access points switched off: mean ± std over draws 0 to 29 (draws 0 to 9 from P1-E02). Source: `metrics/d_e3_more.csv`.

### CETC331

| Model | 0% | 10% | 20% | 30% | 40% | 50% | 60% |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | 2.70 | 2.91 ± 0.18 | 3.20 ± 0.29 | 3.54 ± 0.46 | 4.05 ± 0.59 | 4.57 ± 0.82 | 5.48 ± 1.00 |
| `tabpfn-ph` | 2.68 | 3.15 ± 0.32 | 3.74 ± 0.62 | 4.55 ± 0.81 | 5.66 ± 1.08 | 6.73 ± 1.23 | 8.32 ± 1.25 |
| `tabicl` | 2.60 | 2.92 ± 0.16 | 3.22 ± 0.21 | 3.58 ± 0.38 | 3.92 ± 0.42 | 4.32 ± 0.62 | 5.23 ± 0.82 |
| `knn` | 2.92 | 3.22 ± 0.12 | 3.48 ± 0.20 | 3.93 ± 0.39 | 4.69 ± 0.84 | 5.68 ± 1.06 | 8.47 ± 1.96 |
| `rf` | 3.49 | 5.19 ± 1.42 | 6.19 ± 1.62 | 7.23 ± 1.59 | 8.39 ± 1.72 | 9.31 ± 1.71 | 10.64 ± 1.92 |
| `lgbm-ph` | 3.32 | 4.91 ± 1.31 | 5.88 ± 1.56 | 6.85 ± 1.46 | 7.90 ± 1.57 | 8.77 ± 1.53 | 9.95 ± 1.61 |
| `lgbm-nan` | 3.46 | 5.18 ± 1.46 | 6.19 ± 1.73 | 7.22 ± 1.62 | 8.34 ± 1.73 | 9.19 ± 1.68 | 10.36 ± 1.73 |
| `svr` | 3.64 | 7.37 ± 1.01 | 9.45 ± 0.82 | 10.98 ± 0.78 | 12.04 ± 0.74 | 13.05 ± 0.54 | 13.87 ± 0.42 |
| `mlp` | 3.23 | 5.16 ± 0.76 | 6.39 ± 0.89 | 7.59 ± 1.12 | 8.63 ± 1.06 | 9.81 ± 1.10 | 11.02 ± 1.02 |
| `gp` | 3.06 | 5.46 ± 0.96 | 6.92 ± 0.98 | 8.04 ± 1.14 | 9.07 ± 0.91 | 10.32 ± 0.90 | 11.54 ± 0.90 |

### HCXY-All

| Model | 0% | 10% | 20% | 30% | 40% | 50% | 60% |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | 1.77 | 1.85 ± 0.17 | 1.99 ± 0.29 | 2.19 ± 0.33 | 2.52 ± 0.39 | 3.17 ± 0.57 | 4.15 ± 0.78 |
| `tabpfn-ph` | 1.46 | 1.71 ± 0.15 | 2.23 ± 0.45 | 2.99 ± 0.59 | 3.88 ± 0.79 | 5.70 ± 1.11 | 8.12 ± 1.48 |
| `tabicl` | 1.75 | 1.88 ± 0.10 | 2.07 ± 0.18 | 2.34 ± 0.23 | 2.68 ± 0.29 | 3.24 ± 0.36 | 4.06 ± 0.53 |
| `knn` | 1.80 | 1.97 ± 0.12 | 2.32 ± 0.21 | 2.77 ± 0.38 | 3.48 ± 0.63 | 5.27 ± 1.76 | 8.38 ± 2.90 |
| `rf` | 1.86 | 3.46 ± 1.06 | 6.11 ± 1.97 | 8.70 ± 2.49 | 11.27 ± 2.69 | 14.69 ± 2.81 | 18.10 ± 3.20 |
| `lgbm-ph` | 2.20 | 3.93 ± 1.10 | 6.72 ± 2.23 | 9.29 ± 2.88 | 11.73 ± 2.99 | 15.04 ± 3.06 | 18.55 ± 2.90 |
| `lgbm-nan` | 2.10 | 3.58 ± 0.83 | 6.26 ± 2.00 | 8.91 ± 2.68 | 11.46 ± 2.99 | 14.80 ± 3.15 | 18.46 ± 3.11 |
| `svr` | 4.93 | 4.99 ± 0.80 | 5.83 ± 1.31 | 7.05 ± 1.24 | 8.96 ± 1.36 | 11.55 ± 1.64 | 14.96 ± 1.66 |
| `mlp` | 5.41 | 5.77 ± 0.98 | 6.60 ± 1.42 | 7.42 ± 1.53 | 8.80 ± 1.67 | 10.30 ± 1.72 | 12.81 ± 1.85 |
| `gp` | 7.59 | 7.91 ± 0.87 | 9.65 ± 1.92 | 11.63 ± 1.86 | 14.27 ± 2.05 | 17.27 ± 2.21 | 20.64 ± 2.12 |

### SYL-All

| Model | 0% | 10% | 20% | 30% | 40% | 50% | 60% |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | 3.49 | 3.50 ± 0.05 | 3.62 ± 0.17 | 3.73 ± 0.24 | 3.94 ± 0.28 | 4.32 ± 0.42 | 5.07 ± 0.81 |
| `tabpfn-ph` | 3.31 | 3.36 ± 0.09 | 3.54 ± 0.28 | 3.77 ± 0.35 | 4.16 ± 0.55 | 4.85 ± 0.77 | 5.97 ± 1.40 |
| `tabicl` | 3.24 | 3.28 ± 0.09 | 3.37 ± 0.12 | 3.46 ± 0.15 | 3.60 ± 0.17 | 3.87 ± 0.25 | 4.35 ± 0.52 |
| `knn` | 4.09 | 4.19 ± 0.18 | 4.38 ± 0.30 | 5.05 ± 0.77 | 6.17 ± 1.12 | 8.62 ± 2.80 | 13.52 ± 4.91 |
| `rf` | 3.53 | 3.93 ± 0.37 | 4.80 ± 1.15 | 5.67 ± 1.35 | 6.63 ± 1.56 | 7.99 ± 1.96 | 10.16 ± 2.34 |
| `lgbm-ph` | 3.60 | 3.94 ± 0.32 | 4.91 ± 1.27 | 5.75 ± 1.31 | 6.76 ± 1.51 | 8.02 ± 1.79 | 10.28 ± 2.16 |
| `lgbm-nan` | 3.72 | 4.06 ± 0.32 | 5.07 ± 1.30 | 6.03 ± 1.35 | 7.18 ± 1.54 | 8.52 ± 1.81 | 10.79 ± 2.04 |
| `svr` | 6.89 | 7.08 ± 0.33 | 7.51 ± 0.85 | 8.00 ± 1.10 | 8.68 ± 1.29 | 9.81 ± 1.29 | 11.91 ± 1.85 |
| `mlp` | 4.52 | 4.65 ± 0.21 | 5.03 ± 0.34 | 5.50 ± 0.52 | 6.04 ± 0.62 | 6.87 ± 0.80 | 8.29 ± 0.91 |
| `gp` | 6.27 | 6.50 ± 0.32 | 7.19 ± 0.60 | 7.94 ± 0.93 | 9.08 ± 1.12 | 10.55 ± 1.08 | 12.59 ± 1.39 |

## E. Error by phone and by user

Mean error (m) of the test rows of each phone and user, averaged over seeds (20 for the foundation models, 5 or 1 for the baselines). Every phone and user of the test files also appears in the training files, so this is not a cross-device test. Source: `metrics/e_phone_user.csv`.

### HCXY-All, by phone

| Model | phone 4 (n=120) | phone 5 (n=190) | phone 6 (n=130) | phone 7 (n=130) | phone 8 (n=100) | phone 9 (n=190) |
|---|---|---|---|---|---|---|
| `tabpfn-nan` | 0.88 | 1.54 | 1.26 | 1.47 | 2.47 | 2.88 |
| `tabpfn-ph` | 0.89 | 1.66 | 1.17 | 1.08 | 3.1 | 1.52 |
| `tabicl` | 1.15 | 1.69 | 2.12 | 1.67 | 3.34 | 1.34 |
| `knn` | 0.87 | 1.91 | 1.4 | 2.11 | 2.91 | 1.78 |
| `rf` | 0.87 | 1.77 | 1.14 | 2.46 | 3.72 | 1.72 |
| `lgbm-ph` | 2.19 | 1.8 | 1.41 | 2.82 | 4.23 | 1.61 |
| `lgbm-nan` | 1.85 | 1.84 | 1.34 | 2.6 | 4.24 | 1.57 |
| `svr` | 2.24 | 4.25 | 2.29 | 2.32 | 5.73 | 10.49 |
| `mlp` | 2.56 | 4.05 | 2.47 | 1.86 | 5.18 | 8.79 |
| `gp` | 5.86 | 11.64 | 5.23 | 3.48 | 7.95 | 8.84 |

### HCXY-All, by user

| Model | user 5 (n=120) | user 6 (n=160) | user 7 (n=130) | user 8 (n=280) | user 9 (n=70) | user 10 (n=100) |
|---|---|---|---|---|---|---|
| `tabpfn-nan` | 0.88 | 1.33 | 1.26 | 2.43 | 1.96 | 2.47 |
| `tabpfn-ph` | 0.89 | 1.37 | 1.17 | 1.38 | 1.96 | 3.1 |
| `tabicl` | 1.15 | 1.69 | 2.12 | 1.43 | 1.76 | 3.34 |
| `knn` | 0.87 | 1.75 | 1.4 | 1.98 | 2.02 | 2.91 |
| `rf` | 0.87 | 2.0 | 1.14 | 1.63 | 2.92 | 3.72 |
| `lgbm-ph` | 2.19 | 2.62 | 1.41 | 1.56 | 2.26 | 4.23 |
| `lgbm-nan` | 1.85 | 2.34 | 1.34 | 1.61 | 2.31 | 4.24 |
| `svr` | 2.24 | 4.08 | 2.29 | 7.92 | 3.31 | 5.73 |
| `mlp` | 2.56 | 3.5 | 2.47 | 6.57 | 4.0 | 5.18 |
| `gp` | 5.86 | 10.59 | 5.23 | 7.05 | 9.67 | 7.95 |

### SYL-All, by phone

| Model | phone 1 (n=520) | phone 2 (n=500) |
|---|---|---|
| `tabpfn-nan` | 2.88 | 3.92 |
| `tabpfn-ph` | 2.82 | 3.65 |
| `tabicl` | 2.71 | 3.82 |
| `knn` | 4.19 | 3.99 |
| `rf` | 2.98 | 4.19 |
| `lgbm-ph` | 2.9 | 4.2 |
| `lgbm-nan` | 2.97 | 4.37 |
| `svr` | 6.77 | 7.02 |
| `mlp` | 4.19 | 4.75 |
| `gp` | 5.81 | 6.74 |

### SYL-All, by user

| Model | user 1 (n=280) | user 2 (n=500) | user 3 (n=240) |
|---|---|---|---|
| `tabpfn-nan` | 2.67 | 3.92 | 3.13 |
| `tabpfn-ph` | 2.65 | 3.65 | 3.02 |
| `tabicl` | 2.55 | 3.82 | 2.9 |
| `knn` | 3.55 | 3.99 | 4.93 |
| `rf` | 3.06 | 4.19 | 2.89 |
| `lgbm-ph` | 2.79 | 4.2 | 3.03 |
| `lgbm-nan` | 2.88 | 4.37 | 3.09 |
| `svr` | 6.59 | 7.02 | 6.98 |
| `mlp` | 4.44 | 4.75 | 3.89 |
| `gp` | 4.88 | 6.74 | 6.9 |
