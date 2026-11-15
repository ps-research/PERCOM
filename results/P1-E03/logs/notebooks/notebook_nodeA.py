# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "lightgbm==4.7.0",
#     "optuna==5.0.0",
#     "pandas==3.1.1",
#     "tabicl==2.2.0",
#     "tabpfn==10.0.0",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", auto_download=["html"])


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    from gdrive_fsspec import GoogleDriveFileSystem

    fs = GoogleDriveFileSystem(use_listings_cache=False, skip_instance_cache=True, auth_kwargs={"use_local_webserver": False})
    mo.output.clear_console()
    return (fs,)


@app.cell
def _():
    return


@app.cell
def intro(mo):
    mo.md(r"""
    # P1-E01: can a tabular foundation model localize from Wi-Fi fingerprints without training?

    **Goal.** With the full survey of a building as context, does an off-the-shelf tabular foundation model
    (TabPFN v2, TabICLv2) localize as well as tuned classical methods, and what does it cost in time and memory?
    This notebook runs brief `briefs/P1-E01.md` of the repository `ps-research/PERCOM` for the
    configuration(s) **HCXY-All** of the SODIndoorLoc dataset.

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
    """)

    return


@app.cell
def imports():
    import os
    import sys
    import time
    from pathlib import Path

    import pandas as pd


    return Path, os, pd, sys, time


