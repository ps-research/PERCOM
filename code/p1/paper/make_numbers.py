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

    # Seeds, bootstrap and hardware.
    summ = "results/P1-E01/metrics/e1_summary.csv"
    with (ROOT / summ).open(newline="") as f:
        rs = list(csv.DictReader(f))
    seeded = {len({r["seed"] for r in rs if r["model"] == m}) for m in ("tabpfn-nan", "tabicl", "rf", "lgbm-ph", "mlp")}
    if len(seeded) != 1:
        raise SystemExit(f"{summ}: seeded models differ in seed count: {sorted(seeded)}")
    add("numSeedsMain", str(seeded.pop()), summ, "seeds per model with randomness")
    cs = "results/P1-E03/metrics/c_seeds.csv"
    with (ROOT / cs).open(newline="") as f:
        rc = list(csv.DictReader(f))
    tfm_seeds = {len({r["seed"] for r in rc if r["model"] == m}) for m in ("tabpfn-nan", "tabpfn-ph", "tabicl")}
    if len(tfm_seeds) != 1:
        raise SystemExit(f"{cs}: foundation models differ in seed count: {sorted(tfm_seeds)}")
    add("numSeedsTFM", str(tfm_seeds.pop()), cs, "seeds per foundation model")
    bt = "results/P1-E01/metrics/e1_bootstrap.csv"
    with (ROOT / bt).open(newline="") as f:
        reader = csv.DictReader(f)
        rbt = list(reader)
        level = [c for c in reader.fieldnames if re.fullmatch(r"ci\d+_low", c)][0][2:-4]
    n_res = {r["n_resamples"] for r in rbt}
    if len(n_res) != 1:
        raise SystemExit(f"{bt}: resample counts differ")
    add("numBootstrapResamples", fmt_int(int(n_res.pop())), bt, "n_resamples")
    add("numBootstrapLevel", level, bt, "interval level, from the column names")
    env = (ROOT / "results/P1-E01/env.txt").read_text()
    mib = int(re.search(r"^gpu: .*?, (\d+) MiB", env, flags=re.M).group(1))
    cpus = int(re.search(r"^usable_cpus: (\d+)", env, flags=re.M).group(1))
    add("numGPUMemoryGB", str(round(mib / 1024)), "results/P1-E01/env.txt", f"gpu memory {mib} MiB / 1024, rounded")
    add("numCPUCores", str(cpus), "results/P1-E01/env.txt", "usable_cpus")

    # Full survey: paired bootstrap of best foundation model against best baseline (seed 0).
    by_cfg = {r["config"]: r for r in rbt}
    for short, config in BUILDINGS.items():
        r = by_cfg[config]
        lo, hi, diff = float(r["ci95_low"]), float(r["ci95_high"]), float(r["diff_tfm_minus_baseline"])
        if not hi < 0:
            raise SystemExit(f"{bt}: the interval for {config} does not exclude zero ({lo}, {hi})")
        add(f"numBootGain{short}", f"{-diff:.2f}", bt, f"config={config}: -(diff_tfm_minus_baseline) = {-diff:.4f}, interval [{lo:.3f}, {hi:.3f}]")
    ap_diffs = []
    for config in ("HCXY-AP", "SYL-AP"):
        r = by_cfg[config]
        lo, hi = float(r["ci95_low"]), float(r["ci95_high"])
        if not lo < 0 < hi:
            raise SystemExit(f"{bt}: the interval for {config} excludes zero; the text says it does not")
        ap_diffs.append(abs(float(r["diff_tfm_minus_baseline"])))
    add("numAPDiffMax", f"{math.ceil(max(ap_diffs) * 100) / 100:.2f}", bt,
        f"max |diff| on the installed-access-point files ({max(ap_diffs):.4f}), rounded up; both intervals include zero")
    # Twenty seeds: spread of TabICLv2's mean error per building.
    spreads = []
    for config in BUILDINGS.values():
        vals = [float(r["mean"]) for r in rc if r["config"] == config and r["model"] == "tabicl"]
        spreads.append(max(vals) - min(vals))
    # The text says TabICLv2's average over all its seeds stays below every baseline in each building.
    for config in BUILDINGS.values():
        tab = [float(r["mean"]) for r in rc if r["config"] == config and r["model"] == "tabicl"]
        base = {}
        for r in rs:
            if r["config"] == config and not r["model"].startswith("tab"):
                base.setdefault(r["model"], []).append(float(r["mean"]))
        best_base = min(sum(v) / len(v) for v in base.values())
        if not sum(tab) / len(tab) < best_base:
            raise SystemExit(f"{config}: TabICLv2's seed average {sum(tab) / len(tab):.3f} is not below the best baseline {best_base:.3f}")
    add("numSeedSpreadTabICL", f"{math.ceil(max(spreads) * 100) / 100:.2f}", cs,
        f"max over buildings of (max - min) of TabICLv2's mean error over its seeds ({max(spreads):.4f}), rounded up")

    # Missing access points: building averages (30 draws) at 0% and at the largest share.
    def bavg(model, share):
        vals = []
        for config in BUILDINGS.values():
            v = [float(r["mean"]) for r in rows if r["config"] == config and r["model"] == model and int(float(r["share"])) == share]
            vals.append(sum(v) / len(v))
        return sum(vals) / len(vals)
    for model, name in (("tabicl", "TabICL"), ("tabpfn-nan", "TabPFN"), ("tabpfn-ph", "TabPFNPh"), ("knn", "KNN"),
                        ("lgbm-nan", "LGBMNaN"), ("lgbm-ph", "LGBMPh")):
        add(f"numMissingAvg{name}", f"{bavg(model, top):.2f}", e3, f"{model}: mean over buildings of the 30-draw mean at {top}%")
    add("numZeroAvgTabPFNPh", f"{bavg('tabpfn-ph', 0):.2f}", e3, "tabpfn-ph: mean over buildings at 0%")
    base_avgs = {m: bavg(m, top) for m in ("knn", "rf", "lgbm-nan", "lgbm-ph", "svr", "mlp", "gp")}
    if min(base_avgs, key=base_avgs.get) != "knn":
        raise SystemExit(f"{e3}: kNN is not the strongest baseline on average at {top}%: {base_avgs}")
    # Abstract headline: both foundation models average below a whole number of metres, and below half
    # the average error of the best tuned baseline (checked; the build fails if either stops holding).
    tfm_top = max(bavg("tabicl", top), bavg("tabpfn-nan", top))
    if not tfm_top < 0.5 * min(base_avgs.values()):
        raise SystemExit(f"{e3}: the foundation models are not below half the best baseline at {top}%: {tfm_top:.2f} vs {min(base_avgs.values()):.2f}")
    add("numMissingAvgTFMBelow", str(math.ceil(tfm_top)), e3,
        f"max of the tabicl and tabpfn-nan building averages at {top}% ({tfm_top:.2f}), rounded up; also below half the best baseline average ({min(base_avgs.values()):.2f})")
    zero_avgs = {m: bavg(m, 0) for m in ("tabpfn-nan", "tabpfn-ph", "tabicl", "knn", "rf", "lgbm-nan", "lgbm-ph", "svr", "mlp", "gp")}
    if min(zero_avgs, key=zero_avgs.get) != "tabpfn-ph":
        raise SystemExit(f"{e3}: TabPFN with -105 is not the most accurate model at 0%: {zero_avgs}")
    if not bavg("lgbm-nan", top) >= bavg("lgbm-ph", top):
        raise SystemExit(f"{e3}: LightGBM with NaN beats -105 at {top}%; the text says it gains nothing")

    # Fewer reference points (10 draws) and fewer scans (V-C), each claim checked.
    shares_e2 = sorted({int(r["share"]) for r in r2})
    low = shares_e2[1]
    def e2mean(config, model, share):
        v = [float(r["mean"]) for r in r2 if r["config"] == config and r["model"] == model and int(r["share"]) == share]
        return sum(v) / len(v)
    for config in BUILDINGS.values():
        knn = e2mean(config, "knn", low)
        if not e2mean(config, "tabicl", low) < knn:
            raise SystemExit(f"{e2}: TabICLv2 is not below kNN at {low}% in {config}")
        for m in ("rf", "lgbm-ph", "lgbm-nan"):
            if not e2mean(config, m, low) > knn:
                raise SystemExit(f"{e2}: {m} is not behind kNN at {low}% in {config}")
    add("numRPLowShare", str(low), e2, f"share at which TabICLv2 beats kNN in every building (checked)")
    add("numRPMinShare", str(shares_e2[0]), e2, "smallest share of reference points tested")
    crs = "results/P1-E02/metrics/e2_crossing.csv"
    with (ROOT / crs).open(newline="") as f:
        rcr = {(r["config"], r["model"]): r for r in csv.DictReader(f)}
    for short, config in (("CETC", "CETC331"), ("SYL", "SYL-All")):
        add(f"numCross{short}", f"{float(rcr[(config, 'tabicl')]['crossing_share_pct']):.0f}", crs,
            f"config={config}, tabicl: crossing_share_pct = {float(rcr[(config, 'tabicl')]['crossing_share_pct']):.2f}")
    if not float(rcr[("HCXY-All", "tabicl")]["crossing_share_pct"]) > 50:
        raise SystemExit(f"{crs}: HCXY crossing is not above 50%; 'two of the three buildings' would understate")
    def bscan(config, model, k):
        v = [float(r["mean"]) for r in rb if r["config"] == config and r["model"] == model and int(r["scans_per_point"]) == k]
        return sum(v) / len(v)
    kmin = min(int(r["scans_per_point"]) for r in rb)
    knn_full = {}
    for r in rs:
        if r["model"] == "knn":
            knn_full[r["config"]] = float(r["mean"])
    rel_knn = []
    for config in ("HCXY-All", "SYL-All"):
        for m in ("tabpfn-nan", "tabpfn-ph", "tabicl"):
            if not bscan(config, m, kmin) < knn_full[config]:
                raise SystemExit(f"{bs}: {m} with {kmin} scan is not below full-survey kNN in {config}")
        rel_knn.append(bscan(config, "knn", kmin) / knn_full[config])
    if not sum(rel_knn) / len(rel_knn) > 1:
        raise SystemExit(f"{bs}: kNN with {kmin} scan does not lose accuracy on average")
    add("numScanMin", str(kmin), bs, f"fewest scans per point; every foundation model below full-survey kNN there (checked)")

    # Section VI claims: a foundation model has the lowest error at every level of the three stress
    # tests in every building, and every phone in the test scans also took part in the survey.
    tfms = {"tabpfn-nan", "tabpfn-ph", "tabicl"}
    for rows, key, src in ((list(csv.DictReader((ROOT / e3).open(newline=""))), "share", e3),
                           (r2, "share", e2), (rb, "scans_per_point", bs)):
        cells = {}
        for r in rows:
            if r["config"] in BUILDINGS.values():
                cells.setdefault((r["config"], r[key], r["model"]), []).append(float(r["mean"]))
        levels = {(c, k) for c, k, _ in cells}
        for c, k in levels:
            means = {m: sum(v) / len(v) for (cc, kk, m), v in cells.items() if (cc, kk) == (c, k)}
            if min(means, key=means.get) not in tfms:
                raise SystemExit(f"{src}: no foundation model has the lowest error at {key}={k} in {c}")
    import pandas as pd
    pairs = {"CETC331": ("CETC331/Training_CETC331.csv", "CETC331/Testing_CETC331.csv"),
             "HCXY": ("HCXY/Training_HCXY_All_30.csv", "HCXY/Testing_HCXY_All.csv"),
             "SYL": ("SYL/Training_SYL_All_30.csv", "SYL/Testing_SYL_All.csv")}
    for b, (tr, te) in pairs.items():
        survey = set(pd.read_csv(ROOT / "data/SODIndoorLoc" / tr, usecols=["PhoneID"]).PhoneID)
        test = set(pd.read_csv(ROOT / "data/SODIndoorLoc" / te, usecols=["PhoneID"]).PhoneID)
        if not test <= survey:
            raise SystemExit(f"{b}: test phones {sorted(test - survey)} are absent from the survey; Section VI says otherwise")

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
