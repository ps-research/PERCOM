# P1-E01 results: pipeline check and full-survey comparison

Brief: `briefs/P1-E01.md`, revision 1. Report written 2026-11-15T01:37:47Z.

## How this brief was run

- **Machines.** Three molab notebook nodes with the same hardware: NVIDIA RTX PRO 6000 Blackwell Server Edition (96 GB), a 20-core CPU quota, 160 GB RAM, Debian 13 under gVisor, Python 3.13.11. Main packages: `tabpfn` 10.0.0, `tabicl` 2.2.0, `torch` 2.15.0 (CUDA 13.2 build), `scikit-learn` 1.9.1, `lightgbm` 4.7.0, `optuna` 5.0.0, `pandas` 3.1.1, `numpy` 2.4.6. The full package list of the job interpreter is in `env.txt`.
- **Split.** Node A ran HCXY-All, node B SYL-All, node C CETC331, HCXY-AP and SYL-AP. Every node ran the pipeline check itself; all three gave the same table.
- **Order on each node.** First the timed runs of the tabular foundation models, then the Optuna searches, then the timed runs of the baselines. Jobs of `P1-E02` and `P1-E03` started on a node later were stopped (`SIGSTOP`) for the whole of that node's baseline timed runs and resumed afterwards; the pauses are logged in `logs/final_<node>.log`. No other job was running during the timed runs of the foundation models.
- **Warm-up.** Before the first timed run, each foundation model made one untimed fit and predict on 64 rows, so loading the weights from disk and starting CUDA are not counted in any timed run.
- **Threads.** LightGBM 4 threads per model, MLP and GP 4 BLAS threads, `knn` and `rf` 20 jobs in the timed runs, `OMP_WAIT_POLICY=PASSIVE`.
- **Code.** All `P1-E01` runs used commit `1f61e59` of this branch (recorded in every run file).

## Deviations and things to know

1. **Library calls are as written.** TabPFN: `TabPFNRegressor.create_default_for_version(ModelVersion.V2, device="cuda", random_state=seed)`. TabICL: `TabICLRegressor(device="cuda", random_state=seed)` with its default checkpoint `tabicl-regressor-v2-20260212.ckpt`.
2. **TabICLv2 accepted NaN**, so "not detected" was passed as missing and the placeholder fallback was never used. It never ran out of memory and used every training row (peak allocated GPU memory 52.3 GB on HCXY-All).
3. **Search times are not clean.** For part of the search phase the nodes also ran `P1-E02` jobs; on node C three LightGBM searches overlapped with heavy parallel load and took 2,400 to 3,000 s. Searches are deterministic, so the best values are unaffected, but `search_seconds` in `config/search_runs.json` overstate the cost of tuning and should be read as upper bounds.
4. **Two environment reports.** `env_node*.txt` were written from inside the notebook kernel when the run started; the kernel had loaded `torch` 2.11 before `tabpfn` was installed, which upgraded it on disk to 2.15. The jobs ran in fresh interpreters and used 2.15.0; `env.txt` is the report of that job interpreter.
5. **What "fit" means for a foundation model.** No weights change: fit time is preprocessing and building the context; predict time is inference on the test file. Both coordinates are included.
6. **Total wall-clock time** from the pipeline check to the last timed run: 1 h 43 min (2026-11-14T23:50:16Z to 2026-11-15T01:33:24Z, three nodes in parallel).
7. No stop condition was triggered.

## 1. Pipeline check (Part A, the gate)

Dataset commit `bfe8f63f55957cc25b23ba91c408ae345a3fb0b7`. All counts of the brief's data table match (`metrics/e0_counts.csv`).

kNN as in the brief: `KNeighborsRegressor(n_neighbors=5, weights='distance', metric='euclidean')`, both coordinates as targets.

| Config | Not detected | Mean | Paper mean | Diff | 50th | Paper 50th | 75th | Paper 75th | 95th | Paper 95th | MAE per coord. | Mean within 0.05 m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CETC331 | left as 100 | 4.754 | 2.876 | 1.878 | 3.870 | 2.316 | 6.293 | 3.803 | 11.824 | 6.307 | 2.821 | False |
| CETC331 | placeholder -105 | 2.868 | 2.876 | -0.008 | 2.315 | 2.316 | 3.804 | 3.803 | 6.306 | 6.307 | 1.725 | True |
| HCXY-All | left as 100 | 3.018 | 2.365 | 0.653 | 2.075 | 1.470 | 3.745 | 3.231 | 9.070 | 6.627 | 1.808 | False |
| HCXY-All | placeholder -105 | 2.366 | 2.365 | 0.001 | 1.461 | 1.470 | 3.230 | 3.231 | 6.627 | 6.627 | 1.403 | True |
| SYL-All | left as 100 | 5.180 | 4.656 | 0.524 | 4.686 | 3.842 | 6.605 | 6.078 | 10.824 | 8.521 | 3.123 | False |
| SYL-All | placeholder -105 | 4.656 | 4.656 | 0.000 | 3.818 | 3.842 | 6.107 | 6.078 | 8.485 | 8.521 | 2.817 | True |