@app.cell(hide_code=True)
def helpers():
    # ── molab notebook helpers ──────────────────────────────────────────────────
    # Paste this as ONE cell in the notebook (hide_code=True). Every workaround
    # here fixes a failure verified empirically on a live molab node.
    import os as _os, time as _time, subprocess as _sp, shlex as _shlex

    # ---------- Google Drive ----------
    def _fs():
        """Drive handle with the cache actually cleared.
        TRAPS: fsspec caches the INSTANCE (GoogleDriveFileSystem() returns the SAME
        object), and ls(refresh=True) still will NOT show files written by another
        notebook/the lab box. invalidate_cache() is the only thing that works."""
        from gdrive_fsspec import GoogleDriveFileSystem
        fs = GoogleDriveFileSystem(); fs.invalidate_cache(); return fs

    def _rp(p):
        """Drive paths must NEVER start with '/'. exists('/x') silently returns
        False; open/cat/put raise FileNotFoundError."""
        return str(p).strip().lstrip("/")

    def dls(path="", detail=False):
        fs=_fs(); p=_rp(path)
        e=fs.ls(p if p else "/", detail=True, refresh=True)
        return e if detail else sorted(x["name"].split("/")[-1] for x in e)

    def dexists(path): return _fs().exists(_rp(path))

    def dget(remote, local):
        """Drive -> node (file or directory)."""
        fs=_fs(); r=_rp(remote)
        _os.makedirs(_os.path.dirname(local) or ".", exist_ok=True)
        fs.get(r, local, recursive=True) if fs.isdir(r) else fs.get_file(r, local)
        return local

    def dput(local, remote):
        """Node -> Drive (file or directory).
        TRAP: fs.put(recursive=True) is BROKEN — raises AttributeError partway,
        leaving a SILENT PARTIAL UPLOAD. Upload file-by-file instead."""
        fs=_fs(); r=_rp(remote)
        if _os.path.isdir(local):
            n=0
            for root,_,files in _os.walk(local):
                for f in files:
                    lp=_os.path.join(root,f)
                    rp=f"{r}/"+_os.path.relpath(lp,local).replace(_os.sep,"/")
                    fs.makedirs(_os.path.dirname(rp), exist_ok=True)
                    fs.put_file(lp,rp); n+=1
            return {"uploaded":n,"remote":r}
        if "/" in r: fs.makedirs(_os.path.dirname(r), exist_ok=True)
        fs.put_file(local,r); return {"uploaded":1,"remote":r}

    def dput_atomic(local, remote):
        """Upload to .tmp then move — readers never see a half-written file
        (Drive has NO locking; concurrent writes are last-writer-wins)."""
        fs=_fs(); r=_rp(remote); tmp=r+".tmp"
        if "/" in r: fs.makedirs(_os.path.dirname(r), exist_ok=True)
        fs.put_file(local,tmp)
        if fs.exists(r): fs.rm(r)
        fs.mv(tmp,r); return r

    def dput_tar(local_dir, remote_tar):
        """Pack a directory to ONE tarball first. Drive costs ~1.7 s PER FILE:
        1000 loose files ≈ 30 min, the same data as one tarball ≈ seconds."""
        tar="/tmp/_up_%d.tar.gz"%int(_time.time())
        _sp.run(["tar","-czf",tar,"-C",local_dir,"."],check=True)
        r=dput_atomic(tar,remote_tar); _os.remove(tar); return r

    def dget_tar(remote_tar, local_dir):
        tar="/tmp/_dn_%d.tar.gz"%int(_time.time())
        dget(remote_tar,tar); _os.makedirs(local_dir,exist_ok=True)
        _sp.run(["tar","-xzf",tar,"-C",local_dir],check=True); _os.remove(tar)
        return local_dir

    # ---------- long jobs (kernel safety) ----------
    def bg_run(pycode, tag=None):
        """Run python DETACHED. The ONLY safe way to do anything slower than ~60 s.
        The kernel is single-threaded and marimo INTERRUPTS the running cell when
        the pair-channel client disconnects (agent shell timeout ~120 s)."""
        tag=tag or ("job_%d"%int(_time.time()))
        script,log,done=f"/tmp/{tag}.py",f"/tmp/{tag}.log",f"/tmp/{tag}.done"
        for p in (log,done):
            if _os.path.exists(p): _os.remove(p)
        open(script,"w").write(pycode.rstrip()+"\nopen(%r,'w').write('ok')\n"%done)
        _sp.Popen(f"setsid python3 {_shlex.quote(script)} >{_shlex.quote(log)} 2>&1 </dev/null &",shell=True)
        _time.sleep(0.5); return {"tag":tag,"log":log,"done":done}

    def bg_status(h, tail=15):
        log=h["log"] if isinstance(h,dict) else h
        done=h["done"] if isinstance(h,dict) else log.replace(".log",".done")
        txt=open(log,errors="replace").read() if _os.path.exists(log) else ""
        return {"finished":_os.path.exists(done),"lines":txt.count("\n"),
                "tail":"\n".join(txt.splitlines()[-tail:])}

    # ---------- shell with real verification ----------
    def run(cmd, cwd="/marimo", timeout=60, check=False):
        """Structured shell result: {rc, ok, stdout, stderr, timed_out, secs}.
        Keep timeout well under the client timeout; use bg_run for anything longer."""
        t0=_time.time(); to=False
        try:
            p=_sp.run(cmd,shell=True,cwd=cwd,capture_output=True,text=True,timeout=timeout)
            rc,out,err=p.returncode,p.stdout,p.stderr
        except _sp.TimeoutExpired as e:
            to=True; rc=124
            out=(e.stdout or b"").decode() if isinstance(e.stdout,bytes) else (e.stdout or "")
            err=(e.stderr or b"").decode() if isinstance(e.stderr,bytes) else (e.stderr or "")
        r={"cmd":cmd,"rc":rc,"ok":rc==0 and not to,"stdout":out[:4000],
           "stderr":err[:4000],"timed_out":to,"secs":round(_time.time()-t0,2)}
        if check and not r["ok"]: raise RuntimeError(f"rc={rc}: {cmd}\n{err[:400]}")
        return r


    return bg_run, run


