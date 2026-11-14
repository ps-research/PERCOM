"""Tables and plots used by the notebook that runs a brief on a compute node.

The notebook cells import this module and the rest of ``p1``; the long jobs it
launches run the same code (``python -m p1.e1 ...``).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from . import data as D
from .common import read_json
from .models import ALL_MODELS, SEEDED, TFMS, TUNED


# ----------------------------------------------------------------------------- jobs
def job_script(command: str, repo: str | Path, node: str) -> str:
    """Python source that runs one ``python -m p1...`` command from the repository's code folder."""
    code_dir = str(Path(repo) / "code")
    return (
        "import os, shlex, subprocess, sys\n"
        f"env = dict(os.environ, PYTHONPATH={code_dir!r}, P1_NODE={node!r}, PYTHONUNBUFFERED='1', OMP_WAIT_POLICY='PASSIVE')\n"
        f"print('command:', {command!r}, flush=True)\n"
        f"rc = subprocess.run(shlex.split({command!r}), cwd={str(repo)!r}, env=env).returncode\n"
        "print('exit code:', rc, flush=True)\n"
        "sys.exit(rc)\n"
    )


def job_alive(pattern: str) -> bool:
    """True if a process whose command line contains ``pattern`` is running."""
    out = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True).stdout.split()
    return len(out) > 0


def tail(path: str | Path, n: int = 12) -> str:
    path = Path(path)
    if not path.exists():
        return "(no log yet)"
    return "\n".join(path.read_text(errors="replace").splitlines()[-n:])


