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
    """A numeric constant assigned at module level, e.g. ``NAME = 10_000`` or ``NAME = -105.0``."""
    text = (ROOT / rel).read_text()
    m = re.search(rf"^{name}\s*=\s*(-?[0-9_]+(?:\.[0-9]+)?)\s*$", text, flags=re.M)
    if not m:
        raise SystemExit(f"{rel}: constant {name} not found")
    value = float(m.group(1).replace("_", ""))
    return (int(value) if value == int(value) else value), rel, f"constant {name}"


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
    # Scans per reference point, derived from the two counts above; must divide exactly.
    for short, config in BUILDINGS.items():
        rows = as_int(csv_cell(counts, {"config": config, "quantity": "train_rows"}, "found")[0])
        rps = as_int(csv_cell(counts, {"config": config, "quantity": "ref_points"}, "found")[0])
        if rows % rps:
            raise SystemExit(f"{config}: {rows} survey scans do not divide evenly over {rps} reference points")
        add(f"num{short}ScansPerPoint", fmt_int(rows // rps), counts, f"config={config}: train_rows / ref_points = {rows} / {rps}")
    # Test scans per test point, derived; must divide exactly.
    for short, config in BUILDINGS.items():
        rows = as_int(csv_cell(counts, {"config": config, "quantity": "test_rows"}, "found")[0])
        pts = as_int(csv_cell(counts, {"config": config, "quantity": "test_points"}, "found")[0])
        if rows % pts:
            raise SystemExit(f"{config}: {rows} test scans do not divide evenly over {pts} test points")
        add(f"num{short}TestScansPerPoint", fmt_int(rows // pts), counts, f"config={config}: test_rows / test_points = {rows} / {pts}")
    # Phones and users in the test files, from the phone and user breakdown.
    pu = "results/P1-E03/metrics/e_phone_user.csv"
    with (ROOT / pu).open(newline="") as f:
        pu_rows = list(csv.DictReader(f))
    for short in ("HCXY", "SYL"):
        for group, label in (("PhoneID", "Phones"), ("UserID", "Users")):
            ids = {r["id"] for r in pu_rows if r["config"] == BUILDINGS[short] and r["group"] == group}
            add(f"num{short}{label}", fmt_int(len(ids)), pu, f"distinct {group} in config={BUILDINGS[short]}")
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
    # How the dataset writes "not detected", and the number the baselines get instead.
    value, src, sel = code_constant("code/p1/data.py", "NOT_DETECTED")
    add("numNotDetected", f"{value:+d}", src, sel)
    value, src, sel = code_constant("code/p1/data.py", "PLACEHOLDER")
    add("numPlaceholder", f"$-${abs(value)}", src, sel)

    # Tuning protocol of the baselines.
    value, src, sel = code_constant("code/p1/tuning.py", "N_TRIALS")
    add("numTuningTrials", fmt_int(value), src, sel)
    value, src, sel = code_constant("code/p1/tuning.py", "N_FOLDS")
    add("numTuningFolds", fmt_int(value), src, sel)
    # Pipeline check against the dataset paper (untuned kNN), rounded outward.
    e0 = "results/P1-E01/metrics/e0_check.csv"
    with (ROOT / e0).open(newline="") as f:
        chk = list(csv.DictReader(f))
    ph = [abs(float(r["diff_mean_m"])) for r in chk if r["not_detected"].startswith("placeholder")]
    raw = [abs(float(r["diff_mean_m"])) for r in chk if r["not_detected"].startswith("left as")]
    if len(ph) != 3 or len(raw) != 3:
        raise SystemExit(f"{e0}: expected three buildings per encoding")
    add("numPipelineDiffMax", f"{math.ceil(max(ph) * 100) / 100:.2f}", e0,
        f"max |mean - paper mean| over buildings with -105 ({max(ph):.4f}), rounded up")
    add("numPipelineRawDiffMax", f"{math.ceil(max(raw) * 10) / 10:.1f}", e0,
        f"max |mean - paper mean| over buildings with +100 left in place ({max(raw):.4f}), rounded up")

    # Stress-test protocols, read from the result files.
    def as_list(values):
        vals = [fmt_int(v) for v in values]
        return ", ".join(vals[:-1]) + " and " + vals[-1]
    shares_e3 = sorted({int(float(r["share"])) for r in rows})
    steps = {b - a for a, b in zip(shares_e3, shares_e3[1:])}
    if len(steps) != 1:
        raise SystemExit(f"{e3}: shares are not evenly spaced: {shares_e3}")
    add("numMissingStep", str(steps.pop()), e3, f"spacing of the shares {shares_e3}")
    n_draws = {len({r["draw"] for r in rows if r["config"] == c and r["model"] == m and int(float(r["share"])) == sh})
               for c in BUILDINGS.values() for m in ("tabpfn-nan", "knn") for sh in shares_e3 if sh > 0}
    if len(n_draws) != 1:
        raise SystemExit(f"{e3}: draws differ across shares: {sorted(n_draws)}")
    add("numMissingDraws", str(n_draws.pop()), e3, "draws per share above 0%")
    chk3 = "results/P1-E02/metrics/e3_check_against_e1.csv"
    with (ROOT / chk3).open(newline="") as f:
        d3 = max(abs(float(r["abs_diff"])) for r in csv.DictReader(f))
    add("numMissingZeroCheck", f"{math.ceil(d3 * 100) / 100:.2f}", chk3,
        f"max |error at 0% - full-survey seed-0 error| ({d3:.4f}), rounded up")
    e2 = "results/P1-E02/metrics/e2_summary.csv"
    with (ROOT / e2).open(newline="") as f:
        r2 = list(csv.DictReader(f))
    add("numRPShareList", as_list(sorted({int(r["share"]) for r in r2})), e2, "shares of reference points kept")
    add("numRPDraws", str(len({r["draw"] for r in r2 if r["share"] != "100"})), e2, "draws per share below 100%")
    bs = "results/P1-E03/metrics/b_scans.csv"
    with (ROOT / bs).open(newline="") as f:
        rb = list(csv.DictReader(f))
    add("numScanList", as_list(sorted({int(r["scans_per_point"]) for r in rb})), bs, "scans per reference point kept")
    tfm_draws = {len({r["seed"] for r in rb if r["config"] == c and r["model"] == m and r["scans_per_point"] == k})
                 for c in ("HCXY-All", "SYL-All") for m in ("tabpfn-nan", "tabpfn-ph", "tabicl")
                 for k in {r["scans_per_point"] for r in rb}}
    if len(tfm_draws) != 1:
        raise SystemExit(f"{bs}: foundation-model draws differ: {sorted(tfm_draws)}")
    add("numScanDraws", str(tfm_draws.pop()), bs, "draws per scan count for the foundation models")

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
    ("numDatasetArea", "8,000", "P003", "The total covering area is about 8000 square meters"),
    ("numSpacingSingleFloor", "1.2", "P003",
     "The sampling distance between two adjacent points is about 1.2 meters in two buildings"),
    ("numSpacingCETC", "0.5", "P003", "the distance is about 0.5 meters in a three-story building"),
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