@app.cell
def workspace(Path, mo, os, run, sys, time):
    REPO_URL = "https://github.com/ps-research/PERCOM"
    BRANCH = "exp/P1-E01"
    COMMIT = "1f61e59bad6645d38d0fcf7799aaeb50e24bfec1"
    DATASET_URL = "https://github.com/bijingxue/SODIndoorLoc"
    DATASET_COMMIT = "bfe8f63f55957cc25b23ba91c408ae345a3fb0b7"
    NODE = "nodeA"
    CONFIGS = ['HCXY-All']

    WORK = Path("/tmp/percom")
    REPO = WORK / "PERCOM"
    DATA = REPO / "data" / "SODIndoorLoc"
    OUT = WORK / "out" / "P1-E01"
    WORK.mkdir(parents=True, exist_ok=True)
    if not (REPO / ".git").exists():
        run(f"git clone --quiet --branch {BRANCH} {REPO_URL} {REPO}", cwd=str(WORK), timeout=55, check=True)
    run(f"git fetch --quiet origin {BRANCH} && git checkout --quiet {COMMIT}", cwd=str(REPO), timeout=55, check=True)
    if not (DATA / ".git").exists():
        run(f"git clone --quiet {DATASET_URL} {DATA}", cwd=str(WORK), timeout=55, check=True)
    run(f"git checkout --quiet {DATASET_COMMIT}", cwd=str(DATA), check=True)

    _run_id_file = WORK / "RUN_ID"
    if not _run_id_file.exists():
        _run_id_file.write_text(f"{NODE}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}")
    RUN_ID = _run_id_file.read_text().strip()
    DRIVE_RUN = f"molab/PERCOM/runs/{RUN_ID}"
    OUT.mkdir(parents=True, exist_ok=True)
    os.environ["P1_NODE"] = NODE
    if str(REPO / "code") not in sys.path:
        sys.path.insert(0, str(REPO / "code"))
    mo.md(
        f"**Workspace.** Repository at commit `{COMMIT[:10]}` in `{REPO}`, dataset at commit "
        f"`{DATASET_COMMIT[:10]}`. Run id **{RUN_ID}**; results are checkpointed to Drive under `{DRIVE_RUN}/`."
    )

    return CONFIGS, DATA, DRIVE_RUN, NODE, OUT, REPO, REPO_URL, WORK


@app.cell
def project(REPO):
    import p1.data as p1data
    import p1.e1 as p1e1
    import p1.nb as p1nb
    from p1.assets import write_assets
    from p1.common import env_report

    PROJECT_CODE = REPO / "code" / "p1"  # the workspace cell above put the repository on sys.path

    return env_report, p1data, p1e1, p1nb, write_assets


@app.cell
def environment(DATA, NODE, OUT, env_report, mo):
    env_text = env_report(DATA)
    (OUT / f"env_{NODE}.txt").write_text(env_text)
    mo.md("### Environment\n```\n" + env_text.split("## pip freeze")[0].strip() + "\n```")

    return


