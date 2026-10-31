"""Cognitive mapping: target activation, choice probability and response time.

The graph plays the role of a semantic or decision network. The marked set is a
target memory or a decision boundary. Quantum and classical walk statistics are
turned into process-level cognitive quantities, not biological claims.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .agjk import apply_interpolated_walk, interpolated_initial_state
from .metrics import entropy
from .szegedy import walk_operator_blocks


def vertex_distribution(state: np.ndarray) -> np.ndarray:
    state = np.asarray(state)
    if state.ndim != 2:
        raise ValueError("state must be a two-register matrix")
    return np.sum(np.abs(state) ** 2, axis=0)


def activation_curve(
    curves: Sequence[Sequence[float]],
    option_sets: Sequence[Sequence[int]],
) -> np.ndarray:
    activation = np.asarray(curves, dtype=float)
    return np.stack([activation[:, list(option)].sum(axis=1) for option in option_sets], axis=1)


def choice_probabilities(state: np.ndarray, option_sets: Sequence[Sequence[int]]) -> np.ndarray:
    distribution = vertex_distribution(state)
    return np.array([float(distribution[list(option)].sum()) for option in option_sets])


def response_time(curve: Sequence[float], threshold: float = 0.5) -> int:
    crossings = np.flatnonzero(np.asarray(curve, dtype=float) >= threshold)
    return int(crossings[0]) if crossings.size else -1


def absorbing_option_curve(
    P: np.ndarray,
    option_sets: Sequence[Sequence[int]],
    initial: Sequence[float],
    max_steps: int,
) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    option_nodes = sorted({int(node) for option in option_sets for node in option})
    distribution = np.asarray(initial, dtype=float)
    distribution = distribution / distribution.sum()
    absorbing = P.copy()
    absorbing[option_nodes, :] = 0.0
    absorbing[option_nodes, option_nodes] = 1.0
    curve = np.empty((max_steps + 1, len(option_sets)))
    for step in range(max_steps + 1):
        curve[step] = [float(distribution[list(option)].sum()) for option in option_sets]
        distribution = distribution @ absorbing
    return curve


def quantum_option_curve(
    P: np.ndarray,
    option_sets: Sequence[Sequence[int]],
    initial: Sequence[float],
    s: float,
    max_steps: int,
    blocks: np.ndarray | None = None,
) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    option_nodes = np.asarray(
        sorted({int(node) for option in option_sets for node in option}),
        dtype=int,
    )
    distribution = np.asarray(initial, dtype=float)
    distribution = distribution / distribution.sum()
    if blocks is None:
        blocks = walk_operator_blocks(P)
    state = interpolated_initial_state(P, distribution)
    curve = np.empty((max_steps + 1, len(option_sets)))
    for step in range(max_steps + 1):
        curve[step] = [
            float(np.sum(np.abs(state[:, :, list(option)]) ** 2)) for option in option_sets
        ]
        state = apply_interpolated_walk(state, P, option_nodes, s, blocks)
    return curve


def decision_summary(
    curve: Sequence[Sequence[float]],
    threshold: float = 0.5,
) -> dict[str, object]:
    curve = np.asarray(curve, dtype=float)
    total = curve.sum(axis=1)
    crossings = np.flatnonzero(total >= threshold)
    time_max = int(np.argmax(total))
    decision_time = int(crossings[0]) if crossings.size else time_max
    if total[decision_time] > 0.0:
        probabilities = curve[decision_time] / total[decision_time]
    else:
        probabilities = np.full(curve.shape[1], 1.0 / curve.shape[1])
    return {
        "decision_time": decision_time,
        "total_probability": float(total[decision_time]),
        "max_total": float(total[time_max]),
        "time_max_total": time_max,
        "choice_probabilities": probabilities.tolist(),
        "choice_entropy": entropy(probabilities),
        "max_choice": float(probabilities.max()),
        "choice_bias": float(probabilities.max() - 1.0 / curve.shape[1]),
    }


def time_averaged_choice(curve: Sequence[Sequence[float]], horizon: int) -> np.ndarray:
    """Choice distribution under a uniform random stopping time on 1..horizon.

    Averages the option probabilities over t = 1..horizon and renormalizes, so
    the readout no longer depends on the phase of the coherent oscillation.
    """
    curve = np.asarray(curve, dtype=float)
    if not 1 <= horizon < curve.shape[0]:
        raise ValueError("horizon must lie in [1, len(curve) - 1]")
    mean = curve[1 : horizon + 1].mean(axis=0)
    total = mean.sum()
    if total <= 0.0:
        return np.full(curve.shape[1], 1.0 / curve.shape[1])
    return mean / total


def first_passage_summary(curve: Sequence[Sequence[float]], horizon: int) -> dict[str, object]:
    """Choice and response time for a monotone 'decided by T' curve.

    `curve[T, i]` is the probability of having chosen option i by T (absorbing
    classical walk or the detection model). The response-time density is the
    increment of the total; the mean is conditional on deciding by `horizon`.
    """
    curve = np.asarray(curve, dtype=float)[: horizon + 1]
    total = curve.sum(axis=1)
    decided = float(total[-1])
    if decided <= 0.0:
        probabilities = np.full(curve.shape[1], 1.0 / curve.shape[1])
        mean_time = float("nan")
    else:
        probabilities = curve[-1] / decided
        density = np.clip(np.diff(total, prepend=0.0), 0.0, None)
        mean_time = float(np.sum(np.arange(total.size) * density) / density.sum())
    crossings = np.flatnonzero(total >= 0.5)
    return {
        "choice_probabilities": probabilities.tolist(),
        "decided": decided,
        "mean_time": mean_time,
        "median_time": int(crossings[0]) if crossings.size else -1,
    }
