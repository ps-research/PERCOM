"""Small shared helpers: logging, JSON files, provenance, environment report."""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import logging
import os
import platform
import socket
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def node_tag() -> str:
    """Short name of the machine a run happened on. Set P1_NODE to override."""
    return os.environ.get("P1_NODE") or socket.gethostname()


def usable_cpus() -> int:
    """Cores this process may use: the smaller of the affinity mask and the cgroup quota."""
    n = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else (os.cpu_count() or 1)
    try:
        quota, period = Path("/sys/fs/cgroup/cpu.max").read_text().split()[:2]
        if quota != "max":
            n = min(n, max(1, int(int(quota) / int(period))))
    except (OSError, ValueError):
        pass
    return n


# ----------------------------------------------------------------------------- pausing other jobs
# A P1-E02 job registers its session id here. P1-E01's timed runs stop those
# sessions while they run, so that the fit and predict times of P1-E01 are not
# measured on a machine shared with another job.
JOB_REGISTRY = Path("/tmp/p1_jobs")


def register_session(kind: str) -> Path:
    JOB_REGISTRY.mkdir(parents=True, exist_ok=True)
    path = JOB_REGISTRY / f"{kind}_{os.getpid()}.sid"
    path.write_text(str(os.getsid(0)))
    return path


def _sessions(kind: str) -> list[int]:
    out = []
    for path in JOB_REGISTRY.glob(f"{kind}_*.sid"):
        pid = int(path.stem.split("_")[-1])
        if Path(f"/proc/{pid}").exists():
            sid = int(path.read_text())
            if sid != os.getsid(0):
                out.append(sid)
        else:
            path.unlink(missing_ok=True)
    return out


class paused_sessions:
    """Context manager: SIGSTOP every process of the registered sessions of ``kind``, SIGCONT on exit."""

    def __init__(self, kind: str, log=None):
        self.kind, self.log, self.sids = kind, log, []

    def _signal(self, sig: str) -> None:
        for sid in self.sids:
            subprocess.run(["pkill", f"-{sig}", "-s", str(sid)], capture_output=True)

    def __enter__(self):
        self.sids = _sessions(self.kind)
        self._signal("STOP")
        if self.log and self.sids:
            self.log(f"paused {self.kind} sessions {self.sids} for the timed runs")
        return self

    def __exit__(self, *exc):
        self._signal("CONT")
        if self.log and self.sids:
            self.log(f"resumed {self.kind} sessions {self.sids}")
        return False


def get_logger(name: str, logfile: str | Path | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(message)s", "%Y-%m-%dT%H:%M:%S")
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(fmt)
    logger.addHandler(stream)
    if logfile:
        Path(logfile).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(logfile)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    logger.propagate = False
    return logger


def write_json(path: str | Path, obj) -> None:
    """Write through a temporary file so a reader never sees half a file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, default=_jsonable) + "\n")
    os.replace(tmp, path)


def read_json(path: str | Path):
    return json.loads(Path(path).read_text())


def _jsonable(obj):
    import numpy as np

    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (tuple, set)):
        return list(obj)
    if isinstance(obj, Path):
        return str(obj)
    return str(obj)


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _sh(cmd: str, cwd: str | Path | None = None) -> str:
    try:
        return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=120).stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return f"(failed: {exc})"


def git_commit(repo: str | Path = REPO_ROOT) -> str:
    return _sh("git rev-parse HEAD", cwd=repo) or "unknown"


def git_dirty(repo: str | Path = REPO_ROOT) -> bool:
    return bool(_sh("git status --porcelain --untracked-files=no", cwd=repo))


def env_report(data_root: str | Path | None = None) -> str:
    """Text for env.txt: code commit, hardware, OS, package versions."""
    lines = [
        f"written_utc: {now_utc()}",
        f"node: {node_tag()}",
        f"code_commit: {git_commit()}{' (uncommitted changes)' if git_dirty() else ''}",
        f"code_branch: {_sh('git rev-parse --abbrev-ref HEAD', cwd=REPO_ROOT)}",
    ]
    if data_root:
        lines.append(f"dataset_commit: {git_commit(data_root)}")
    lines += [
        f"python: {sys.version.replace(chr(10), ' ')}",
        f"platform: {platform.platform()}",
        f"os_release: {_sh('. /etc/os-release 2>/dev/null && echo $PRETTY_NAME')}",
        "cpu_model: " + _sh("lscpu | grep 'Model name' | head -1 | sed 's/.*: *//'"),
        f"cpu_count_logical: {os.cpu_count()}",
        f"cpu_count_usable: {len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else os.cpu_count()}",
        "cpu_quota_cgroup: " + (_sh("cat /sys/fs/cgroup/cpu.max 2>/dev/null") or "n/a"),
        "memory: " + _sh("free -g | awk 'NR==2{print $2\" GiB total\"}'"),
        "gpu: " + (_sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader") or "none"),
        f"usable_cpus: {usable_cpus()}",
        f"OMP_WAIT_POLICY: {os.environ.get('OMP_WAIT_POLICY', '(unset)')}",
    ]
    try:
        import torch

        lines.append(f"torch: {torch.__version__}; cuda build {torch.version.cuda}; cuda available {torch.cuda.is_available()}")
    except Exception as exc:  # noqa: BLE001
        lines.append(f"torch: not importable ({exc})")
    freeze = _sh(f"{sys.executable} -m pip freeze 2>/dev/null") or _sh(f"uv pip freeze --python {sys.executable} 2>/dev/null")
    lines += ["", f"## installed packages ({sys.executable})", freeze]
    return "\n".join(lines) + "\n"