@app.cell
def data(CONFIGS, DATA, mo, p1data, p1nb, pd):
    counts = p1data.count_table(DATA)
    surveys = {_c: p1data.load_config(_c, DATA) for _c in CONFIGS}
    _first = surveys[CONFIGS[0]]
    mo.vstack(
        [
            mo.md(
                "### The data: SODIndoorLoc\n"
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

    return


@app.cell
def gate(DATA, OUT, mo, p1e1, pd):
    gate_result = p1e1.gate(str(DATA), OUT)
    gate_table = pd.read_csv(OUT / "metrics" / "e0_check.csv")
    mo.vstack(
        [
            mo.md(
                "### Part A. Pipeline check (the gate)\n"
                "kNN with k = 5, distance weights and Euclidean distance, against the dataset paper. Values in metres.\n\n"
                f"Gate passed: **{gate_result['gate_passed']}**, with \"not detected\" written as "
                f"**{', '.join(gate_result.get('passed_with', [])) or 'neither way'}**."
            ),
            gate_table[
                ["config", "not_detected", "mean_m", "paper_mean_m", "diff_mean_m", "p50_m", "paper_p50_m", "p95_m",
                 "paper_p95_m", "mean_within_tolerance"]
            ].round(3),
        ]
    )

    return (gate_result,)


@app.cell
def weights(DATA, OUT, mo, write_assets):
    assets = write_assets(OUT, str(DATA))
    mo.md(
        "### Model weights\n"
        f"- TabPFN v2: `{assets['tabpfn']['file']}` from `{assets['tabpfn']['repo']}`, gated: "
        f"{assets['tabpfn']['gated']}, licence: {assets['tabpfn']['licence']}\n"
        f"- TabICLv2: `{assets['tabicl']['file']}` from `{assets['tabicl']['repo']}`, gated: "
        f"{assets['tabicl']['gated']}, licence: {assets['tabicl']['licence']}, allowed by the brief "
        f"(BSD, MIT or Apache): **{assets['tabicl']['licence_allowed']}**\n\n"
        "Both were downloaded without a token, an account or a licence prompt. SHA-256 sums are in `assets.md`."
    )

    return (assets,)


@app.cell
def launch(
    CONFIGS,
    DATA,
    NODE,
    OUT,
    REPO,
    assets,
    bg_run,
    gate_result,
    mo,
    p1nb,
    sys,
):
    PARTB_CMD = (
        f"{sys.executable} -m p1.e1 partb --out {OUT} --data {DATA} --configs {' '.join(CONFIGS)} "
        "--workers 3 --threads 6"
    )
    if not assets["tabicl"]["licence_allowed"]:
        # Stop condition of the brief: drop tabicl, finish the rest, and report.
        PARTB_CMD += " --models knn rf lgbm-ph lgbm-nan svr mlp gp tabpfn-nan tabpfn-ph"
    if not gate_result["gate_passed"]:
        partb_job = None  # the gate did not pass: nothing is launched
    elif p1nb.job_alive("p1.e1 partb"):
        partb_job = {"tag": "p1e01_partb", "log": "/tmp/p1e01_partb.log", "done": "/tmp/p1e01_partb.done"}
    else:
        partb_job = bg_run(p1nb.job_script(PARTB_CMD, REPO, NODE), tag="p1e01_partb")
    mo.md(
        "### Part B. Full-survey comparison\n"
        "One background job runs the Optuna searches of the tuned baselines, then fits every model and predicts "
        "the test file, one run after the other so that the timings are clean. Finished units are skipped when "
        f"the job is started again.\n\n`{PARTB_CMD}`"
    )

    return


@app.cell
def refresh(mo):
    progress_refresh = mo.ui.refresh(options=["30s", "1m", "5m"], default_interval="1m", label="Refresh progress")
    progress_refresh

    return (progress_refresh,)


@app.cell
def search_progress(CONFIGS, NODE, OUT, mo, p1nb, progress_refresh):
    progress_refresh
    search_trials = p1nb.search_trials(OUT)
    mo.vstack(
        [
            mo.md("#### Baseline search: best cross-validated error so far (read from the job's log)"),
            p1nb.search_figure(search_trials),
            p1nb.search_status(OUT, CONFIGS),
            mo.md("```\n" + p1nb.tail(OUT / "logs" / f"search_{NODE}.log", 5) + "\n```"),
        ]
    )

    return


@app.cell
def runs_progress(CONFIGS, NODE, OUT, mo, p1nb, progress_refresh):
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
            mo.md("```\n" + p1nb.tail(OUT / "logs" / f"final_{NODE}.log", 5) + "\n```"),
        ]
    )

    return (runs,)


@app.cell
def results(mo, p1nb, progress_refresh, runs):
    progress_refresh
    _rc = p1nb.job_exit_code("/tmp/p1e01_partb.log")
    _finished = _rc is not None
    _table = p1nb.runs_table(runs)
    mo.vstack(
        [
            mo.md(
                "### Results on this node\n"
                + (f"The Part B job has finished with exit code {_rc}. " if _finished else "The Part B job is still running; the table fills in as runs finish. ")
                + "Mean positioning error on the test file, averaged over seeds (std over seeds where there are five)."
            ),
            _table.pivot(index="model", columns="config", values="mean_error_m").reset_index() if len(_table) else _table,
        ]
    )

    return


@app.cell
def writeup(mo):
    mo.md(r"""
    ### Write-up (P1-E01)

    On **HCXY-All** (this node), TabPFN v2 with "not detected" as -105 had the lowest mean error, 1.558 m over 5 seeds, against 1.805 m for the best tuned baseline (kNN); seed 0 difference -0.344 m, 95% bootstrap interval [-0.665, -0.019].

    The pipeline check reproduced the dataset paper's kNN within 0.008 m in all three buildings with "not detected" written as -105. Full comparison over the five configurations: `results/P1-E01/RESULTS.md` in the repository (pull request #2).
    """)

    return


@app.cell
def e2_intro(mo):
    mo.md(r"""
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

    This node runs draws **[0, 1, 2]** of Part A for all three buildings, and Part B and the extra 100% seeds for
    **HCXY-All**, whose P1-E01 results are on this node. The foundation models run as a GPU job; the baseline
    searches as a CPU job. Both import `code/p1` from a second checkout of the repository.
    """)
    return


@app.cell
def e2_workspace(DATA, NODE, REPO_URL, WORK, mo, run, sys):
    import subprocess as _subprocess

    E2_COMMIT = "0f526ead990ececd0c06d004781317f51b0286d5"
    E2_DRAWS = [0, 1, 2]
    E2_OWN = ['HCXY-All']
    E2_CONFIGS = ['CETC331', 'HCXY-All', 'SYL-All']
    REPO2 = WORK / "PERCOM-e2"
    OUT2 = WORK / "out" / "P1-E02"
    if not (REPO2 / ".git").exists():
        run(f"git clone --quiet --branch exp/P1-E02 {REPO_URL} {REPO2}", cwd=str(WORK), timeout=55, check=True)
    run(f"git fetch --quiet origin exp/P1-E02 && git checkout --quiet {E2_COMMIT}", cwd=str(REPO2), timeout=55, check=True)
    OUT2.mkdir(parents=True, exist_ok=True)
    _r = _subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {str(REPO2 / 'code')!r}); from p1.common import env_report; "
         f"print(env_report({str(DATA)!r}), end='')"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO2),
    )
    (OUT2 / f"env_{NODE}.txt").write_text(_r.stdout)
    mo.md(
        f"P1-E02 code at commit `{E2_COMMIT[:10]}` in `{REPO2}`; output in `{OUT2}`. "
        f"Environment of the job interpreter written to `env_{NODE}.txt`:\n```\n"
        + _r.stdout.split("## installed")[0].strip() + "\n```"
    )

    return E2_CONFIGS, E2_DRAWS, E2_OWN, OUT2, REPO2