**The gate passes** with "not detected" written as **placeholder -105**: the mean positioning error is within 0.05 m of the dataset paper in all three configurations. All values are in metres. Full comparison: `metrics/e0_check.csv`.

## 2. Full-survey comparison (Part B)

190 runs: seeds 0 to 4 for the models with randomness, one run for `knn`, `svr` and `gp`. Entries are mean ± standard deviation over seeds, in metres. Per-run numbers: `metrics/e1_summary.csv`.

### CETC331

955 training rows, 955 reference points, 52 RSS columns, 840 test rows at 84 test points.

| Model | Group | Runs | Mean (m) | Median (m) | 75th (m) | 95th (m) | RMS (m) |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | TFM | 5 | 2.682 ± 0.023 | 2.139 ± 0.038 | 3.308 ± 0.067 | 6.462 ± 0.107 | 3.793 ± 0.035 |
| `tabpfn-ph` | TFM | 5 | 2.693 ± 0.022 | 2.061 ± 0.017 | 3.477 ± 0.098 | 6.540 ± 0.099 | 3.782 ± 0.021 |
| `tabicl` | TFM | 5 | 2.596 ± 0.022 | 2.063 ± 0.051 | 3.290 ± 0.071 | 5.698 ± 0.110 | 3.634 ± 0.019 |
| `knn` | baseline | 1 | 2.910 | 2.319 | 3.834 | 6.717 | 4.030 |
| `rf` | baseline | 5 | 3.515 ± 0.031 | 2.445 ± 0.039 | 3.918 ± 0.050 | 9.787 ± 0.313 | 5.148 ± 0.097 |
| `lgbm-ph` | baseline | 5 | 3.338 ± 0.035 | 2.414 ± 0.070 | 3.674 ± 0.049 | 9.399 ± 0.455 | 4.903 ± 0.118 |
| `lgbm-nan` | baseline | 5 | 3.441 ± 0.042 | 2.425 ± 0.042 | 3.827 ± 0.132 | 9.800 ± 0.238 | 5.095 ± 0.106 |
| `svr` | baseline | 1 | 3.638 | 2.868 | 4.497 | 9.587 | 4.866 |
| `mlp` | baseline | 5 | 3.363 ± 0.152 | 2.806 ± 0.179 | 4.125 ± 0.301 | 7.843 ± 0.456 | 4.377 ± 0.110 |
| `gp` | baseline | 1 | 3.064 | 2.477 | 3.999 | 7.471 | 4.212 |

### HCXY-All

11,370 training rows, 379 reference points, 347 RSS columns, 860 test rows at 86 test points.

| Model | Group | Runs | Mean (m) | Median (m) | 75th (m) | 95th (m) | RMS (m) |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | TFM | 5 | 1.835 ± 0.297 | 1.366 ± 0.159 | 2.340 ± 0.288 | 5.361 ± 2.189 | 2.459 ± 0.527 |
| `tabpfn-ph` | TFM | 5 | 1.558 ± 0.072 | 1.163 ± 0.103 | 1.970 ± 0.072 | 3.994 ± 0.261 | 2.174 ± 0.080 |
| `tabicl` | TFM | 5 | 1.781 ± 0.054 | 1.309 ± 0.039 | 2.279 ± 0.087 | 4.182 ± 0.153 | 2.569 ± 0.140 |
| `knn` | baseline | 1 | 1.805 | 1.275 | 2.391 | 5.786 | 2.444 |
| `rf` | baseline | 5 | 1.869 ± 0.018 | 1.234 ± 0.026 | 2.249 ± 0.066 | 5.007 ± 0.164 | 2.801 ± 0.064 |
| `lgbm-ph` | baseline | 5 | 2.189 ± 0.056 | 1.427 ± 0.057 | 2.331 ± 0.153 | 6.173 ± 0.817 | 3.824 ± 0.253 |
| `lgbm-nan` | baseline | 5 | 2.100 ± 0.045 | 1.394 ± 0.056 | 2.159 ± 0.097 | 6.353 ± 0.663 | 3.402 ± 0.184 |
| `svr` | baseline | 1 | 4.931 | 3.180 | 7.079 | 13.782 | 6.585 |
| `mlp` | baseline | 5 | 4.450 ± 0.984 | 2.989 ± 0.289 | 5.439 ± 0.916 | 14.291 ± 5.618 | 6.204 ± 1.727 |
| `gp` | baseline | 1 | 7.585 | 5.505 | 9.384 | 23.884 | 9.898 |

