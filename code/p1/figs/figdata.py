"""Runtime access to the result files. Figure scripts never hard-code a number (FIGURE_TASTE II, A3)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


class Results:
    def __init__(self, e1: Path | None = None, e2: Path | None = None, e3: Path | None = None):
        self.e1 = Path(e1 or ROOT / "results" / "P1-E01")
        self.e2 = Path(e2 or ROOT / "results" / "P1-E02")
        self.e3 = Path(e3 or ROOT / "results" / "P1-E03")

    def csv(self, folder: Path, name: str) -> pd.DataFrame:
        p = folder / "metrics" / name
        return pd.read_csv(p) if p.exists() else pd.DataFrame()

    # P1-E01
    def e1_summary(self): return self.csv(self.e1, "e1_summary.csv")
    def e1_bootstrap(self): return self.csv(self.e1, "e1_bootstrap.csv")
    def e0_check(self): return self.csv(self.e1, "e0_check.csv")

    def e1_search(self) -> pd.DataFrame:
        p = self.e1 / "config" / "search_runs.json"
        if not p.exists():
            return pd.DataFrame()
        d = json.loads(p.read_text())
        return pd.DataFrame([dict(config=c, model=m, **{k: v for k, v in r.items() if not isinstance(v, dict)})
                             for c, ms in d.items() for m, r in ms.items()])

    # P1-E02
    def e2_summary(self): return self.csv(self.e2, "e2_summary.csv")
    def e2_crossing(self): return self.csv(self.e2, "e2_crossing.csv")
    def e3_summary(self): return self.csv(self.e2, "e3_summary.csv")

    # P1-E03
    def a_uncertainty(self): return self.csv(self.e3, "a_uncertainty.csv")
    def b_scans(self): return self.csv(self.e3, "b_scans.csv")
    def c_seeds(self): return self.csv(self.e3, "c_seeds.csv")
    def d_e3_more(self): return self.csv(self.e3, "d_e3_more.csv")
    def e_phone_user(self): return self.csv(self.e3, "e_phone_user.csv")

    def e3_all_draws(self) -> pd.DataFrame:
        """P1-E02 Part B (draws 0 to 9) plus P1-E03 D (draws 10 to 29) when present."""
        d = self.d_e3_more()
        if len(d):
            return d
        return self.e3_summary()


def interp_crossing(shares, values, threshold) -> float | None:
    """Smallest share at which ``values`` reach ``threshold``, interpolated on a log share axis."""
    shares, values = np.asarray(shares, float), np.asarray(values, float)
    if values[0] <= threshold:
        return float(shares[0])
    for i in range(1, len(shares)):
        if values[i] <= threshold < values[i - 1]:
            l0, l1 = np.log(shares[i - 1]), np.log(shares[i])
            return float(np.exp(l0 + (values[i - 1] - threshold) / (values[i - 1] - values[i]) * (l1 - l0)))
    return None