@app.cell
def e2_launch(
    DATA,
    E2_CONFIGS,
    E2_DRAWS,
    E2_OWN,
    NODE,
    OUT,
    OUT2,
    REPO2,
    REPO_URL,
    WORK,
    bg_run,
    mo,
    p1nb,
    run,
    sys,
):
    E2B_COMMIT = "4393db1dad12ca685c83679aceebe096f49cb49f"
    E2_GPU_CMD = (
        f"{sys.executable} -m p1.e2 gpu --out {OUT2} --e1-out {OUT} --data {DATA} --configs {' '.join(E2_CONFIGS)} "
        f"--draws {' '.join(map(str, E2_DRAWS))} --own {' '.join(E2_OWN)}"
    )
    # LightGBM single-threaded (identical predictions to 4 threads, measured on a node) and more workers:
    # no OpenMP oversubscription. Runs from its own checkout so the GPU job's tree is never touched.
    REPO2B = WORK / "PERCOM-e2b"
    if not (REPO2B / ".git").exists():
        run(f"git clone --quiet --branch exp/P1-E02 {REPO_URL} {REPO2B}", cwd=str(WORK), timeout=55, check=True)
    run(f"git fetch --quiet origin exp/P1-E02 && git checkout --quiet {E2B_COMMIT}", cwd=str(REPO2B), timeout=55, check=True)
    E2_CPU_CMD = (
        f"env P1_LGBM_THREADS=1 {sys.executable} -m p1.e2 parta --no-tfm --out {OUT2} --data {DATA} "
        f"--configs {' '.join(E2_CONFIGS)} --draws {' '.join(map(str, E2_DRAWS))} --workers 6 --threads 3"
    )
    e2_jobs = {}
    # The CPU job starts only after this node's P1-E01 job has exited: running both at once oversubscribes
    # the 20 cores (LightGBM slows down badly) and P1-E01's timed runs must not share the machine.
    e2_e1_done = p1nb.job_exit_code("/tmp/p1e01_partb.log") == 0
    for _tag, _cmd, _pat, _gate in (("p1e02_gpu", E2_GPU_CMD, "p1.e2 gpu", True),
                                    ("p1e02_parta", E2_CPU_CMD, "p1.e2 parta", e2_e1_done)):
        if p1nb.job_alive(_pat) or p1nb.job_exit_code(f"/tmp/{_tag}.log") == 0:
            e2_jobs[_tag] = "already running or finished"
        elif not _gate:
            e2_jobs[_tag] = "waiting for the P1-E01 job on this node to finish"
        else:
            e2_jobs[_tag] = bg_run(p1nb.job_script(_cmd, REPO2B if _tag == "p1e02_parta" else REPO2, NODE), tag=_tag)["log"]
    mo.md(
        "### P1-E02 jobs\n"
        f"- GPU job (foundation models, Part A draws {E2_DRAWS}, then Part B and 100% seeds 5 to 9 for {E2_OWN}):\n  `{E2_GPU_CMD}`\n"
        f"- CPU job (baseline searches and refits, Part A draws {E2_DRAWS}): **{e2_jobs['p1e02_parta'] if isinstance(e2_jobs['p1e02_parta'], str) and not e2_jobs['p1e02_parta'].startswith('/tmp') else 'launched'}**\n  `{E2_CPU_CMD}`\n\n"
        "A P1-E01 timed run on this node pauses both jobs while it runs."
    )

    return E2_CPU_CMD, REPO2B


