"""Cells of the marimo notebook that run P1-E03 on one compute node (appended after the P1-E02 cells)."""
from __future__ import annotations


def cells(node: str, gpu_configs: list[str], own: list[str], commit: str, branch: str = "exp/P1-E03") -> list[dict]:
    C = []

    def cell(name, code, hide=False, run=True):
        C.append(dict(name=name, code=code.strip("\n") + "\n", hide=hide, run=run))

    cell("e3_intro", f'''
mo.md(
    r"""
---
# P1-E03: uncertainty, scans per point, more seeds, more missing-AP draws

Approved by the PI on 2026-11-15 (brief `briefs/P1-E03.md` on branch `{branch}`). No model is tuned.

- **A. Uncertainty.** Predictive quantiles of TabPFN and TabICL and the GP's predictive std on the full survey:
  coverage and width of central intervals, and whether the predicted spread ranks the errors.
- **B. Scans per reference point.** Context of k = 1 to 30 scans of every reference point (HCXY-All, SYL-All):
  accuracy, fit and predict time, GPU memory; k = 30 on HCXY goes past TabPFN's 10,000-row limit.
- **C. More seeds.** Seeds 5 to 19 of the foundation models on the full survey.
- **D. More missing-AP draws.** P1-E02 Part B with draws 10 to 29.

This node: A and C for **{", ".join(gpu_configs)}** (B where it applies), D for **{", ".join(own)}**.
"""
)
''')

    cell("e3_workspace", f'''
E3_COMMIT = "{commit}"
E3_GPU_CONFIGS = {gpu_configs!r}
E3_OWN = {own!r}
REPO3 = WORK / "PERCOM-e3"
OUT3 = WORK / "out" / "P1-E03"
if not (REPO3 / ".git").exists():
    run(f"git clone --quiet --branch {branch} {{REPO_URL}} {{REPO3}}", cwd=str(WORK), timeout=55, check=True)
run(f"git fetch --quiet origin {branch} && git checkout --quiet {{E3_COMMIT}}", cwd=str(REPO3), timeout=55, check=True)
OUT3.mkdir(parents=True, exist_ok=True)
mo.md(f"P1-E03 code at commit `{{E3_COMMIT[:10]}}` in `{{REPO3}}`; output in `{{OUT3}}`.")
''')

    cell("e3_launch", '''
progress_refresh
E3_GPU_CMD = (
    f"{sys.executable} -m p1.e3x gpu --out {OUT3} --e1-out {OUT} --data {DATA} --configs {' '.join(E3_GPU_CONFIGS)}"
)
E3_OWN_CMD = f"{sys.executable} -m p1.e3x own --out {OUT3} --e1-out {OUT} --data {DATA} --configs {' '.join(E3_OWN)}"
e3_jobs = {}
# GPU job after this node's P1-E02 GPU job; D after this node's P1-E01 job (it needs the best values).
for _tag, _cmd, _pat, _gate in (
    ("p1e03_gpu", E3_GPU_CMD, "p1.e3x gpu", p1nb.job_exit_code("/tmp/p1e02_gpu.log") == 0),
    ("p1e03_own", E3_OWN_CMD, "p1.e3x own", p1nb.job_exit_code("/tmp/p1e01_partb.log") == 0),
):
    if p1nb.job_alive(_pat) or p1nb.job_exit_code(f"/tmp/{_tag}.log") == 0:
        e3_jobs[_tag] = "running or finished"
    elif not _gate:
        e3_jobs[_tag] = "waiting"
    else:
        bg_run(p1nb.job_script(_cmd, REPO3, NODE), tag=_tag)
        e3_jobs[_tag] = "launched"
mo.md(
    "### P1-E03 jobs\\n"
    f"- GPU job (A, C, B): **{e3_jobs['p1e03_gpu']}**\\n  `{E3_GPU_CMD}`\\n"
    f"- D (more Part B draws): **{e3_jobs['p1e03_own']}**\\n  `{E3_OWN_CMD}`"
)
''')

    cell("e3_progress", '''
progress_refresh
import json as _json3

_rows = []
for _kind in ("uncertainty", "scans", "runs", "e3more"):
    _d = OUT3 / "logs" / _kind
    for _p in sorted(_d.glob("*.json")) if _d.exists() else []:
        _r = _json3.loads(_p.read_text())
        _rows.append(dict(part={"uncertainty": "A", "scans": "B", "runs": "C", "e3more": "D"}[_kind],
                          config=_r.get("config"), model=_r.get("model"),
                          k=_r.get("scans_per_point"), seed=_r.get("seed"),
                          mean_m=(_r.get("stats") or {}).get("mean"),
                          cover80_both=(_r.get("stats") or {}).get("cover80_both")))
e3_rows = pd.DataFrame(_rows, columns=["part", "config", "model", "k", "seed", "mean_m", "cover80_both"])


def _e3_fig(df):
    import matplotlib.pyplot as _plt

    _fig, (_a, _b) = _plt.subplots(1, 2, figsize=(12, 3.6))
    _u = df[df["part"] == "A"]
    for _m in sorted(set(_u["model"])):
        _g = _u[_u["model"] == _m].groupby("config")["cover80_both"].mean()
        _a.plot(_g.index, _g.values, marker="o", label=_m)
    _a.axhline(0.64, color="k", lw=0.8, ls="--")
    _a.set_ylabel("coverage of the 80% box (both coordinates)")
    _a.legend(fontsize=7)
    _s = df[df["part"] == "B"]
    for (_c, _m), _g in _s.groupby(["config", "model"]):
        _gg = _g.groupby("k")["mean_m"].mean()
        _b.plot(_gg.index, _gg.values, marker="o", label=f"{_c} {_m}")
    _b.set_xscale("log")
    _b.set_xlabel("scans per reference point")
    _b.set_ylabel("mean positioning error (m)")
    if _b.has_data():
        _b.legend(fontsize=6, ncol=2)
    _fig.tight_layout()
    return _fig


mo.vstack(
    [
        mo.md(f"#### P1-E03 progress on this node: " + ", ".join(f"{_p}: {(e3_rows['part'] == _p).sum()}" for _p in "ABCD")),
        _e3_fig(e3_rows),
        mo.md("```\\n" + "\\n".join(f"{_t}: " + p1nb.tail(f"/tmp/{_t}.log", 2).replace("\\n", " | ")
                                   for _t in ("p1e03_gpu", "p1e03_own")) + "\\n```"),
    ]
)
''')

    cell("e3_writeup", '''
mo.md(
    r"""
### P1-E03 write-up

*Filled in when the jobs on this node have finished.* Results over all nodes are assembled in `results/P1-E03/`.
"""
)
''')
    return C