### HCXY-AP

11,370 training rows, 379 reference points, 56 RSS columns, 860 test rows at 86 test points.

| Model | Group | Runs | Mean (m) | Median (m) | 75th (m) | 95th (m) | RMS (m) |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | TFM | 5 | 2.704 ± 0.360 | 1.769 ± 0.105 | 3.235 ± 0.251 | 9.915 ± 3.543 | 3.927 ± 0.701 |
| `tabpfn-ph` | TFM | 5 | 3.414 ± 0.667 | 1.939 ± 0.137 | 3.850 ± 0.625 | 12.056 ± 3.533 | 5.165 ± 1.149 |
| `tabicl` | TFM | 5 | 2.827 ± 0.029 | 1.972 ± 0.075 | 3.468 ± 0.082 | 9.317 ± 0.501 | 4.112 ± 0.035 |
| `knn` | baseline | 1 | 2.658 | 2.032 | 3.484 | 7.048 | 3.444 |
| `rf` | baseline | 5 | 2.465 ± 0.014 | 1.796 ± 0.111 | 3.035 ± 0.107 | 6.021 ± 0.142 | 3.444 ± 0.029 |
| `lgbm-ph` | baseline | 5 | 2.796 ± 0.022 | 2.104 ± 0.018 | 3.599 ± 0.137 | 8.308 ± 0.488 | 3.786 ± 0.057 |
| `lgbm-nan` | baseline | 5 | 2.802 ± 0.028 | 2.135 ± 0.068 | 3.635 ± 0.090 | 8.366 ± 0.768 | 3.760 ± 0.062 |
| `svr` | baseline | 1 | 9.330 | 4.542 | 9.610 | 41.255 | 15.162 |
| `mlp` | baseline | 5 | 8.203 ± 0.446 | 3.700 ± 0.324 | 9.355 ± 1.280 | 35.007 ± 3.210 | 13.109 ± 0.947 |
| `gp` | baseline | 1 | 9.327 | 5.032 | 12.370 | 34.608 | 13.567 |

### SYL-All

8,880 training rows, 296 reference points, 363 RSS columns, 1,020 test rows at 102 test points.

| Model | Group | Runs | Mean (m) | Median (m) | 75th (m) | 95th (m) | RMS (m) |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | TFM | 5 | 3.404 ± 0.073 | 2.758 ± 0.121 | 3.910 ± 0.146 | 7.054 ± 0.262 | 5.972 ± 0.039 |
| `tabpfn-ph` | TFM | 5 | 3.217 ± 0.054 | 2.493 ± 0.118 | 3.553 ± 0.103 | 6.784 ± 0.173 | 5.874 ± 0.028 |
| `tabicl` | TFM | 5 | 3.258 ± 0.021 | 2.737 ± 0.070 | 3.759 ± 0.142 | 5.956 ± 0.259 | 5.815 ± 0.006 |
| `knn` | baseline | 1 | 4.091 | 3.407 | 5.400 | 7.678 | 6.523 |
| `rf` | baseline | 5 | 3.574 ± 0.033 | 2.898 ± 0.044 | 3.857 ± 0.137 | 7.917 ± 0.123 | 6.112 ± 0.032 |
| `lgbm-ph` | baseline | 5 | 3.535 ± 0.058 | 2.551 ± 0.048 | 3.923 ± 0.104 | 8.048 ± 0.347 | 6.086 ± 0.053 |
| `lgbm-nan` | baseline | 5 | 3.660 ± 0.070 | 2.819 ± 0.067 | 3.939 ± 0.049 | 7.741 ± 0.181 | 6.116 ± 0.060 |
| `svr` | baseline | 1 | 6.892 | 5.033 | 7.642 | 22.680 | 9.600 |
| `mlp` | baseline | 5 | 4.461 ± 0.399 | 3.454 ± 0.250 | 5.306 ± 0.482 | 9.107 ± 1.158 | 6.935 ± 0.431 |
| `gp` | baseline | 1 | 6.268 | 4.488 | 7.136 | 21.994 | 9.159 |

