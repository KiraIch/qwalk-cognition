"""Search, scaling and cognitive metrics."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy import stats as scipy_stats


def success_metrics(probabilities: Sequence[float], threshold: float = 0.5) -> dict[str, float]:
    curve = np.asarray(probabilities, dtype=float)
    if curve.size == 0:
        raise ValueError("empty probability curve")
    peak_index = int(np.argmax(curve))
    crossings = np.flatnonzero(curve >= threshold)
    threshold_time = int(crossings[0]) if crossings.size else -1
    return {
        "p_max": float(curve[peak_index]),
        "t_opt": peak_index,
        "t_threshold": threshold_time,
        "threshold": threshold,
    }


def power_law_fit(x: Sequence[float], y: Sequence[float]) -> dict[str, float]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError("x and y must be one-dimensional and of equal length")
    if np.any(x <= 0.0) or np.any(y <= 0.0):
        raise ValueError("x and y must be positive")
    slope, intercept = np.polyfit(np.log(x), np.log(y), 1)
    predicted = slope * np.log(x) + intercept
    residual = np.log(y) - predicted
    total = np.log(y) - np.log(y).mean()
    r_squared = 1.0 - float(np.dot(residual, residual) / np.dot(total, total))
    result = {
        "exponent": float(slope),
        "prefactor": float(np.exp(intercept)),
        "r_squared": r_squared,
    }
    dof = x.size - 2
    if dof >= 1:
        lx = np.log(x)
        sxx = float(np.sum((lx - lx.mean()) ** 2))
        se = float(np.sqrt(np.dot(residual, residual) / dof / sxx))
        half = float(scipy_stats.t.ppf(0.975, dof)) * se
        result.update(
            {
                "exponent_se": se,
                "exponent_ci95": [float(slope) - half, float(slope) + half],
            }
        )
    return result


def entropy(distribution: Sequence[float], base: float = 2.0) -> float:
    p = np.asarray(distribution, dtype=float)
    p = p[p > 0.0]
    if p.size == 0:
        return 0.0
    return float(-np.sum(p * np.log(p)) / np.log(base))


def normalized_entropy(distribution: Sequence[float]) -> float:
    p = np.asarray(distribution, dtype=float)
    if p.size <= 1:
        return 0.0
    return entropy(p) / np.log2(p.size)


def choice_probabilities(
    distribution: Sequence[float],
    option_sets: Sequence[Sequence[int]],
) -> np.ndarray:
    p = np.asarray(distribution, dtype=float)
    return np.array([float(p[list(option)].sum()) for option in option_sets])


def first_passage_time(curve: Sequence[float], threshold: float = 0.5) -> int:
    crossings = np.flatnonzero(np.asarray(curve, dtype=float) >= threshold)
    return int(crossings[0]) if crossings.size else -1


def area_under_curve(x: Sequence[float], y: Sequence[float]) -> float:
    return float(np.trapezoid(np.asarray(y, dtype=float), np.asarray(x, dtype=float)))


def bootstrap_confidence_interval(
    samples: Sequence[float],
    n_resamples: int = 2000,
    confidence: float = 0.95,
    seed: int | None = None,
) -> tuple[float, float]:
    values = np.asarray(samples, dtype=float)
    if values.size == 0:
        raise ValueError("empty sample")
    rng = np.random.default_rng(seed)
    means = np.empty(n_resamples)
    for index in range(n_resamples):
        means[index] = rng.choice(values, size=values.size, replace=True).mean()
    tail = (1.0 - confidence) / 2.0
    return float(np.quantile(means, tail)), float(np.quantile(means, 1.0 - tail))


def time_averaged_success(curve: Sequence[float], horizon: int) -> float:
    """Mean of p_t over t = 1..horizon: success when the deadline is uniform on that range."""
    values = np.asarray(curve, dtype=float)
    if not 1 <= horizon < values.size:
        raise ValueError("horizon must lie in [1, len(curve) - 1]")
    return float(values[1 : horizon + 1].mean())


def oscillation_index(curve: Sequence[float], horizon: int) -> float:
    """Coefficient of variation of p_t over t = 1..horizon."""
    values = np.asarray(curve, dtype=float)
    if not 1 <= horizon < values.size:
        raise ValueError("horizon must lie in [1, len(curve) - 1]")
    values = values[1 : horizon + 1]
    mean = values.mean()
    return float(values.std() / mean) if mean > 0.0 else float("nan")


def deadline_win_rate(curve: Sequence[float], baseline: Sequence[float], horizon: int) -> float:
    """Fraction of deadlines T in 1..horizon at which curve beats baseline."""
    values = np.asarray(curve, dtype=float)[1 : horizon + 1]
    reference = np.asarray(baseline, dtype=float)[1 : horizon + 1]
    return float(np.mean(values > reference))
