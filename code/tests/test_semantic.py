import networkx as nx
import numpy as np

from src.graphs import toy_semantic_graph
from src.semantic import (
    crw_trajectory,
    ctqw_trajectory,
    normalized_laplacian,
    semantic_metrics,
    spectral_gap,
)


def test_normalized_laplacian_spectrum():
    graph = toy_semantic_graph()
    laplacian, degree, stationary = normalized_laplacian(graph)
    assert np.allclose(laplacian, laplacian.T)
    eigenvalues = np.linalg.eigvalsh(laplacian)
    assert np.all(eigenvalues >= -1e-12)
    assert np.isclose(eigenvalues[0], 0.0)
    assert 0.0 < spectral_gap(laplacian) < 2.0
    assert np.isclose(stationary.sum(), 1.0)
    assert np.allclose(stationary, degree / degree.sum())


def test_ctqw_preserves_norm():
    graph = toy_semantic_graph()
    laplacian, _, _ = normalized_laplacian(graph)
    initial = np.zeros(graph.number_of_nodes(), dtype=complex)
    initial[0] = 1.0
    times = np.linspace(0.0, 20.0, 51)
    states = ctqw_trajectory(laplacian, initial, times)
    probabilities = np.abs(states) ** 2
    assert np.allclose(probabilities.sum(axis=0), 1.0)


def test_crw_preserves_probability_and_relaxes_to_stationary():
    graph = toy_semantic_graph()
    laplacian, degree, stationary = normalized_laplacian(graph)
    initial = np.zeros(graph.number_of_nodes())
    initial[0] = 1.0
    gap = spectral_gap(laplacian)
    times = np.linspace(0.0, 40.0 / gap, 41)
    trajectory = crw_trajectory(laplacian, degree, initial, times)
    assert np.allclose(trajectory.sum(axis=0), 1.0)
    assert np.allclose(trajectory[:, -1], stationary, atol=1e-5)


def test_semantic_metrics_are_well_formed():
    graph = toy_semantic_graph()
    laplacian, _, _ = normalized_laplacian(graph)
    initial = np.zeros(graph.number_of_nodes(), dtype=complex)
    initial[0] = 1.0
    times = np.linspace(0.0, 30.0, 301)
    states = ctqw_trajectory(laplacian, initial, times)
    probabilities = np.abs(states) ** 2
    metrics = semantic_metrics(probabilities, times, 1, graph, 0, spectral_gap(laplacian))
    assert 0.0 <= metrics["p_peak"] <= 1.0
    assert metrics["tau_peak"] >= 0.0
    assert metrics["entropy_peak"] >= 0.0
    assert 0.0 <= metrics["coverage_half_peak"] <= 1.0
    assert metrics["expected_radius_peak"] >= 0.0


def test_toy_semantic_graph_communities_are_connected():
    graph = toy_semantic_graph()
    assert nx.is_connected(graph)
    concepts = {data["concept"] for _, data in graph.nodes(data=True)}
    assert {"dog", "violin", "airplane"}.issubset(concepts)


def test_monotone_curve_has_no_interior_peak():
    times = np.linspace(0.0, 10.0, 101)
    trajectory = np.vstack([np.linspace(0.0, 1.0, times.size), np.zeros(times.size)])
    metrics = semantic_metrics(trajectory, times, 0, toy_semantic_graph(), 0, 1.0)
    assert metrics["peak_interior"] is False
    assert np.isclose(metrics["t_peak"], 10.0)


def test_plateau_at_stationarity_is_not_a_peak():
    times = np.linspace(0.0, 10.0, 101)
    plateau = 0.5 + 1e-9 * np.sin(np.arange(times.size))
    trajectory = np.vstack([np.concatenate([np.linspace(0.0, 0.5, 50), plateau[50:]]), np.zeros(times.size)])
    metrics = semantic_metrics(trajectory, times, 0, toy_semantic_graph(), 0, 1.0)
    assert metrics["peak_interior"] is False


def test_auc_window_limits_integration_range():
    times = np.linspace(0.0, 20.0, 2001)
    trajectory = np.vstack([np.ones(times.size), np.zeros(times.size)])
    graph = toy_semantic_graph()
    full = semantic_metrics(trajectory, times, 0, graph, 0, 1.0)
    early = semantic_metrics(trajectory, times, 0, graph, 0, 1.0, auc_tau=5.0)
    assert np.isclose(full["auc"], 20.0)
    assert np.isclose(early["auc"], 5.0)
