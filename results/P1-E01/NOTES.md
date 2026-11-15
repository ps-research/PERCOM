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
