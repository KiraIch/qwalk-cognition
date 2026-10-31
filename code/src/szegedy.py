"""Szegedy quantum walk: discriminant matrix, walk operator and search curves.

Register convention follows AGJK 2019:

    V(P) |0bar>|x> = sum_y sqrt(P_xy) |y, x>
    Shift |x, y> = |y, x>
    Ref = (2|0bar><0bar| - I) tensor I
    W(P) = V(P)^dagger Shift V(P) Ref

The vertex register is the second register.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np

from .classical import stationary_distribution


def discriminant_matrix(P: np.ndarray) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("P must be square")
    return np.sqrt(P * P.T)


def is_reversible(P: np.ndarray, stationary: np.ndarray | None = None, atol: float = 1e-10) -> bool:
    P = np.asarray(P, dtype=float)
    if stationary is None:
        stationary = stationary_distribution(P)
    flow = stationary[:, None] * P
    return bool(np.allclose(flow, flow.T, atol=atol))


def _householder_completion(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, dtype=complex)
    n = p.size
    reference = np.zeros(n, dtype=complex)
    reference[0] = 1.0
    overlap = np.vdot(reference, p)
    if abs(1.0 - overlap) < 1e-14:
        return np.eye(n, dtype=complex)
    direction = reference - p
    return np.eye(n, dtype=complex) - 2.0 * np.outer(direction, direction.conj()) / np.vdot(
        direction, direction
    ).real


def walk_operator_blocks(P: np.ndarray) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    blocks = np.empty((n, n, n), dtype=complex)
    for vertex in range(n):
        blocks[:, :, vertex] = _householder_completion(np.sqrt(P[vertex]))
    return blocks


def apply_v(state: np.ndarray, blocks: np.ndarray, adjoint: bool = False) -> np.ndarray:
    if adjoint:
        blocks = blocks.conj().transpose(1, 0, 2)
    return np.einsum("ijx,jx->ix", blocks, state, optimize=True)


def apply_reflection(state: np.ndarray) -> np.ndarray:
    reflected = state.copy()
    reflected[1:, :] *= -1.0
    return reflected


def apply_walk(state: np.ndarray, P: np.ndarray, blocks: np.ndarray | None = None) -> np.ndarray:
    if blocks is None:
        blocks = walk_operator_blocks(P)
    reflected = apply_reflection(state)
    stepped = apply_v(reflected, blocks)
    shifted = stepped.T
    return apply_v(shifted, blocks, adjoint=True)


def walk_matrix(P: np.ndarray) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    blocks = walk_operator_blocks(P)
    dimension = n * n
    v_matrix = np.zeros((dimension, dimension), dtype=complex)
    for vertex in range(n):
        projector = np.zeros((n, n), dtype=complex)
        projector[vertex, vertex] = 1.0
        v_matrix += np.kron(blocks[:, :, vertex], projector)
    indices = np.arange(dimension).reshape(n, n)
    shift = np.zeros((dimension, dimension), dtype=complex)
    shift[indices.T.ravel(), indices.ravel()] = 1.0
    signs = np.ones(n)
    signs[1:] = -1.0
    reflection = np.diag(np.repeat(signs, n))
    return v_matrix.conj().T @ shift @ v_matrix @ reflection


def initial_state(P: np.ndarray, distribution: Sequence[float] | None = None) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    if distribution is None:
        distribution = stationary_distribution(P)
    distribution = np.asarray(distribution, dtype=float)
    if distribution.shape != (n,):
        raise ValueError("distribution must have one entry per vertex")
    if np.any(distribution < -1e-12):
        raise ValueError("distribution must be non-negative")
    distribution = np.clip(distribution, 0.0, None)
    distribution = distribution / distribution.sum()
    state = np.zeros((n, n), dtype=complex)
    state[0, :] = np.sqrt(distribution)
    return state


def success_probability_curve(
    P: np.ndarray,
    marked: Iterable[int],
    max_steps: int,
    distribution: Sequence[float] | None = None,
    blocks: np.ndarray | None = None,
) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    if marked.size == 0:
        raise ValueError("marked set must be non-empty")
    if blocks is None:
        blocks = walk_operator_blocks(P)
    state = initial_state(P, distribution)
    curve = np.empty(max_steps + 1)
    curve[0] = float(np.sum(np.abs(state[:, marked]) ** 2))
    for step in range(1, max_steps + 1):
        state = apply_walk(state, P, blocks)
        curve[step] = float(np.sum(np.abs(state[:, marked]) ** 2))
    return curve


def chebyshev_lower_bound(
    P: np.ndarray,
    marked: Iterable[int],
    max_steps: int,
    distribution: Sequence[float] | None = None,
) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    marked = np.asarray(sorted(set(int(x) for x in marked)), dtype=int)
    if distribution is None:
        distribution = stationary_distribution(P)
    root = np.sqrt(np.asarray(distribution, dtype=float))
    matrix = discriminant_matrix(P)
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


def discriminant_spectrum(P: np.ndarray) -> np.ndarray:
    matrix = discriminant_matrix(P)
    if np.allclose(matrix, matrix.T):
        eigenvalues = np.linalg.eigvalsh(matrix)
    else:
        eigenvalues = np.linalg.eigvals(matrix)
    return np.sort(np.real_if_close(eigenvalues))[::-1]


def spectral_gap(P: np.ndarray) -> float:
    eigenvalues = discriminant_spectrum(P)
    if eigenvalues.size < 2:
        return 1.0
    return float(1.0 - np.max(np.abs(eigenvalues[1:])))


def phase_gap(P: np.ndarray) -> float:
    """One-sided gap 1 - lambda_2; unlike spectral_gap it ignores eigenvalues near -1."""
    eigenvalues = discriminant_spectrum(P)
    if eigenvalues.size < 2:
        return 1.0
    return float(1.0 - eigenvalues[1])


def check_unitarity(matrix: np.ndarray, atol: float = 1e-9) -> bool:
    identity = np.eye(matrix.shape[0], dtype=complex)
    return bool(np.allclose(matrix.conj().T @ matrix, identity, atol=atol))
