"""Classical random-walk quantities: stationary law, hitting times, diffusion."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def _validate_transition(P: np.ndarray) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("P must be a square matrix")
    if not np.allclose(P.sum(axis=1), 1.0):
        raise ValueError("rows of P must sum to one")
    if np.any(P < -1e-12):
        raise ValueError("P must be non-negative")
    return P


def stationary_distribution(P: np.ndarray) -> np.ndarray:
    P = _validate_transition(P)
    n = P.shape[0]
    system = np.vstack([P.T - np.eye(n), np.ones(n)])
    target = np.zeros(n + 1)
    target[-1] = 1.0
    solution, *_ = np.linalg.lstsq(system, target, rcond=None)
    solution = np.clip(solution, 0.0, None)
    total = solution.sum()
    if total <= 0.0:
        raise ValueError("failed to find a stationary distribution")
    return solution / total


def hitting_times(P: np.ndarray, marked: Iterable[int]) -> np.ndarray:
    P = _validate_transition(P)
    n = P.shape[0]
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    if marked.size == 0:
        raise ValueError("marked set must be non-empty")
    free = np.setdiff1d(np.arange(n), marked)
    times = np.zeros(n)
    if free.size == 0:
        return times
    system = np.eye(free.size) - P[np.ix_(free, free)]
    times[free] = np.linalg.solve(system, np.ones(free.size))
    return times


def mean_hitting_time(
    P: np.ndarray,
    marked: Iterable[int],
    stationary: np.ndarray | None = None,
) -> float:
    P = _validate_transition(P)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    if stationary is None:
        stationary = stationary_distribution(P)
    times = hitting_times(P, marked)
    free = np.setdiff1d(np.arange(P.shape[0]), marked)
    mass = stationary[free].sum()
    if mass <= 0.0:
        return 0.0
    return float(np.dot(stationary[free], times[free]) / mass)


def monte_carlo_hitting_time(
    P: np.ndarray,
    marked: Iterable[int],
    n_samples: int = 10000,
    max_steps: int = 100000,
    seed: int | None = None,
) -> dict[str, float]:
    P = _validate_transition(P)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    n = P.shape[0]
    rng = np.random.default_rng(seed)
    current = rng.choice(n, size=n_samples, p=stationary_distribution(P))
    hit_times = np.full(n_samples, np.nan)
    active = np.ones(n_samples, dtype=bool)
    cumulative = np.cumsum(P, axis=1)
    for step in range(1, max_steps + 1):
        if not np.any(active):
            break
        draw = rng.random(active.sum())
        rows = current[active]
        choices = (cumulative[rows] > draw[:, None]).argmax(axis=1)
        current[active] = choices
        newly_hit = active & np.isin(current, marked)
        hit_times[newly_hit] = step
        active &= ~newly_hit
    found = np.isfinite(hit_times)
    return {
        "mean": float(np.mean(hit_times[found])) if np.any(found) else float("inf"),
        "fraction_found": float(found.mean()),
        "censored": int((~found).sum()),
    }


def hit_probability_curve(
    P: np.ndarray,
    marked: Iterable[int],
    initial: np.ndarray,
    max_steps: int,
) -> np.ndarray:
    P = _validate_transition(P)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    initial = np.asarray(initial, dtype=float)
    if initial.shape != (P.shape[0],):
        raise ValueError("initial must be a distribution over vertices")
    free = np.setdiff1d(np.arange(P.shape[0]), marked)
    submatrix = P[np.ix_(free, free)]
    survival = initial[free].copy()
    curve = np.empty(max_steps + 1)
    curve[0] = 1.0 - survival.sum()
    for step in range(1, max_steps + 1):
        survival = survival @ submatrix
        curve[step] = 1.0 - survival.sum()
    return np.clip(curve, 0.0, 1.0)


def diffusion(P: np.ndarray, initial: np.ndarray, steps: int) -> np.ndarray:
    P = _validate_transition(P)
    distribution = np.asarray(initial, dtype=float).copy()
    for _ in range(steps):
        distribution = distribution @ P
    return distribution


def diffusion_trajectory(P: np.ndarray, initial: np.ndarray, steps: int) -> np.ndarray:
    P = _validate_transition(P)
    trajectory = np.empty((steps + 1, P.shape[0]))
    trajectory[0] = np.asarray(initial, dtype=float)
    for step in range(1, steps + 1):
        trajectory[step] = trajectory[step - 1] @ P
    return trajectory