@app.cell
def e2_launch_own(
    DATA,
    E2_OWN,
    NODE,
    OUT,
    OUT2,
    REPO2,
    bg_run,
    mo,
    p1nb,
    progress_refresh,
    sys,
):
    progress_refresh
    _tuned = ["knn", "rf", "lgbm-ph", "lgbm-nan", "svr", "mlp"]
    # Needs this node's P1-E01 best values, and must not overlap P1-E01's timed runs: wait for the P1-E01 job to exit.
    e2_own_ready = all((OUT / "config" / "best_params" / f"{_c}__{_m}.json").exists() for _c in E2_OWN for _m in _tuned) \
        and p1nb.job_exit_code("/tmp/p1e01_partb.log") == 0
    E2_OWN_CMD = (
        f"{sys.executable} -m p1.e2 own --out {OUT2} --e1-out {OUT} --data {DATA} --configs {' '.join(E2_OWN)}"
    )
    if not e2_own_ready:
        e2_own_state = "waiting for the P1-E01 job on this node (searches of " + ", ".join(E2_OWN) + " and timed runs)"
    elif p1nb.job_alive("p1.e2 own") or p1nb.job_exit_code("/tmp/p1e02_own.log") == 0:
        e2_own_state = "running or finished"
    else:
        bg_run(p1nb.job_script(E2_OWN_CMD, REPO2, NODE), tag="p1e02_own")
        e2_own_state = "launched"
    mo.md(f"Part B and 100% seeds 5 to 9 of the baselines for {E2_OWN}: **{e2_own_state}**.\n\n`{E2_OWN_CMD}`")

    return


@app.cell
def e2_progress(E2_CONFIGS, E2_DRAWS, OUT2, mo, p1nb, pd, progress_refresh):
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
            mo.md("```\n" + "\n".join(f"{_t}: " + p1nb.tail(f"/tmp/{_t}.log", 2).replace("\n", " | ")
                                       for _t in ("p1e02_gpu", "p1e02_parta", "p1e02_own")) + "\n```"),
        ]
    )

    return (e2_runs,)


@app.cell
def e2_results(OUT2, e2_runs, mo, pd, progress_refresh):
    progress_refresh
    import json as _json_e3

    _e3 = []
    for _p in sorted((OUT2 / "logs" / "e3").glob("*.json")) if (OUT2 / "logs" / "e3").exists() else []:
        _r = _json_e3.loads(_p.read_text())
        for _s in _r["per_set"]:
            _e3.append(dict(config=_r["config"], model=_r["model"], share=_s["share"], mean_m=_s["mean"]))
    e2_e3 = pd.DataFrame(_e3, columns=["config", "model", "share", "mean_m"])
    mo.vstack(
        [
            mo.md("### P1-E02 results on this node\nPart A: mean error averaged over the finished draws, by share kept."),
            e2_runs.groupby(["config", "model", "share"])["mean_m"].mean().unstack("share").round(3).reset_index()
            if len(e2_runs) else e2_runs,
            mo.md("Part B: mean error averaged over draws, by share of access points switched off."),
            e2_e3.groupby(["config", "model", "share"])["mean_m"].mean().unstack("share").round(3).reset_index()
            if len(e2_e3) else e2_e3,
        ]
    )

    return


