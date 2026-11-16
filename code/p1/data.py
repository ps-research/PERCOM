"""SODIndoorLoc: loading, count checks and the two ways of writing "not detected".

The dataset is cloned from DATASET_URL into ``data/SODIndoorLoc`` (ignored by git).
Every function here works on the raw signal-strength matrix, in which the value
100 means "not detected". Models never see that matrix directly: they see
``encode(X, "missing")`` or ``encode(X, "placeholder")``.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

DATASET_URL = "https://github.com/bijingxue/SODIndoorLoc"
DEFAULT_ROOT = "data/SODIndoorLoc"

# The last eight columns of every file. No metadata column is ever an input.
META_COLS = ["ECoord", "NCoord", "FloorID", "BuildingID", "SceneID", "UserID", "PhoneID", "SampleTimes"]
TARGET_COLS = ["ECoord", "NCoord"]
# A reference point (training file) or a test point (test file) is one unique triple.
POINT_COLS = ["ECoord", "NCoord", "FloorID"]

NOT_DETECTED = 100
PLACEHOLDER = -105.0

# TabPFN v2 context cap (brief P1-E01, "Models").
TABPFN_MAX_ROWS = 10_000
TABPFN_SCANS_KEPT = 26

# Expected counts, copied from the table in briefs/P1-E01.md.
CONFIGS: dict[str, dict] = {
    "CETC331": dict(
        train="CETC331/Training_CETC331.csv", test="CETC331/Testing_CETC331.csv",
        train_rows=955, ref_points=955, rss_cols=52, test_rows=840, test_points=84,
    ),
    "HCXY-All": dict(
        train="HCXY/Training_HCXY_All_30.csv", test="HCXY/Testing_HCXY_All.csv",
        train_rows=11_370, ref_points=379, rss_cols=347, test_rows=860, test_points=86,
    ),
    "HCXY-AP": dict(
        train="HCXY/Training_HCXY_AP_30.csv", test="HCXY/Testing_HCXY_AP.csv",
        train_rows=11_370, ref_points=379, rss_cols=56, test_rows=860, test_points=86,
    ),
    "SYL-All": dict(
        train="SYL/Training_SYL_All_30.csv", test="SYL/Testing_SYL_All.csv",
        train_rows=8_880, ref_points=296, rss_cols=363, test_rows=1_020, test_points=102,
    ),
    "SYL-AP": dict(
        train="SYL/Training_SYL_AP_30.csv", test="SYL/Testing_SYL_AP.csv",
        train_rows=8_880, ref_points=296, rss_cols=46, test_rows=1_020, test_points=102,
    ),
}
ALL_CONFIGS = list(CONFIGS)
# The three configurations of the pipeline check (P1-E01 Part A) and of P1-E02.
MAIN_CONFIGS = ["CETC331", "HCXY-All", "SYL-All"]


@dataclass
class Survey:
    """One configuration: a training file and its test file."""

    name: str
    mac_cols: list[str]
    X_train: np.ndarray  # raw signal strengths, float64, 100 = not detected
    y_train: np.ndarray  # (n, 2): ECoord, NCoord in metres
    rp_train: np.ndarray  # reference-point id of every training row
    rp_table: pd.DataFrame  # one row per reference point: id, ECoord, NCoord, FloorID
    X_test: np.ndarray
    y_test: np.ndarray
    tp_test: np.ndarray  # test-point id of every test row
    tp_table: pd.DataFrame

    @property
    def n_ref_points(self) -> int:
        return len(self.rp_table)

    @property
    def n_test_points(self) -> int:
        return len(self.tp_table)


def _points(df: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    """Number the unique (ECoord, NCoord, FloorID) triples in order of first appearance."""
    ids = df.groupby(POINT_COLS, sort=False).ngroup().to_numpy()
    table = df[POINT_COLS].drop_duplicates().reset_index(drop=True)
    table.insert(0, "id", np.arange(len(table)))
    return ids, table


def load_config(name: str, root: str | Path = DEFAULT_ROOT) -> Survey:
    spec = CONFIGS[name]
    root = Path(root)
    train = pd.read_csv(root / spec["train"])
    test = pd.read_csv(root / spec["test"])
    for label, df in (("training", train), ("test", test)):
        if list(df.columns[-8:]) != META_COLS:
            raise ValueError(f"{name}: the last eight columns of the {label} file are not the metadata columns")
    mac_cols = list(train.columns[:-8])
    if list(test.columns[:-8]) != mac_cols:
        raise ValueError(f"{name}: training and test files do not have the same MAC columns in the same order")
    rp_train, rp_table = _points(train)
    tp_test, tp_table = _points(test)
    return Survey(
        name=name,
        mac_cols=mac_cols,
        X_train=train[mac_cols].to_numpy(dtype=np.float64, copy=True),
        y_train=train[TARGET_COLS].to_numpy(dtype=np.float64, copy=True),
        rp_train=rp_train,
        rp_table=rp_table,
        X_test=test[mac_cols].to_numpy(dtype=np.float64, copy=True),
        y_test=test[TARGET_COLS].to_numpy(dtype=np.float64, copy=True),
        tp_test=tp_test,
        tp_table=tp_table,
    )


def count_table(root: str | Path = DEFAULT_ROOT) -> pd.DataFrame:
    """Every count of the brief's data table, expected against found (P1-E01 step 2)."""
    rows = []
    for name, spec in CONFIGS.items():
        s = load_config(name, root)
        found = dict(
            train_rows=len(s.X_train), ref_points=s.n_ref_points, rss_cols=len(s.mac_cols),
            test_rows=len(s.X_test), test_points=s.n_test_points,
        )
        for key, value in found.items():
            rows.append(dict(config=name, quantity=key, expected=spec[key], found=value, ok=spec[key] == value))
    return pd.DataFrame(rows)


