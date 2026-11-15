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