### SYL-AP

8,880 training rows, 296 reference points, 46 RSS columns, 1,020 test rows at 102 test points.

| Model | Group | Runs | Mean (m) | Median (m) | 75th (m) | 95th (m) | RMS (m) |
|---|---|---|---|---|---|---|---|
| `tabpfn-nan` | TFM | 5 | 3.428 ± 0.054 | 2.639 ± 0.066 | 3.946 ± 0.071 | 7.361 ± 0.233 | 6.000 ± 0.039 |
| `tabpfn-ph` | TFM | 5 | 3.305 ± 0.030 | 2.632 ± 0.102 | 3.848 ± 0.089 | 6.417 ± 0.321 | 5.945 ± 0.025 |
| `tabicl` | TFM | 5 | 3.492 ± 0.053 | 2.544 ± 0.149 | 3.995 ± 0.127 | 7.188 ± 0.165 | 6.001 ± 0.033 |
| `knn` | baseline | 1 | 4.332 | 3.499 | 5.367 | 8.905 | 6.728 |
| `rf` | baseline | 5 | 3.434 ± 0.018 | 2.679 ± 0.061 | 3.840 ± 0.080 | 7.289 ± 0.090 | 6.040 ± 0.026 |
| `lgbm-ph` | baseline | 5 | 3.622 ± 0.038 | 2.715 ± 0.081 | 4.195 ± 0.109 | 8.034 ± 0.576 | 6.155 ± 0.034 |
| `lgbm-nan` | baseline | 5 | 3.668 ± 0.009 | 2.838 ± 0.089 | 4.069 ± 0.080 | 8.346 ± 0.369 | 6.176 ± 0.018 |
| `svr` | baseline | 1 | 4.348 | 3.274 | 5.360 | 10.346 | 6.762 |
| `mlp` | baseline | 5 | 4.438 ± 0.124 | 3.684 ± 0.182 | 5.328 ± 0.246 | 10.260 ± 0.648 | 6.834 ± 0.084 |
| `gp` | baseline | 1 | 4.671 | 3.599 | 5.774 | 10.049 | 6.879 |

## 3. Best tabular foundation model against best baseline

Per configuration: the tabular foundation model and the baseline with the lowest mean error averaged over seeds. The difference uses seed 0 of each, with a 95% bootstrap interval from 10,000 resamples of test points; a resampled test point brings all 10 of its rows. Negative means the tabular foundation model is better. Source: `metrics/e1_bootstrap.csv`.

| Config | Best TFM | Best baseline | TFM mean, seed 0 (m) | Baseline mean, seed 0 (m) | Difference (m) | 95% interval (m) |
|---|---|---|---|---|---|---|
| CETC331 | `tabicl` | `knn` | 2.601 | 2.910 | -0.309 | [-0.587, -0.035] |
| HCXY-All | `tabpfn-ph` | `knn` | 1.461 | 1.805 | -0.344 | [-0.665, -0.019] |
| HCXY-AP | `tabpfn-nan` | `rf` | 2.625 | 2.476 | +0.149 | [-0.427, +0.748] |
| SYL-All | `tabpfn-ph` | `lgbm-ph` | 3.306 | 3.598 | -0.292 | [-0.564, -0.036] |
| SYL-AP | `tabpfn-ph` | `rf` | 3.293 | 3.439 | -0.146 | [-0.436, +0.131] |

## 4. Cost

Wall-clock seconds to fit and to predict the test file, and peak GPU memory (`torch.cuda.max_memory_allocated`), averaged over seeds. Fitting covers both coordinates. Search time of the tuned baselines is not included here; it is in `config/search_runs.json`.