# ----------------------------------------------------------------------------- data
def survey_figure(surveys: dict[str, D.Survey]):
    """Where the reference points and test points are, and how often an access point is heard."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, len(surveys), figsize=(4.6 * len(surveys), 6.4), squeeze=False)
    for j, (name, s) in enumerate(surveys.items()):
        ax = axes[0, j]
        ax.scatter(s.rp_table["ECoord"], s.rp_table["NCoord"], s=6, c="#b0b0b0", label=f"{s.n_ref_points} reference points")
        ax.scatter(s.tp_table["ECoord"], s.tp_table["NCoord"], s=14, c="#d62728", marker="x", label=f"{s.n_test_points} test points")
        ax.set_title(f"{name}: survey layout")
        ax.set_xlabel("ECoord (m)")
        ax.set_ylabel("NCoord (m)")
        ax.set_aspect("equal", adjustable="datalim")
        ax.legend(fontsize=7, loc="best")
        ax = axes[1, j]
        detected = s.X_train != D.NOT_DETECTED
        ax.hist(s.X_train[detected], bins=40, color="#1f77b4")
        ax.set_title(f"{name}: detected signal strengths ({detected.mean():.0%} of cells detected)", fontsize=9)
        ax.set_xlabel("RSS (dBm)")
        ax.set_ylabel("count")
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------------- search progress
_TRIAL = re.compile(r"^(\S+) trial\s+(\d+) value=([0-9.eE+-]+)")


def search_trials(out: str | Path) -> pd.DataFrame:
    """One row per finished trial, parsed from the search logs of the running job."""
    rows = []
    for path in sorted((Path(out) / "logs" / "search").glob("*.log")):
        config, model = path.stem.split("__")
        for line in path.read_text(errors="replace").splitlines():
            m = _TRIAL.match(line)
            if m:
                rows.append(dict(config=config, model=model, trial=int(m.group(2)), value=float(m.group(3)), time=m.group(1)))
    df = pd.DataFrame(rows, columns=["config", "model", "trial", "value", "time"])
    if len(df):
        df["best_so_far"] = df.groupby(["config", "model"])["value"].cummin()
    return df


def search_status(out: str | Path, configs: list[str], n_trials: int = 30) -> pd.DataFrame:
    trials = search_trials(out)
    rows = []
    for c in configs:
        for m in TUNED:
            g = trials[(trials["config"] == c) & (trials["model"] == m)]
            done = (Path(out) / "config" / "best_params" / f"{c}__{m}.json").exists()
            rows.append(dict(config=c, model=m, trials_done=len(g), of=n_trials, finished=done,
                             best_cv_error_m=round(float(g["value"].min()), 3) if len(g) else np.nan))
    return pd.DataFrame(rows)


def search_done(out: str | Path, configs: list[str]) -> bool:
    return all((Path(out) / "config" / "best_params" / f"{c}__{m}.json").exists() for c in configs for m in TUNED)


def search_figure(trials: pd.DataFrame):
    """Best cross-validated error so far against trial number, one line per baseline."""
    import matplotlib.pyplot as plt

    configs = list(dict.fromkeys(trials["config"])) or ["(no trials yet)"]
    fig, axes = plt.subplots(1, len(configs), figsize=(4.8 * len(configs), 3.4), squeeze=False)
    for ax, c in zip(axes[0], configs):
        for m in TUNED:
            g = trials[(trials["config"] == c) & (trials["model"] == m)]
            if len(g):
                ax.plot(g["trial"], g["best_so_far"], marker="o", ms=3, label=m)
        ax.set_title(f"{c}: best CV error so far")
        ax.set_xlabel("Optuna trial")
        ax.set_ylabel("mean positioning error (m)")
        ax.set_xlim(-0.5, 29.5)
        ax.grid(linewidth=0.3)
        if ax.has_data():
            ax.legend(fontsize=7)
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------------- fit-and-predict progress
def finished_runs(out: str | Path) -> pd.DataFrame:
    rows = []
    for path in sorted((Path(out) / "logs" / "runs").glob("*.json")):
        r = read_json(path)
        rows.append(dict(config=r["config"], model=r["model"], seed=r["seed"], mean_m=r["stats"]["mean"],
                         median_m=r["stats"]["median"], p95_m=r["stats"]["p95"], fit_s=r["cost"]["fit_s"],
                         predict_s=r["cost"]["predict_s"], peak_gpu_mem_mb=r["cost"]["peak_gpu_mem_mb"],
                         finished_utc=r["finished_utc"]))
    return pd.DataFrame(rows, columns=["config", "model", "seed", "mean_m", "median_m", "p95_m", "fit_s", "predict_s",
                                       "peak_gpu_mem_mb", "finished_utc"])


def runs_expected(configs: list[str]) -> int:
    return len(configs) * sum(5 if m in SEEDED else 1 for m in ALL_MODELS)


def runs_table(runs: pd.DataFrame) -> pd.DataFrame:
    """Mean and standard deviation over seeds of the mean error, per configuration and model."""
    if runs.empty:
        return pd.DataFrame(columns=["config", "model", "runs", "mean_error_m", "std_m", "fit_s", "predict_s"])
    g = runs.groupby(["config", "model"], sort=False)
    t = g.agg(runs=("seed", "count"), mean_error_m=("mean_m", "mean"), std_m=("mean_m", "std"),
              fit_s=("fit_s", "mean"), predict_s=("predict_s", "mean")).reset_index()
    t["model"] = pd.Categorical(t["model"], list(ALL_MODELS))
    return t.sort_values(["config", "model"]).round(3).reset_index(drop=True)


def runs_figure(runs: pd.DataFrame):
    """Mean positioning error of every finished run, per model."""
    import matplotlib.pyplot as plt

    configs = list(dict.fromkeys(runs["config"])) or ["(no runs yet)"]
    fig, axes = plt.subplots(1, len(configs), figsize=(4.8 * len(configs), 3.6), squeeze=False)
    for ax, c in zip(axes[0], configs):
        g = runs[runs["config"] == c]
        models = [m for m in ALL_MODELS if m in set(g["model"])]
        for i, m in enumerate(models):
            v = g[g["model"] == m]["mean_m"]
            ax.scatter([i] * len(v), v, s=18, c="#1f77b4" if m in TFMS else "#7f7f7f")
        ax.set_xticks(range(len(models)))
        ax.set_xticklabels(models, rotation=60, ha="right", fontsize=8)
        ax.set_title(f"{c}: mean error per run")
        ax.set_ylabel("mean positioning error (m)")
        ax.grid(axis="y", linewidth=0.3)
    fig.tight_layout()
    return fig
