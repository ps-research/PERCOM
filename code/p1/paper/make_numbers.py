"""Write the paper's number macros from merged results.

Every number in the paper is a macro produced here, never typed by hand. Each macro
is read from a file under ``results/`` (merged into ``main``) or from a constant in
``code/``. Next to each macro the output records the source file, what was selected
in it, and the first 12 hex digits of the file's SHA-256, so any number in the paper
can be traced back.

Run from the repository root:

    python3 code/p1/paper/make_numbers.py --out <overleaf clone>/ASSETS/numbers.tex

Add a macro by adding one entry to ``SPEC``; macros enter as the paragraphs that
need them are approved.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

BUILDINGS = {"CETC": "CETC331", "HCXY": "HCXY-All", "SYL": "SYL-All"}
PREINSTALLED = {"HCXY": "HCXY-AP", "SYL": "SYL-AP"}


def sha12(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def csv_cell(rel: str, where: dict, col: str):
    """The one cell in column ``col`` of the one row matching ``where``; fails otherwise."""
    path = ROOT / rel
    with path.open(newline="") as f:
        rows = [r for r in csv.DictReader(f) if all(r[k] == v for k, v in where.items())]
    if len(rows) != 1:
        raise SystemExit(f"{rel}: expected one row for {where}, found {len(rows)}")
    selector = ", ".join(f"{k}={v}" for k, v in where.items()) + f" -> {col}"
    return rows[0][col], rel, selector


def run_log_field(pattern: str, keys: tuple[str, ...]):
    """A field that must be identical in every run log matching ``pattern``."""
    paths = sorted((ROOT / "results").glob(pattern))
    if not paths:
        raise SystemExit(f"no run logs match results/{pattern}")
    values = set()
    for p in paths:
        node = json.loads(p.read_text())
        for k in keys:
            node = node[k]
        values.add(node)
    if len(values) != 1:
        raise SystemExit(f"results/{pattern}: {'.'.join(keys)} differs across runs: {sorted(values)}")
    combined = hashlib.sha256(b"".join(p.read_bytes() for p in paths)).hexdigest()[:12]
    return values.pop(), f"results/{pattern}", f"{'.'.join(keys)}, identical in {len(paths)} run logs", combined


def code_constant(rel: str, name: str):
    """An integer constant assigned at module level, e.g. ``NAME = 10_000``."""
    text = (ROOT / rel).read_text()
    m = re.search(rf"^{name}\s*=\s*([0-9_]+)\s*$", text, flags=re.M)
    if not m:
        raise SystemExit(f"{rel}: constant {name} not found")
    return int(m.group(1).replace("_", "")), rel, f"constant {name}"


def as_int(text) -> int:
    value = float(text)
    if value != int(value):
        raise SystemExit(f"expected an integer, got {text}")
    return int(value)


def fmt_int(n: int) -> str:
    return f"{n:,}"


def build_spec():
    """(macro name, value as LaTeX text, source file, selector, file hash)."""
    out = []

    def add(name, value_text, source, selector, digest=None):
        out.append((name, value_text, source, selector, digest or sha12(ROOT / source)))

    counts = "results/P1-E01/metrics/e0_counts.csv"
    shared = "results/P1-E01/metrics/e1_shared_locations.csv"
    for short, config in BUILDINGS.items():
        for qty, label in [("ref_points", "RefPoints"), ("train_rows", "SurveyScans"),
                           ("test_points", "TestPoints"), ("test_rows", "TestScans"),
                           ("rss_cols", "MACs")]:
            raw, src, sel = csv_cell(counts, {"config": config, "quantity": qty}, "found")
            add(f"num{short}{label}", fmt_int(as_int(raw)), src, sel)
        raw, src, sel = csv_cell(shared, {"config": config}, "shared_with_floor")
        add(f"num{short}SharedTestPoints", fmt_int(as_int(raw)), src, sel)
    for short, config in PREINSTALLED.items():
        raw, src, sel = csv_cell(counts, {"config": config, "quantity": "rss_cols"}, "found")
        add(f"num{short}PreinstalledAPs", fmt_int(as_int(raw)), src, sel)

    value, src, sel, digest = run_log_field("P1-E01/logs/runs/HCXY-*__tabpfn-*__seed*.json",
                                            ("info", "context_rows"))
    add("numHCXYTabPFNContextRows", fmt_int(int(value)), src, sel, digest)
    # Missing access points, all 30 draws (the data of Fig. 2), at the largest share switched off.
    # Bounds are rounded outward so the sentence that uses them stays true: up for the foundation
    # models, down for the baselines.
    e3 = "results/P1-E03/metrics/d_e3_more.csv"
    with (ROOT / e3).open(newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["config"] in BUILDINGS.values()]
    top = max(int(float(r["share"])) for r in rows)
    means = {}
    for r in rows:
        if int(float(r["share"])) == top:
            means.setdefault((r["config"], r["model"]), []).append(float(r["mean"]))
    draws = {len(v) for v in means.values()}
    if draws != {30}:
        raise SystemExit(f"{e3}: expected 30 draws per model at {top}%, found {sorted(draws)}")
    avg = {k: sum(v) / len(v) for k, v in means.items()}
    tfm = [v for (c, m), v in avg.items() if m in ("tabpfn-nan", "tabicl")]
    base = [v for (c, m), v in avg.items() if not m.startswith("tab")]
    add("numMissingMaxShare", str(top), e3, "largest share of access points switched off")
    add("numMissingTFMBelow", f"{math.ceil(max(tfm) * 10) / 10:.1f}", e3,
        f"max over buildings of the 30-draw mean at {top}% for tabpfn-nan and tabicl ({max(tfm):.3f}), rounded up")
    add("numMissingBaseAbove", f"{math.floor(min(base) * 10) / 10:.1f}", e3,
        f"min over buildings and baselines of the 30-draw mean at {top}% ({min(base):.3f}), rounded down")

    value, src, sel = code_constant("code/p1/data.py", "TABPFN_MAX_ROWS")
    add("numTabPFNMaxRows", fmt_int(value), src, sel)
    value, src, sel = code_constant("code/p1/data.py", "TABPFN_SCANS_KEPT")
    add("numTabPFNScansKept", fmt_int(value), src, sel)

    # Numbers from published papers: quoted as reported, only from sources read in full
    # (CONTEXT.md). The hash is the source's SHA-256 recorded in the review's index.
    index = ROOT / "litreview" / "p1-tabular-localization" / "sources" / "index.csv"
    with index.open(newline="") as f:
        sha = {r["pid"]: (r["sha256"], r["access_level"]) for r in csv.DictReader(f)}
    for name, value, pid, quote in PUBLISHED:
        digest, level = sha[pid]
        if level != "FULLTEXT":
            raise SystemExit(f"{name}: {pid} was read at {level} level; published numbers need a full-text source")
        out.append((name, value, f"litreview {pid}", f'quote: "{quote}"', digest[:12]))
    return out


PUBLISHED = [
    ("numTabPFNApplications", "200", "P006",
     "we have collected more than 200 published research applications of TabPFN"),
]


def render(spec) -> str:
    names = [s[0] for s in spec]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise SystemExit(f"duplicate macro names: {sorted(dupes)}")
    for n in names:
        if not re.fullmatch(r"[A-Za-z]+", n):
            raise SystemExit(f"macro names may hold letters only: {n}")
    lines = [
        "% Generated by code/p1/paper/make_numbers.py from merged results. Do not edit by hand.",
        "% Each macro: value, then source file | selector | sha256[:12] of the source.",
    ]
    for name, value, source, selector, digest in spec:
        lines.append(f"\\newcommand{{\\{name}}}{{{value}}} % {source} | {selector} | {digest}")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    text = render(build_spec())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(f"wrote {args.out} with {text.count(chr(92) + 'newcommand')} macros")


if __name__ == "__main__":
    main()