| Config | Model | Runs | Fit (s) | Predict (s) | Peak GPU memory (MB) |
|---|---|---|---|---|---|
| CETC331 | `tabpfn-nan` | 5 | 2.23 | 0.51 | 600 |
| CETC331 | `tabpfn-ph` | 5 | 2.16 | 0.50 | 600 |
| CETC331 | `tabicl` | 5 | 1.03 | 0.47 | 2255 |
| CETC331 | `knn` | 1 | 0.00 | 0.12 | n/a |
| CETC331 | `rf` | 5 | 0.46 | 0.13 | n/a |
| CETC331 | `lgbm-ph` | 5 | 24.71 | 0.08 | n/a |
| CETC331 | `lgbm-nan` | 5 | 30.65 | 0.12 | n/a |
| CETC331 | `svr` | 1 | 0.15 | 0.06 | n/a |
| CETC331 | `mlp` | 5 | 0.82 | 0.01 | n/a |
| CETC331 | `gp` | 1 | 12.91 | 0.04 | n/a |
| HCXY-All | `tabpfn-nan` | 5 | 18.49 | 18.86 | 8861 |
| HCXY-All | `tabpfn-ph` | 5 | 20.67 | 18.82 | 8861 |
| HCXY-All | `tabicl` | 5 | 5.66 | 7.49 | 53572 |
| HCXY-All | `knn` | 1 | 0.03 | 0.28 | n/a |
| HCXY-All | `rf` | 5 | 1.14 | 0.13 | n/a |
| HCXY-All | `lgbm-ph` | 5 | 25.88 | 0.05 | n/a |
| HCXY-All | `lgbm-nan` | 5 | 27.85 | 0.05 | n/a |
| HCXY-All | `svr` | 1 | 86.37 | 2.30 | n/a |
| HCXY-All | `mlp` | 5 | 4.73 | 0.01 | n/a |
| HCXY-All | `gp` | 1 | 4.13 | 0.10 | n/a |
| HCXY-AP | `tabpfn-nan` | 5 | 5.42 | 5.15 | 3189 |
| HCXY-AP | `tabpfn-ph` | 5 | 4.77 | 5.14 | 3189 |
| HCXY-AP | `tabicl` | 5 | 1.41 | 1.81 | 9570 |
| HCXY-AP | `knn` | 1 | 0.00 | 0.03 | n/a |
| HCXY-AP | `rf` | 5 | 0.53 | 0.11 | n/a |
| HCXY-AP | `lgbm-ph` | 5 | 15.95 | 0.03 | n/a |
| HCXY-AP | `lgbm-nan` | 5 | 20.35 | 0.06 | n/a |
| HCXY-AP | `svr` | 1 | 17.95 | 0.47 | n/a |
| HCXY-AP | `mlp` | 5 | 7.41 | 0.01 | n/a |
| HCXY-AP | `gp` | 1 | 1.71 | 0.02 | n/a |
| SYL-All | `tabpfn-nan` | 5 | 13.18 | 14.47 | 6839 |
| SYL-All | `tabpfn-ph` | 5 | 14.11 | 14.41 | 6839 |
| SYL-All | `tabicl` | 5 | 4.04 | 5.27 | 33690 |
| SYL-All | `knn` | 1 | 0.03 | 0.25 | n/a |
| SYL-All | `rf` | 5 | 0.63 | 0.14 | n/a |
| SYL-All | `lgbm-ph` | 5 | 53.77 | 0.11 | n/a |
| SYL-All | `lgbm-nan` | 5 | 41.88 | 0.12 | n/a |
| SYL-All | `svr` | 1 | 5.23 | 0.89 | n/a |
| SYL-All | `mlp` | 5 | 3.85 | 0.01 | n/a |
| SYL-All | `gp` | 1 | 2.00 | 0.10 | n/a |
| SYL-AP | `tabpfn-nan` | 5 | 5.76 | 3.78 | 2452 |
| SYL-AP | `tabpfn-ph` | 5 | 3.93 | 3.77 | 2452 |
| SYL-AP | `tabicl` | 5 | 1.14 | 1.21 | 6393 |
| SYL-AP | `knn` | 1 | 0.00 | 0.02 | n/a |
| SYL-AP | `rf` | 5 | 0.52 | 0.11 | n/a |
| SYL-AP | `lgbm-ph` | 5 | 17.74 | 0.05 | n/a |
| SYL-AP | `lgbm-nan` | 5 | 36.66 | 0.13 | n/a |
| SYL-AP | `svr` | 1 | 2.93 | 0.27 | n/a |
| SYL-AP | `mlp` | 5 | 4.91 | 0.01 | n/a |
| SYL-AP | `gp` | 1 | 1.00 | 0.02 | n/a |

Search time of the tuned baselines (30 trials, 3 folds each):

