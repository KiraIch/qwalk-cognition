"""Partial measurement and dephasing models for open-system walks."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np

from .agjk import apply_interpolated_walk, interpolated_initial_state
from .szegedy import apply_walk, walk_operator_blocks


def vertex_distribution(state: np.ndarray) -> np.ndarray:
    state = np.asarray(state)
    return np.sum(np.abs(state) ** 2, axis=0)


def sample_vertex(state: np.ndarray, rng: np.random.Generator) -> int:
    distribution = vertex_distribution(state)
    distribution = distribution / distribution.sum()
    return int(rng.choice(distribution.size, p=distribution))


def reset_to_vertex(state: np.ndarray, vertex: int) -> np.ndarray:
    state = np.asarray(state, dtype=complex)
    collapsed = np.zeros_like(state)
    collapsed[0, vertex] = 1.0
    return collapsed


def partial_measurement_step(
    state: np.ndarray,
    measurement_probability: float,
    rng: np.random.Generator,
) -> np.ndarray:
    if not 0.0 <= measurement_probability <= 1.0:
        raise ValueError("measurement_probability must lie in [0, 1]")
    if rng.random() < measurement_probability:
        return reset_to_vertex(state, sample_vertex(state, rng))
    return state


def success_probability_with_measurement(
    P: np.ndarray,
    marked: Iterable[int],
    max_steps: int,
    measurement_probability: float,
    n_trials: int = 1000,
    seed: int | None = None,
) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    rng = np.random.default_rng(seed)
    blocks = walk_operator_blocks(P)
    n = P.shape[0]
    initial = np.zeros((n, n), dtype=complex)
    initial[0, :] = np.sqrt(np.ones(n) / n)
    hits = np.zeros(max_steps + 1)
    for _ in range(n_trials):
        state = initial.copy()
        hits[0] += float(np.sum(np.abs(state[:, marked]) ** 2))
        for step in range(1, max_steps + 1):
            state = partial_measurement_step(state, measurement_probability, rng)
            state = apply_walk(state, P, blocks)
            hits[step] += float(np.sum(np.abs(state[:, marked]) ** 2))
    return hits / n_trials


def basis_ensembles(
    P: np.ndarray,
    marked: Iterable[int],
    s: float,
    max_steps: int,
    blocks: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    P = np.asarray(P, dtype=float)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    n = P.shape[0]
    if blocks is None:
        blocks = walk_operator_blocks(P)
    positions = np.zeros((n, max_steps + 1, n))
    success = np.zeros((n, max_steps + 1))
    for start in range(n):
        state = np.zeros((2, n, n), dtype=complex)
        state[0, 0, start] = 1.0
        for age in range(max_steps + 1):
            distribution = np.sum(np.abs(state) ** 2, axis=(0, 1))
            positions[start, age] = distribution
            success[start, age] = float(distribution[marked].sum())
            state = apply_interpolated_walk(state, P, marked, s, blocks)
    return positions, success


def pure_ensemble(
    P: np.ndarray,
    marked: Iterable[int],
    s: float,
    max_steps: int,
    distribution: np.ndarray,
    blocks: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    P = np.asarray(P, dtype=float)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    if blocks is None:
        blocks = walk_operator_blocks(P)
    state = interpolated_initial_state(P, distribution)
    n = P.shape[0]
    positions = np.zeros((max_steps + 1, n))
    success = np.zeros(max_steps + 1)
    for step in range(max_steps + 1):
        current = np.sum(np.abs(state) ** 2, axis=(0, 1))
        positions[step] = current
        success[step] = float(current[marked].sum())
        state = apply_interpolated_walk(state, P, marked, s, blocks)
    return positions, success


def measurement_curve(
    measurement_probability: float,
    max_steps: int,
    positions: np.ndarray,
    success: np.ndarray,
    pure_positions: np.ndarray,
    pure_success: np.ndarray,
) -> np.ndarray:
    if not 0.0 <= measurement_probability <= 1.0:
        raise ValueError("measurement_probability must lie in [0, 1]")
    n, _, _ = positions.shape
    q0 = 1.0
    q = np.zeros((n, max_steps + 1))
    curve = np.zeros(max_steps + 1)
    curve[0] = pure_success[0]
    for step in range(max_steps):
        new_q = np.zeros_like(q)
        new_q0 = (1.0 - measurement_probability) * q0
        if max_steps >= 2:
            new_q[:, 2:] += (1.0 - measurement_probability) * q[:, 1:-1]
        if q[:, 1:].any():
            new_q[:, 1] += measurement_probability * np.einsum(
                "xa,xay->y", q[:, 1:], positions[:, 1:, :]
            )
        if q0 > 0.0:
            new_q[:, 1] += measurement_probability * q0 * pure_positions[step]
        q0 = new_q0
        q = new_q
        curve[step + 1] = q0 * pure_success[step + 1] + float(
            np.sum(q[:, 1:] * success[:, 1:])
        )
    return curve


def detection_curve(
    measurement_probability: float,
    max_steps: int,
    positions: np.ndarray,
    success: np.ndarray,
    pure_positions: np.ndarray,
    pure_success: np.ndarray,
    marked: Iterable[int],
) -> np.ndarray:
    """Probability that the target has been found by a forced readout at time T.

    Same reset model as measurement_curve, except that an intermediate
    measurement landing on a marked vertex ends the search (it is absorbed into
    the found probability instead of restarting the walk). At the deadline T a
    final readout is always made, so p=0 returns the pure success curve and p=1
    returns the classical first-passage distribution P(tau <= T).
    """
    if not 0.0 <= measurement_probability <= 1.0:
        raise ValueError("measurement_probability must lie in [0, 1]")
    n, _, _ = positions.shape
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    unmarked = np.ones(n, dtype=bool)
    unmarked[marked] = False
    q0 = 1.0
    q = np.zeros((n, max_steps + 1))
    found = 0.0
    curve = np.zeros(max_steps + 1)
    curve[0] = pure_success[0]
    for step in range(max_steps):
        new_q = np.zeros_like(q)
        new_q0 = (1.0 - measurement_probability) * q0
        if max_steps >= 2:
            new_q[:, 2:] += (1.0 - measurement_probability) * q[:, 1:-1]
        landing = np.zeros(n)
        if q[:, 1:].any():
            landing += np.einsum("xa,xay->y", q[:, 1:], positions[:, 1:, :])
        if q0 > 0.0:
            landing += q0 * pure_positions[step]
        found += measurement_probability * float(landing[marked].sum())
        new_q[:, 1] += measurement_probability * np.where(unmarked, landing, 0.0)
        q0 = new_q0
        q = new_q
        curve[step + 1] = found + q0 * pure_success[step + 1] + float(
            np.sum(q[:, 1:] * success[:, 1:])
        )
    return curve


def detection_option_curve(
    measurement_probability: float,
    max_steps: int,
    positions: np.ndarray,
    pure_positions: np.ndarray,
    option_sets: Sequence[Iterable[int]],
    final_readout: bool = True,
) -> np.ndarray:
    """Per-option version of detection_curve for multi-alternative choice.

    A measurement that lands in option set i ends the search with choice i.
    Returns an array of shape (max_steps + 1, n_options) whose row T is the
    probability of having chosen each option by a forced readout at T. With
    final_readout=False only intermediate measurements count, so each column
    is non-decreasing (a first-passage distribution). Option sets must be
    disjoint.
    """
    if not 0.0 <= measurement_probability <= 1.0:
        raise ValueError("measurement_probability must lie in [0, 1]")
    n, _, _ = positions.shape
    options = [np.asarray(sorted(set(int(x) for x in option)), dtype=int) for option in option_sets]
    all_nodes = np.concatenate(options)
    if all_nodes.size != np.unique(all_nodes).size:
        raise ValueError("option sets must be disjoint")
    unmarked = np.ones(n, dtype=bool)
    unmarked[all_nodes] = False

    def per_option(distribution: np.ndarray) -> np.ndarray:
        return np.array([float(distribution[option].sum()) for option in options])

    q0 = 1.0
    q = np.zeros((n, max_steps + 1))
    found = np.zeros(len(options))
    curve = np.zeros((max_steps + 1, len(options)))
    curve[0] = per_option(pure_positions[0]) if final_readout else 0.0
    for step in range(max_steps):
        new_q = np.zeros_like(q)
        new_q0 = (1.0 - measurement_probability) * q0
        if max_steps >= 2:
            new_q[:, 2:] += (1.0 - measurement_probability) * q[:, 1:-1]
        landing = np.zeros(n)
        if q[:, 1:].any():
            landing += np.einsum("xa,xay->y", q[:, 1:], positions[:, 1:, :])
        if q0 > 0.0:
            landing += q0 * pure_positions[step]
        found += measurement_probability * per_option(landing)
        new_q[:, 1] += measurement_probability * np.where(unmarked, landing, 0.0)
        q0 = new_q0
        q = new_q
        if not final_readout:
            curve[step + 1] = found
            continue
        readout = q0 * pure_positions[step + 1]
        if q[:, 1:].any():
            readout = readout + np.einsum("xa,xay->y", q[:, 1:], positions[:, 1:, :])
        curve[step + 1] = found + per_option(readout)
    return curve