@app.cell
def e2_writeup(mo):
    mo.md(r"""
    ### P1-E02 write-up

    Over all three nodes (assembled in `results/P1-E02/` of the repository): the foundation models reach the error of tuned kNN on the full survey with 16 to 30% of the reference points in SYL and CETC331 (TabICL 16% and 21%), but need 55% (TabPFN -105) or more in HCXY. When access points disappear after the survey, native missing values protect TabPFN: with 60% of the MACs switched off in HCXY, TabPFN with NaN errs by 4.5 m and with -105 by 8.5 m, kNN by 8.2 m, and random forest and LightGBM by about 19 m.

    Pull request #3 of the repository.
    """)

    return


@app.cell
def e3_intro(mo):
    mo.md(r"""
    ---
    # P1-E03: uncertainty, scans per point, more seeds, more missing-AP draws

    Approved by the PI on 2026-11-15 (brief `briefs/P1-E03.md` on branch `exp/P1-E03`). No model is tuned.

    - **A. Uncertainty.** Predictive quantiles of TabPFN and TabICL and the GP's predictive std on the full survey:
      coverage and width of central intervals, and whether the predicted spread ranks the errors.
    - **B. Scans per reference point.** Context of k = 1 to 30 scans of every reference point (HCXY-All, SYL-All):
      accuracy, fit and predict time, GPU memory; k = 30 on HCXY goes past TabPFN's 10,000-row limit.
    - **C. More seeds.** Seeds 5 to 19 of the foundation models on the full survey.
    - **D. More missing-AP draws.** P1-E02 Part B with draws 10 to 29.

    This node: A and C for **HCXY-All, HCXY-AP** (B where it applies), D for **HCXY-All**.
    """)
    return


@app.cell
def e3_workspace(REPO_URL, WORK, mo, run):
    E3_COMMIT = "6d16af4904e8c14cdf1ca77346939c375ab3c10e"
    E3_GPU_CONFIGS = ['HCXY-All']
    E3_OWN = ['HCXY-All']
    REPO3 = WORK / "PERCOM-e3"
    OUT3 = WORK / "out" / "P1-E03"
    if not (REPO3 / ".git").exists():
        run(f"git clone --quiet --branch exp/P1-E03 {REPO_URL} {REPO3}", cwd=str(WORK), timeout=55, check=True)
    run(f"git fetch --quiet origin exp/P1-E03 && git checkout --quiet {E3_COMMIT}", cwd=str(REPO3), timeout=55, check=True)
    OUT3.mkdir(parents=True, exist_ok=True)
    mo.md(f"P1-E03 code at commit `{E3_COMMIT[:10]}` in `{REPO3}`; output in `{OUT3}`.")

    return E3_GPU_CONFIGS, E3_OWN, OUT3, REPO3


@app.cell
def e3_launch(
    DATA,
    E3_GPU_CONFIGS,
    E3_OWN,
    NODE,
    OUT,
    OUT3,
    REPO3,
    bg_run,
    mo,
    p1nb,
    progress_refresh,
    sys,
):
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
        "### P1-E03 jobs\n"
        f"- GPU job (A, C, B): **{e3_jobs['p1e03_gpu']}**\n  `{E3_GPU_CMD}`\n"
        f"- D (more Part B draws): **{e3_jobs['p1e03_own']}**\n  `{E3_OWN_CMD}`"
    )

    return


@app.cell
def e3_progress(OUT3, mo, p1nb, pd, progress_refresh):
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
            mo.md("```\n" + "\n".join(f"{_t}: " + p1nb.tail(f"/tmp/{_t}.log", 2).replace("\n", " | ")
                                       for _t in ("p1e03_gpu", "p1e03_own")) + "\n```"),
        ]
    )

    return