def encode(X_raw: np.ndarray, how: str) -> np.ndarray:
    """Write "not detected" (100) the way a model expects.

    ``missing``: NaN. ``placeholder``: -105. ``raw``: left as 100 (pipeline check only).
    """
    X = np.array(X_raw, dtype=np.float64, copy=True)
    if how == "missing":
        X[X == NOT_DETECTED] = np.nan
    elif how == "placeholder":
        X[X == NOT_DETECTED] = PLACEHOLDER
    elif how != "raw":
        raise ValueError(f"unknown encoding: {how}")
    return X


def cap_rows(rp_ids: np.ndarray, seed: int, max_rows: int = TABPFN_MAX_ROWS,
             keep: int = TABPFN_SCANS_KEPT) -> np.ndarray | None:
    """Row indices of the capped context, or None when the survey fits under the cap.

    Above ``max_rows`` rows, keep ``keep`` scans of every reference point, drawn at
    random with the run seed. On HCXY (379 points, 30 scans each) this gives 9,854 rows.
    """
    if len(rp_ids) <= max_rows:
        return None
    rng = np.random.default_rng(seed)
    picked = []
    for rp in np.unique(rp_ids):
        rows = np.flatnonzero(rp_ids == rp)
        picked.append(rng.choice(rows, size=min(keep, len(rows)), replace=False))
    return np.sort(np.concatenate(picked))


def average_per_point(X_encoded: np.ndarray, y: np.ndarray, rp_ids: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """One fingerprint per reference point: the mean of its scans (after encoding)."""
    order = np.unique(rp_ids)
    Xm = np.vstack([X_encoded[rp_ids == rp].mean(axis=0) for rp in order])
    ym = np.vstack([y[rp_ids == rp].mean(axis=0) for rp in order])
    return Xm, ym


def shared_locations(s: Survey) -> dict:
    """How many test points share their location with a reference point (P1-E01 step 15)."""
    ref3 = set(map(tuple, s.rp_table[POINT_COLS].to_numpy()))
    ref2 = set(map(tuple, s.rp_table[TARGET_COLS].to_numpy()))
    same3 = sum(tuple(t) in ref3 for t in s.tp_table[POINT_COLS].to_numpy())
    same2 = sum(tuple(t) in ref2 for t in s.tp_table[TARGET_COLS].to_numpy())
    return dict(config=s.name, test_points=s.n_test_points, shared_with_floor=same3, shared_ignoring_floor=same2)
