"""Cells of the marimo notebook that run P1-E02 on one compute node.

They are appended to the P1-E01 notebook of the same node and reuse its names
(WORK, REPO, DATA, OUT, NODE, bg_run, run, p1nb, progress_refresh). P1-E02 code is
checked out in a second folder, so the P1-E01 job keeps running from its own tree.
"""
from __future__ import annotations

ALL = ["CETC331", "HCXY-All", "SYL-All"]


def cells(node: str, draws: list[int], own: list[str], commit: str, workers: int = 4, threads: int = 6,
          branch: str = "exp/P1-E02") -> list[dict]:
    C = []

    def cell(name, code, hide=False, run=True):
        C.append(dict(name=name, code=code.strip("\n") + "\n", hide=hide, run=run))

    cell("e2_intro", f'''
mo.md(
    r"""
---
# P1-E02: fewer reference points, and access points that go missing

**Questions.** (1) How does positioning error grow as fewer reference points are surveyed?
(2) How does it grow when access points go missing after the survey?

**Method (brief `briefs/P1-E02.md`).** Configurations CETC331, HCXY-All and SYL-All; all ten models of P1-E01.

- *Part A (E2).* Keep 5, 10, 25, 50 or 100% of the reference points; for draw `d` shuffle them with seed `d` and keep
  the first ones. Re-tune every baseline on each reduced survey (30 Optuna trials, 3-fold GroupKFold by reference
  point), refit with seed `d`; give the tabular foundation models the reduced survey as context. Predict the full test file.
- *Part B (E3).* Fit every model once on the full survey; switch off 0 to 60% of the MAC columns in the test file
  (set to "not detected") and predict.

This node runs draws **{draws}** of Part A for all three buildings, and Part B and the extra 100% seeds for
**{", ".join(own)}**, whose P1-E01 results are on this node. The foundation models run as a GPU job; the baseline
searches as a CPU job. Both import `code/p1` from a second checkout of the repository.
"""
)
''')

    cell("e2_workspace", f'''
import subprocess as _subprocess

E2_COMMIT = "{commit}"
E2_DRAWS = {draws!r}
E2_OWN = {own!r}
E2_CONFIGS = {ALL!r}
REPO2 = WORK / "PERCOM-e2"
OUT2 = WORK / "out" / "P1-E02"
if not (REPO2 / ".git").exists():
    run(f"git clone --quiet --branch {branch} {{REPO_URL}} {{REPO2}}", cwd=str(WORK), timeout=55, check=True)
run(f"git fetch --quiet origin {branch} && git checkout --quiet {{E2_COMMIT}}", cwd=str(REPO2), timeout=55, check=True)
OUT2.mkdir(parents=True, exist_ok=True)
_r = _subprocess.run(
    [sys.executable, "-c",
     f"import sys; sys.path.insert(0, {{str(REPO2 / 'code')!r}}); from p1.common import env_report; "
     f"print(env_report({{str(DATA)!r}}), end='')"],
    capture_output=True, text=True, timeout=120, cwd=str(REPO2),
)
(OUT2 / f"env_{{NODE}}.txt").write_text(_r.stdout)
mo.md(
    f"P1-E02 code at commit `{{E2_COMMIT[:10]}}` in `{{REPO2}}`; output in `{{OUT2}}`. "
    f"Environment of the job interpreter written to `env_{{NODE}}.txt`:\\n```\\n"
    + _r.stdout.split("## installed")[0].strip() + "\\n```"
)
''')

    cell("e2_launch", f'''
E2_GPU_CMD = (
    f"{{sys.executable}} -m p1.e2 gpu --out {{OUT2}} --e1-out {{OUT}} --data {{DATA}} --configs {{' '.join(E2_CONFIGS)}} "
    f"--draws {{' '.join(map(str, E2_DRAWS))}} --own {{' '.join(E2_OWN)}}"
)
E2_CPU_CMD = (
    f"{{sys.executable}} -m p1.e2 parta --no-tfm --out {{OUT2}} --data {{DATA}} --configs {{' '.join(E2_CONFIGS)}} "
    f"--draws {{' '.join(map(str, E2_DRAWS))}} --workers {workers} --threads {threads}"
)
e2_jobs = {{}}
for _tag, _cmd, _pat in (("p1e02_gpu", E2_GPU_CMD, "p1.e2 gpu"), ("p1e02_parta", E2_CPU_CMD, "p1.e2 parta")):
    if p1nb.job_alive(_pat) or p1nb.job_exit_code(f"/tmp/{{_tag}}.log") == 0:
        e2_jobs[_tag] = "already running or finished"
    else:
        e2_jobs[_tag] = bg_run(p1nb.job_script(_cmd, REPO2, NODE), tag=_tag)["log"]
mo.md(
    "### P1-E02 jobs\\n"
    f"- GPU job (foundation models, Part A draws {{E2_DRAWS}}, then Part B and 100% seeds 5 to 9 for {{E2_OWN}}):\\n  `{{E2_GPU_CMD}}`\\n"
    f"- CPU job (baseline searches and refits, Part A draws {{E2_DRAWS}}):\\n  `{{E2_CPU_CMD}}`\\n\\n"
    "A P1-E01 timed run on this node pauses both jobs while it runs."
)
''')

    cell("e2_launch_own", f'''
progress_refresh
_tuned = ["knn", "rf", "lgbm-ph", "lgbm-nan", "svr", "mlp"]
e2_own_ready = all((OUT / "config" / "best_params" / f"{{_c}}__{{_m}}.json").exists() for _c in E2_OWN for _m in _tuned)
E2_OWN_CMD = (
    f"{{sys.executable}} -m p1.e2 own --out {{OUT2}} --e1-out {{OUT}} --data {{DATA}} --configs {{' '.join(E2_OWN)}}"
)
if not e2_own_ready:
    e2_own_state = "waiting for the P1-E01 searches of " + ", ".join(E2_OWN)
elif p1nb.job_alive("p1.e2 own") or p1nb.job_exit_code("/tmp/p1e02_own.log") == 0:
    e2_own_state = "running or finished"
else:
    bg_run(p1nb.job_script(E2_OWN_CMD, REPO2, NODE), tag="p1e02_own")
    e2_own_state = "launched"
mo.md(f"Part B and 100% seeds 5 to 9 of the baselines for {{E2_OWN}}: **{{e2_own_state}}**.\\n\\n`{{E2_OWN_CMD}}`")
''')

    cell("e2_progress", '''
progress_refresh
import json as _json


def _e2_runs(out_dir):
    _rows = []
    for _p in sorted((out_dir / "logs" / "runs").glob("*.json")):
        _r = _json.loads(_p.read_text())
        _rows.append(dict(config=_r["config"], share=_r["share"], draw=_r["draw"], model=_r["model"],
                          mean_m=_r["stats"]["mean"], fit_s=_r["cost"]["fit_s"]))
    return pd.DataFrame(_rows, columns=["config", "share", "draw", "model", "mean_m", "fit_s"])


e2_runs = _e2_runs(OUT2)


def _e2_figure(df):
    import matplotlib.pyplot as _plt

    _fig, _axes = _plt.subplots(1, 3, figsize=(14, 3.6))
    for _ax, _c in zip(_axes, E2_CONFIGS):
        _g = df[df["config"] == _c]
        for _m in sorted(set(_g["model"])):
            _gm = _g[_g["model"] == _m].groupby("share")["mean_m"].mean()
            _ax.plot(_gm.index, _gm.values, marker="o", ms=3, lw=1.6 if _m.startswith("tab") else 0.9, label=_m)
        _ax.set_xscale("log")
        _ax.set_title(f"{_c}: mean error by share kept (draws so far)")
        _ax.set_xlabel("share of reference points kept (%)")
        _ax.set_ylabel("mean positioning error (m)")
        _ax.grid(linewidth=0.3)
        if _ax.has_data():
            _ax.legend(fontsize=6, ncol=2)
    _fig.tight_layout()
    return _fig


_expected = len(E2_CONFIGS) * 4 * len(E2_DRAWS) * 10
mo.vstack(
    [
        mo.md(f"#### P1-E02 Part A progress on this node: {len(e2_runs)} of {_expected} runs finished"),
        _e2_figure(e2_runs),
        mo.md("```\\n" + "\\n".join(f"{_t}: " + p1nb.tail(f"/tmp/{_t}.log", 2).replace("\\n", " | ")
                                   for _t in ("p1e02_gpu", "p1e02_parta", "p1e02_own")) + "\\n```"),
    ]
)
''')

    cell("e2_results", '''
progress_refresh
_e3 = []
for _p in sorted((OUT2 / "logs" / "e3").glob("*.json")) if (OUT2 / "logs" / "e3").exists() else []:
    _r = _json.loads(_p.read_text())
    for _s in _r["per_set"]:
        _e3.append(dict(config=_r["config"], model=_r["model"], share=_s["share"], mean_m=_s["mean"]))
e2_e3 = pd.DataFrame(_e3, columns=["config", "model", "share", "mean_m"])
mo.vstack(
    [
        mo.md("### P1-E02 results on this node\\nPart A: mean error averaged over the finished draws, by share kept."),
        e2_runs.groupby(["config", "model", "share"])["mean_m"].mean().unstack("share").round(3).reset_index()
        if len(e2_runs) else e2_runs,
        mo.md("Part B: mean error averaged over draws, by share of access points switched off."),
        e2_e3.groupby(["config", "model", "share"])["mean_m"].mean().unstack("share").round(3).reset_index()
        if len(e2_e3) else e2_e3,
    ]
)
''')

    cell("e2_writeup", '''
mo.md(
    r"""
### P1-E02 write-up

*Filled in when the jobs on this node have finished.* The figures and tables over all three nodes are assembled in
`results/P1-E02/` of the repository.
"""
)
''')
    return C