| Config | Baseline | Trials | Search (s) | Best CV mean error (m) |
|---|---|---|---|---|
| CETC331 | `knn` | 30 | 5 | 1.035 |
| CETC331 | `lgbm-nan` | 30 | 1954 | 1.285 |
| CETC331 | `lgbm-ph` | 30 | 2578 | 1.271 |
| CETC331 | `mlp` | 30 | 63 | 1.631 |
| CETC331 | `rf` | 30 | 35 | 1.443 |
| CETC331 | `svr` | 30 | 7 | 1.414 |
| HCXY-AP | `knn` | 30 | 9 | 2.548 |
| HCXY-AP | `lgbm-nan` | 30 | 1823 | 2.529 |
| HCXY-AP | `lgbm-ph` | 30 | 2410 | 2.489 |
| HCXY-AP | `mlp` | 30 | 232 | 2.765 |
| HCXY-AP | `rf` | 30 | 97 | 2.384 |
| HCXY-AP | `svr` | 30 | 270 | 3.046 |
| HCXY-All | `knn` | 30 | 29 | 1.744 |
| HCXY-All | `lgbm-nan` | 30 | 2252 | 1.719 |
| HCXY-All | `lgbm-ph` | 30 | 2458 | 1.805 |
| HCXY-All | `mlp` | 30 | 283 | 3.079 |
| HCXY-All | `rf` | 30 | 331 | 1.712 |
| HCXY-All | `svr` | 30 | 1264 | 3.531 |
| SYL-AP | `knn` | 30 | 6 | 2.386 |
| SYL-AP | `lgbm-nan` | 30 | 1818 | 2.068 |
| SYL-AP | `lgbm-ph` | 30 | 2961 | 2.084 |
| SYL-AP | `mlp` | 30 | 155 | 2.537 |
| SYL-AP | `rf` | 30 | 67 | 2.021 |
| SYL-AP | `svr` | 30 | 57 | 2.702 |
| SYL-All | `knn` | 30 | 19 | 1.939 |
| SYL-All | `lgbm-nan` | 30 | 2760 | 1.884 |
| SYL-All | `lgbm-ph` | 30 | 3154 | 1.860 |
| SYL-All | `mlp` | 30 | 172 | 2.663 |
| SYL-All | `rf` | 30 | 131 | 1.852 |
| SYL-All | `svr` | 30 | 150 | 3.257 |

## 5. Test points that share their location with a reference point

| Config | Test points | Shared (ECoord, NCoord, FloorID) | Shared (ECoord, NCoord) |
|---|---|---|---|
| CETC331 | 84 | 84 | 84 |
| HCXY-All | 86 | 0 | 0 |
| HCXY-AP | 86 | 0 | 0 |
| SYL-All | 102 | 1 | 1 |
| SYL-AP | 102 | 1 | 1 |

## 6. Tabular foundation models: weights, context and missing values

| Config | Model | Not detected as | Context rows | Context capped | Weights |
|---|---|---|---|---|---|
| CETC331 | `tabicl` | missing | 955 | False | tabicl-regressor-v2-20260212.ckpt |
| CETC331 | `tabpfn-nan` | missing | 955 | False | tabpfn-v2-regressor.ckpt |
| CETC331 | `tabpfn-ph` | placeholder | 955 | False | tabpfn-v2-regressor.ckpt |
| HCXY-AP | `tabicl` | missing | 11370 | False | tabicl-regressor-v2-20260212.ckpt |
| HCXY-AP | `tabpfn-nan` | missing | 9854 | True | tabpfn-v2-regressor.ckpt |
| HCXY-AP | `tabpfn-ph` | placeholder | 9854 | True | tabpfn-v2-regressor.ckpt |
| HCXY-All | `tabicl` | missing | 11370 | False | tabicl-regressor-v2-20260212.ckpt |
| HCXY-All | `tabpfn-nan` | missing | 9854 | True | tabpfn-v2-regressor.ckpt |
| HCXY-All | `tabpfn-ph` | placeholder | 9854 | True | tabpfn-v2-regressor.ckpt |
| SYL-AP | `tabicl` | missing | 8880 | False | tabicl-regressor-v2-20260212.ckpt |
| SYL-AP | `tabpfn-nan` | missing | 8880 | False | tabpfn-v2-regressor.ckpt |
| SYL-AP | `tabpfn-ph` | placeholder | 8880 | False | tabpfn-v2-regressor.ckpt |
| SYL-All | `tabicl` | missing | 8880 | False | tabicl-regressor-v2-20260212.ckpt |
| SYL-All | `tabpfn-nan` | missing | 8880 | False | tabpfn-v2-regressor.ckpt |
| SYL-All | `tabpfn-ph` | placeholder | 8880 | False | tabpfn-v2-regressor.ckpt |