@app.cell
def e3_writeup(mo):
    mo.md(r"""
    ### P1-E03 write-up

    The predictive intervals of the foundation models are overconfident: their 80% intervals hold 64 to 69% of the test rows (the GP's hold 78% but are about three times wider), and the predicted spread ranks the errors only weakly (Spearman 0.18 to 0.29). One scan per reference point is almost as good as 26 for the foundation models (TabPFN -105: +10% error in HCXY, none in SYL), while kNN loses 72% in HCXY. Twenty seeds confirm the five-seed results; the error differs strongly between phones.

    Pull request #4 of the repository.
    """)

    return


@app.cell
def checkpoint(DRIVE_RUN, NODE, OUT, OUT2, OUT3, Path, fs, mo, time):
    import shutil as _shutil
    import subprocess as _sp_ckpt

    _jobs = (("p1e01_partb", OUT), ("p1e02_gpu", OUT2), ("p1e02_parta", OUT2), ("p1e02_parta2", OUT2), ("p1e02_own", OUT2),
             ("p1e03_gpu", OUT3), ("p1e03_gpu2", OUT3), ("p1e03_own", OUT3))
    for _tag, _dst in _jobs:
        if Path(f"/tmp/{_tag}.log").exists() and _dst.exists():
            (_dst / "logs" / "jobs").mkdir(parents=True, exist_ok=True)
            _shutil.copyfile(f"/tmp/{_tag}.log", _dst / "logs" / "jobs" / f"{_tag}_{NODE}.log")


    def _upload(_local_dir, _remote):
        """Tar locally, remove the old copy and any leftover .tmp, upload to the final name; one retry on a cache error.
        Only this notebook writes its run folder and nobody reads it while jobs run, so no atomic rename is needed."""
        _tar = f"/tmp/_ckpt_{Path(_remote).name}"
        _sp_ckpt.run(["tar", "-czf", _tar, "-C", str(_local_dir), "."], check=True)
        for _attempt in range(2):
            try:
                fs.invalidate_cache()
                for _p in (_remote, _remote + ".tmp"):
                    if fs.exists(_p):
                        fs.rm(_p)
                fs.put_file(_tar, _remote)
                return _remote
            except (FileNotFoundError, FileExistsError):
                if _attempt:
                    raise
        return _remote


    _ckpt = []
    for _name, _dir in (("P1-E01", OUT), ("P1-E02", OUT2), ("P1-E03", OUT3)):
        if _dir.exists():
            _ckpt.append(_upload(_dir, f"{DRIVE_RUN}/{_name}.tar.gz"))
    checkpoint = _ckpt
    mo.md(f"Results and job logs checkpointed to Drive: {', '.join('`' + c + '`' for c in checkpoint)} at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}.")

    return


@app.cell
def e2_launch_extra(
    E2_CPU_CMD,
    NODE,
    REPO2B,
    bg_run,
    mo,
    p1nb,
    progress_refresh,
):
    progress_refresh
    # Draws moved to this node from a slower one; they start once this node's first Part A job has finished.
    E2_EXTRA_DRAWS = [6]
    E2_CPU_CMD2 = E2_CPU_CMD.split(" --draws ")[0] + " --draws " + " ".join(map(str, E2_EXTRA_DRAWS)) + \
        " --workers " + E2_CPU_CMD.split(" --workers ")[1]
    if not E2_EXTRA_DRAWS:
        e2_extra_state = "no extra draws on this node"
    elif p1nb.job_alive("p1.e2 parta") or p1nb.job_exit_code("/tmp/p1e02_parta2.log") == 0:
        e2_extra_state = "running or finished"
    elif p1nb.job_exit_code("/tmp/p1e02_parta.log") != 0:
        e2_extra_state = "waiting for the first Part A job on this node"
    else:
        bg_run(p1nb.job_script(E2_CPU_CMD2, REPO2B, NODE), tag="p1e02_parta2")
        e2_extra_state = "launched"
    mo.md(f"Extra Part A draws {E2_EXTRA_DRAWS}: **{e2_extra_state}**" + (f"\n\n`{E2_CPU_CMD2}`" if E2_EXTRA_DRAWS else ""))

    return


if __name__ == "__main__":
    app.run()
