"""Positioning error and its statistics."""
from __future__ import annotations

import numpy as np

STAT_NAMES = ["mean", "median", "p75", "p95", "rmse"]


def positioning_error(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Euclidean distance in metres between predicted and true (ECoord, NCoord), per row."""
    return np.linalg.norm(np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float), axis=1)


def error_stats(err: np.ndarray) -> dict:
    """Mean, median, 75th and 95th percentile, and root mean square of the error."""
    err = np.asarray(err, dtype=float)
    return dict(
        mean=float(err.mean()),
        median=float(np.percentile(err, 50)),
        p75=float(np.percentile(err, 75)),
        p95=float(np.percentile(err, 95)),
        rmse=float(np.sqrt(np.mean(err ** 2))),
    )


def mae_per_coordinate(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean absolute error of each coordinate, averaged over the two coordinates."""
    return float(np.abs(np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float)).mean(axis=0).mean())


def bootstrap_mean_difference(err_a: np.ndarray, err_b: np.ndarray, point_ids: np.ndarray,
                              n_resamples: int = 10_000, seed: int = 0, level: float = 0.95) -> dict:
    """Difference in mean positioning error (a minus b) with a bootstrap interval.

    Test points are resampled with replacement; a resampled test point brings all
    of its rows. Both models are evaluated on the same resample (paired).
    """
    err_a, err_b = np.asarray(err_a, dtype=float), np.asarray(err_b, dtype=float)
    points = np.unique(point_ids)
    index = np.searchsorted(points, point_ids)
    counts = np.bincount(index, minlength=len(points)).astype(float)
    sum_a = np.bincount(index, weights=err_a, minlength=len(points))
    sum_b = np.bincount(index, weights=err_b, minlength=len(points))
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(points), size=(n_resamples, len(points)))
    n = counts[draws].sum(axis=1)
    diff = sum_a[draws].sum(axis=1) / n - sum_b[draws].sum(axis=1) / n
    lo, hi = np.percentile(diff, [100 * (1 - level) / 2, 100 * (1 + level) / 2])
    return dict(
        mean_a=float(err_a.mean()), mean_b=float(err_b.mean()),
        diff=float(err_a.mean() - err_b.mean()), ci_low=float(lo), ci_high=float(hi),
        n_resamples=int(n_resamples), n_points=int(len(points)), bootstrap_seed=int(seed),
    )
