"""Continuous-time quantum and classical walks on semantic graphs."""

from __future__ import annotations

from collections.abc import Sequence

import networkx as nx
import numpy as np

from .metrics import entropy


def normalized_laplacian(graph: nx.Graph) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    adjacency = nx.to_numpy_array(graph, dtype=float)
    degree = adjacency.sum(axis=1)
    if np.any(degree <= 0.0):
        raise ValueError("graph must have no isolated vertices")
    inverse_sqrt = 1.0 / np.sqrt(degree)
    laplacian = np.eye(adjacency.shape[0]) - inverse_sqrt[:, None] * adjacency * inverse_sqrt[None, :]
    stationary = degree / degree.sum()
    return laplacian, degree, stationary


def random_walk_laplacian(graph: nx.Graph) -> np.ndarray:
    adjacency = nx.to_numpy_array(graph, dtype=float)
    degree = adjacency.sum(axis=1)
    if np.any(degree <= 0.0):
        raise ValueError("graph must have no isolated vertices")
    transition = adjacency / degree[:, None]
    return np.eye(adjacency.shape[0]) - transition


def spectral_gap(laplacian: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvalsh(laplacian)
    positive = eigenvalues[eigenvalues > 1e-12]
    if positive.size == 0:
        return 0.0
    return float(positive[0])


def ctqw_trajectory(
    laplacian: np.ndarray,
    initial: Sequence[complex],
    times: Sequence[float],
) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    coefficients = eigenvectors.T @ np.asarray(initial, dtype=complex)
    times = np.asarray(times, dtype=float)
    phases = np.exp(-1j * np.outer(eigenvalues, times))
    return eigenvectors @ (phases * coefficients[:, None])


def crw_trajectory(
    laplacian: np.ndarray,
    degree: np.ndarray,
    initial: Sequence[float],
    times: Sequence[float],
) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    root_degree = np.sqrt(np.asarray(degree, dtype=float))
    coefficients = eigenvectors.T @ (np.asarray(initial, dtype=float) / root_degree)
    times = np.asarray(times, dtype=float)
    decay = np.exp(-np.outer(eigenvalues, times))
    trajectory = root_degree[:, None] * (eigenvectors @ (decay * coefficients[:, None]))
    trajectory = np.clip(trajectory, 0.0, None)
    return trajectory / trajectory.sum(axis=0, keepdims=True)


def target_curve(trajectory: np.ndarray, target: int) -> np.ndarray:
    return trajectory[target]


def semantic_metrics(
    trajectory: np.ndarray,
    times: Sequence[float],
    target: int,
    graph: nx.Graph,
    cue: int,
    gap: float,
    auc_tau: float | None = None,
) -> dict[str, float]:
    """Activation summary for one target.

    The peak is the global maximum over `times`. `peak_interior` is True only
    if that maximum is not on an end point and the curve later falls below
    (1 - 1%) of it; a plateau approaching stationarity (argmax on rounding
    noise) therefore counts as "no peak". The AUC is taken
    over tau <= auc_tau (default: the whole window) so that it does not depend
    on how long the window is.
    """
    times = np.asarray(times, dtype=float)
    curve = trajectory[target]
    peak = int(np.argmax(curve))
    p_peak = float(curve[peak])
    t_peak = float(times[peak])
    early = gap * times <= (np.inf if auc_tau is None else auc_tau)
    early_auc = float(np.trapezoid(curve[early], times[early]) * gap)
    distribution = np.abs(trajectory[:, peak])
    distribution = distribution / distribution.sum()
    distances = nx.single_source_shortest_path_length(graph, cue)
    radius = float(
        sum(distribution[node] * distances.get(node, 0.0) for node in range(distribution.size))
    )
    return {
        "p_peak": p_peak,
        "t_peak": t_peak,
        "tau_peak": gap * t_peak,
        "auc": early_auc,
        "peak_interior": bool(
            0 < peak < times.size - 1 and curve[peak:].min() < 0.99 * p_peak
        ),
        "entropy_peak": entropy(distribution),
        "coverage_half_peak": float(np.mean(distribution >= 0.5 * p_peak)),
        "expected_radius_peak": radius,
    }
