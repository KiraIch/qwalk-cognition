"""Interpolated walks and AGJK extended hitting time.

Definitions follow AGJK 2019, Sections 2 and 4:

    P' = [[P_UU, P_UM], [0, I]]
    P(s) = (1 - s) P + s P'
    HT(s) = 1/(1 - p_M) sum_k |<v_k(s)|sqrt(pi_U)>|^2 / (1 - lambda_k(s))
    HT^+ = lim_{s -> 1} HT(s)
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from .classical import stationary_distribution
from .szegedy import discriminant_matrix, walk_operator_blocks


def absorbing_transition(P: np.ndarray, marked: Iterable[int]) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    if marked.size == 0:
        raise ValueError("marked set must be non-empty")
    absorbing = P.copy()
    absorbing[marked, :] = 0.0
    absorbing[marked, marked] = 1.0
    return absorbing


def interpolated_transition(P: np.ndarray, marked: Iterable[int], s: float) -> np.ndarray:
    if not 0.0 <= s < 1.0:
        raise ValueError("s must lie in [0, 1)")
    P = np.asarray(P, dtype=float)
    return (1.0 - s) * P + s * absorbing_transition(P, marked)


def interpolated_stationary(
    P: np.ndarray,
    marked: Iterable[int],
    s: float,
    stationary: np.ndarray | None = None,
) -> np.ndarray:
    if stationary is None:
        stationary = stationary_distribution(P)
    stationary = np.asarray(stationary, dtype=float)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    distribution = (1.0 - s) * stationary.copy()
    distribution[marked] = stationary[marked]
    return distribution / (1.0 - s * (1.0 - stationary[marked].sum()))


def interpolated_discriminant(P: np.ndarray, marked: Iterable[int], s: float) -> np.ndarray:
    return discriminant_matrix(interpolated_transition(P, marked, s))


def ht_spectral(
    P: np.ndarray,
    marked: Iterable[int],
    s: float,
    stationary: np.ndarray | None = None,
) -> float:
    if stationary is None:
        stationary = stationary_distribution(P)
    stationary = np.asarray(stationary, dtype=float)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    p_marked = float(stationary[marked].sum())
    matrix = interpolated_discriminant(P, marked, s)
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    root = np.sqrt(stationary)
    root[marked] = 0.0
    total = 0.0
    for index in range(eigenvalues.size):
        if 1.0 - eigenvalues[index] < 1e-12:
            continue
        total += float(np.dot(eigenvectors[:, index], root) ** 2) / (1.0 - eigenvalues[index])
    return total / (1.0 - p_marked)


def ht_extended(
    P: np.ndarray,
    marked: Iterable[int],
    epsilon: float = 1e-6,
    stationary: np.ndarray | None = None,
) -> float:
    return ht_spectral(P, marked, 1.0 - epsilon, stationary)


def _coin(s: float) -> np.ndarray:
    return np.array([[np.sqrt(1.0 - s), -np.sqrt(s)], [np.sqrt(s), np.sqrt(1.0 - s)]])


def interpolated_initial_state(
    P: np.ndarray,
    distribution: np.ndarray | None = None,
) -> np.ndarray:
    if distribution is None:
        distribution = stationary_distribution(P)
    distribution = np.asarray(distribution, dtype=float)
    n = P.shape[0]
    state = np.zeros((2, n, n), dtype=complex)
    state[0, 0, :] = np.sqrt(distribution)
    return state


def apply_interpolated_reflection(state: np.ndarray) -> np.ndarray:
    reflected = -np.asarray(state, dtype=complex)
    reflected[0, 0, :] = -reflected[0, 0, :]
    return reflected


def apply_interpolated_shift(state: np.ndarray) -> np.ndarray:
    shifted = np.asarray(state, dtype=complex).copy()
    shifted[0] = shifted[0].T
    return shifted


def apply_interpolated_v(
    state: np.ndarray,
    blocks: np.ndarray,
    marked: np.ndarray,
    s: float,
    adjoint: bool = False,
) -> np.ndarray:
    state = np.asarray(state, dtype=complex)
    coin = _coin(s)
    if not adjoint:
        transformed = np.einsum("ijx,ajx->aix", blocks, state, optimize=True)
        if marked.size:
            mixed = np.einsum("ab,bim->aim", coin, state[:, :, marked])
            transformed[1][:, marked] = mixed[1]
            transformed[0][:, marked] = np.einsum(
                "ijx,jx->ix", blocks[:, :, marked], mixed[0], optimize=True
            )
        return transformed
    transformed = np.einsum("jix,ajx->aix", blocks.conj(), state, optimize=True)
    if marked.size:
        branch = state[:, :, marked].copy()
        branch[0] = np.einsum(
            "jix,jx->ix", blocks[:, :, marked].conj(), state[0][:, marked], optimize=True
        )
        transformed[:, :, marked] = np.einsum("ba,bim->aim", coin.conj(), branch)
    return transformed


def apply_interpolated_walk(
    state: np.ndarray,
    P: np.ndarray,
    marked: Iterable[int],
    s: float,
    blocks: np.ndarray | None = None,
) -> np.ndarray:
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    if blocks is None:
        blocks = walk_operator_blocks(P)
    reflected = apply_interpolated_reflection(state)
    forward = apply_interpolated_v(reflected, blocks, marked, s)
    shifted = apply_interpolated_shift(forward)
    return apply_interpolated_v(shifted, blocks, marked, s, adjoint=True)


def interpolated_walk_matrix(P: np.ndarray, marked: Iterable[int], s: float) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    n = P.shape[0]
    dimension = 2 * n * n
    blocks = walk_operator_blocks(P)
    matrix = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension):
        state = np.zeros((2, n, n), dtype=complex)
        state.reshape(-1)[index] = 1.0
        evolved = apply_interpolated_walk(state, P, marked, s, blocks)
        matrix[:, index] = evolved.reshape(-1)
    return matrix


def interpolated_success_curve(
    P: np.ndarray,
    marked: Iterable[int],
    s: float,
    max_steps: int,
    distribution: np.ndarray | None = None,
    blocks: np.ndarray | None = None,
) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    if blocks is None:
        blocks = walk_operator_blocks(P)
    state = interpolated_initial_state(P, distribution)
    curve = np.empty(max_steps + 1)
    curve[0] = float(np.sum(np.abs(state[:, :, marked]) ** 2))
    for step in range(1, max_steps + 1):
        state = apply_interpolated_walk(state, P, marked, s, blocks)
        curve[step] = float(np.sum(np.abs(state[:, :, marked]) ** 2))
    return curve


def interpolated_lower_bound(
    P: np.ndarray,
    marked: Iterable[int],
    s: float,
    max_steps: int,
    distribution: np.ndarray | None = None,
) -> np.ndarray:
    if distribution is None:
        distribution = stationary_distribution(P)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    root = np.sqrt(np.asarray(distribution, dtype=float))
    matrix = interpolated_discriminant(P, marked, s)
    previous = root.copy()
    current = matrix @ root
    curve = np.empty(max_steps + 1)
    curve[0] = float(np.sum(np.abs(previous[marked]) ** 2))
    if max_steps >= 1:
        curve[1] = float(np.sum(np.abs(current[marked]) ** 2))
    for step in range(1, max_steps):
        following = 2.0 * (matrix @ current) - previous
        curve[step + 1] = float(np.sum(np.abs(following[marked]) ** 2))
        previous, current = current, following
    return curve
