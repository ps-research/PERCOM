"""Cells of the marimo notebook that runs P1-E01 on one compute node.

Each node runs the same notebook for its own share of the configurations.
``cells(...)`` returns the cell sources in order; ``push.py`` sends them to the
node's live notebook. The notebook stays thin: it imports ``p1`` from the cloned
repository, looks at the data, runs the gate, launches Part B as one background
job and plots that job's progress from its log.
"""
from __future__ import annotations

DATASET_COMMIT = "bfe8f63f55957cc25b23ba91c408ae345a3fb0b7"
PACKAGES = ["tabpfn==10.0.0", "tabicl==2.2.0", "scikit-learn", "lightgbm", "optuna", "numpy", "pandas", "torch",
            "matplotlib", "threadpoolctl", "joblib"]


def cells(node: str, configs: list[str], commit: str, workers: int, threads: int,
          branch: str = "exp/P1-E01") -> list[dict]:
    C = []

    def cell(name, code, hide=False, run=True):
        C.append(dict(name=name, code=code.strip("\n") + "\n", hide=hide, run=run))

    cell("intro", f'''
mo.md(
    r"""
# P1-E01: can a tabular foundation model localize from Wi-Fi fingerprints without training?

**Goal.** With the full survey of a building as context, does an off-the-shelf tabular foundation model
(TabPFN v2, TabICLv2) localize as well as tuned classical methods, and what does it cost in time and memory?
This notebook runs brief `briefs/P1-E01.md` of the repository `ps-research/PERCOM` for the
configuration(s) **{", ".join(configs)}** of the SODIndoorLoc dataset.

**Method.**

1. *Pipeline check (the gate).* Re-create the untuned kNN result of the dataset paper. Nothing else runs
   unless the mean error is within 0.05 m of the paper in all three buildings.
2. *Tuned baselines.* kNN, random forest, LightGBM (with two ways of writing "not detected"), SVR and an MLP
   are tuned with Optuna (TPE, 30 trials, 3-fold GroupKFold with the reference point as the group).
   A Gaussian process is tuned by its own marginal likelihood.
3. *Tabular foundation models.* TabPFN v2 and TabICLv2 receive the surveyed fingerprints as context and
   predict the two coordinates, with default settings and no tuning.
4. *Comparison.* Every model predicts the same test file. The error of a test row is the Euclidean distance
   in metres between the predicted and the true position.

The code is in `code/p1/` of the repository and is imported below. The searches and the fit-and-predict runs
use that same code as one background job; its progress is plotted further down from the job's log.
"""
)
''')

    cell("imports", '''
import os
import sys
import time
from pathlib import Path

import pandas as pd
''')

    cell("workspace", f'''
REPO_URL = "https://github.com/ps-research/PERCOM"
BRANCH = "{branch}"
COMMIT = "{commit}"
DATASET_URL = "https://github.com/bijingxue/SODIndoorLoc"
DATASET_COMMIT = "{DATASET_COMMIT}"
NODE = "{node}"
CONFIGS = {configs!r}

WORK = Path("/tmp/percom")
REPO = WORK / "PERCOM"
DATA = REPO / "data" / "SODIndoorLoc"
OUT = WORK / "out" / "P1-E01"
WORK.mkdir(parents=True, exist_ok=True)
if not (REPO / ".git").exists():
    run(f"git clone --quiet --branch {{BRANCH}} {{REPO_URL}} {{REPO}}", cwd=str(WORK), timeout=55, check=True)
run(f"git fetch --quiet origin {{BRANCH}} && git checkout --quiet {{COMMIT}}", cwd=str(REPO), timeout=55, check=True)
if not (DATA / ".git").exists():
    run(f"git clone --quiet {{DATASET_URL}} {{DATA}}", cwd=str(WORK), timeout=55, check=True)
run(f"git checkout --quiet {{DATASET_COMMIT}}", cwd=str(DATA), check=True)

_run_id_file = WORK / "RUN_ID"
if not _run_id_file.exists():
    _run_id_file.write_text(
        f"{{os.environ.get('CW_SANDBOX_ID', 'nb')[:8]}}-{{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}}"
    )
RUN_ID = _run_id_file.read_text().strip()
DRIVE_RUN = f"molab/PERCOM/runs/{{RUN_ID}}"
OUT.mkdir(parents=True, exist_ok=True)
os.environ["P1_NODE"] = NODE
if str(REPO / "code") not in sys.path:
    sys.path.insert(0, str(REPO / "code"))
mo.md(
    f"**Workspace.** Repository at commit `{{COMMIT[:10]}}` in `{{REPO}}`, dataset at commit "
    f"`{{DATASET_COMMIT[:10]}}`. Run id **{{RUN_ID}}**; results are checkpointed to Drive under `{{DRIVE_RUN}}/`."
)
''')

    cell("project", '''
import p1.data as p1data
import p1.e1 as p1e1
import p1.nb as p1nb
from p1.assets import write_assets
from p1.common import env_report

PROJECT_CODE = REPO / "code" / "p1"  # the workspace cell above put the repository on sys.path
''')

    cell("environment", '''
env_text = env_report(DATA)
(OUT / f"env_{NODE}.txt").write_text(env_text)
mo.md("### Environment\\n```\\n" + env_text.split("## pip freeze")[0].strip() + "\\n```")
''')

    cell("data", '''
counts = p1data.count_table(DATA)
surveys = {_c: p1data.load_config(_c, DATA) for _c in CONFIGS}
_first = surveys[CONFIGS[0]]
mo.vstack(
    [
        mo.md(
            "### The data: SODIndoorLoc\\n"
            f"Every count of the brief's data table matches the files: **{bool(counts['ok'].all())}**. "
            "Each row is one Wi-Fi scan: one column per access point (signal strength in dBm, 100 = not detected) "
            "and the position where it was taken."
        ),
        counts.pivot(index="config", columns="quantity", values="found").reset_index(),
        p1nb.survey_figure(surveys),
        mo.md(f"First training rows of {CONFIGS[0]} (first eight access points and the two targets):"),
        pd.DataFrame(_first.X_train[:5, :8], columns=_first.mac_cols[:8]).assign(
            ECoord=_first.y_train[:5, 0], NCoord=_first.y_train[:5, 1]
        ),
    ]
)
''')

    cell("gate", '''
gate_result = p1e1.gate(str(DATA), OUT)
gate_table = pd.read_csv(OUT / "metrics" / "e0_check.csv")
mo.vstack(
    [
        mo.md(
            "### Part A. Pipeline check (the gate)\\n"
            "kNN with k = 5, distance weights and Euclidean distance, against the dataset paper. Values in metres.\\n\\n"
            f"Gate passed: **{gate_result['gate_passed']}**, with \\"not detected\\" written as "
            f"**{', '.join(gate_result.get('passed_with', [])) or 'neither way'}**."
        ),
        gate_table[
            ["config", "not_detected", "mean_m", "paper_mean_m", "diff_mean_m", "p50_m", "paper_p50_m", "p95_m",
             "paper_p95_m", "mean_within_tolerance"]
        ].round(3),
    ]
)
''')

    cell("weights", '''
assets = write_assets(OUT, str(DATA))
mo.md(
    "### Model weights\\n"
    f"- TabPFN v2: `{assets['tabpfn']['file']}` from `{assets['tabpfn']['repo']}`, gated: "
    f"{assets['tabpfn']['gated']}, licence: {assets['tabpfn']['licence']}\\n"
    f"- TabICLv2: `{assets['tabicl']['file']}` from `{assets['tabicl']['repo']}`, gated: "
    f"{assets['tabicl']['gated']}, licence: {assets['tabicl']['licence']}, allowed by the brief "
    f"(BSD, MIT or Apache): **{assets['tabicl']['licence_allowed']}**\\n\\n"
    "Both were downloaded without a token, an account or a licence prompt. SHA-256 sums are in `assets.md`."
)
''')

    cell("launch", f'''
PARTB_CMD = (
    f"{{sys.executable}} -m p1.e1 partb --out {{OUT}} --data {{DATA}} --configs {{' '.join(CONFIGS)}} "
    "--workers {workers} --threads {threads}"
)
if not assets["tabicl"]["licence_allowed"]:
    # Stop condition of the brief: drop tabicl, finish the rest, and report.
    PARTB_CMD += " --models knn rf lgbm-ph lgbm-nan svr mlp gp tabpfn-nan tabpfn-ph"
if not gate_result["gate_passed"]:
    partb_job = None  # the gate did not pass: nothing is launched
elif p1nb.job_alive("p1.e1 partb"):
    partb_job = {{"tag": "p1e01_partb", "log": "/tmp/p1e01_partb.log", "done": "/tmp/p1e01_partb.done"}}
else:
    partb_job = bg_run(p1nb.job_script(PARTB_CMD, REPO, NODE), tag="p1e01_partb")
mo.md(
    "### Part B. Full-survey comparison\\n"
    "One background job runs the Optuna searches of the tuned baselines, then fits every model and predicts "
    "the test file, one run after the other so that the timings are clean. Finished units are skipped when "
    f"the job is started again.\\n\\n`{{PARTB_CMD}}`"
)
''')

    cell("refresh", '''
progress_refresh = mo.ui.refresh(options=["30s", "1m", "5m"], default_interval="1m", label="Refresh progress")
progress_refresh
''')

    cell("search_progress", '''
progress_refresh
search_trials = p1nb.search_trials(OUT)
mo.vstack(
    [
        mo.md("#### Baseline search: best cross-validated error so far (read from the job's log)"),
        p1nb.search_figure(search_trials),
        p1nb.search_status(OUT, CONFIGS),
        mo.md("```\\n" + p1nb.tail(OUT / "logs" / f"search_{NODE}.log", 5) + "\\n```"),
    ]
)
''')

    cell("runs_progress", '''
progress_refresh
runs = p1nb.finished_runs(OUT)
mo.vstack(
    [
        mo.md(
            f"#### Fit-and-predict runs finished: {len(runs)} of {p1nb.runs_expected(CONFIGS)} "
            "(mean positioning error on the test file)"
        ),
        p1nb.runs_figure(runs),
        p1nb.runs_table(runs),
        mo.md("```\\n" + p1nb.tail(OUT / "logs" / f"final_{NODE}.log", 5) + "\\n```"),
    ]
)
''')

    cell("checkpoint", '''
checkpoint = dput_tar(str(OUT), f"{DRIVE_RUN}/P1-E01.tar.gz")
mo.md(f"Results folder checkpointed to Drive: `{checkpoint}` at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}.")
''', run=False)
    return C
