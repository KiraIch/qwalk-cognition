import networkx as nx
import numpy as np
import pytest

from src.classical import (
    diffusion,
    diffusion_trajectory,
    hit_probability_curve,
    hitting_times,
    mean_hitting_time,
    monte_carlo_hitting_time,
    stationary_distribution,
)
from src.graphs import (
    complete_graph,
    cycle_graph,
    independent_marked,
    toy_semantic_graph,
    transition_matrix,
)


def test_complete_graph_hitting_time():
    for n in (8, 16):
        P = transition_matrix(complete_graph(n))
        times = hitting_times(P, [0])
        assert np.allclose(times[1:], n - 1)
        assert times[0] == 0.0
        assert np.isclose(mean_hitting_time(P, [0]), n - 1)


def test_cycle_hitting_time_formula():
    n = 8
    P = transition_matrix(cycle_graph(n))
    times = hitting_times(P, [0])
    expected = np.array([min(i, n - i) * (n - min(i, n - i)) for i in range(n)], dtype=float)
    assert np.allclose(times, expected)
    assert np.isclose(mean_hitting_time(P, [0]), n * (n + 1) / 6)


def test_stationary_distribution_is_uniform_for_regular_graphs():
    for graph in (complete_graph(8), cycle_graph(8)):
        P = transition_matrix(graph, self_loop=0.1)
        pi = stationary_distribution(P)
        assert np.allclose(pi, 1.0 / len(graph))


def test_toy_semantic_graph_is_connected_and_stationary_is_consistent():
    graph = toy_semantic_graph()
    assert nx.is_connected(graph)
    assert graph.number_of_nodes() == 19
    assert all("concept" in data for _, data in graph.nodes(data=True))
    P = transition_matrix(graph, self_loop=0.1)
    pi = stationary_distribution(P)
    assert np.allclose(pi @ P, pi)


def test_hit_probability_curve_is_monotone_and_normalized():
    P = transition_matrix(cycle_graph(6), self_loop=0.2)
    initial = stationary_distribution(P)
    curve = hit_probability_curve(P, [0], initial, 200)
    assert np.all(np.diff(curve) >= -1e-12)
    assert 0.0 <= curve[0] <= 1.0
    assert curve[-1] > 0.99


def test_diffusion_preserves_total_probability():
    P = transition_matrix(cycle_graph(6))
    initial = np.ones(6) / 6
    final = diffusion(P, initial, 25)
    assert np.isclose(final.sum(), 1.0)
    trajectory = diffusion_trajectory(P, initial, 5)
    assert trajectory.shape == (6, 6)
    assert np.allclose(trajectory.sum(axis=1), 1.0)


def test_monte_carlo_hitting_time_matches_exact():
    P = transition_matrix(complete_graph(8))
    exact = mean_hitting_time(P, [0])
    estimate = monte_carlo_hitting_time(P, [0], n_samples=4000, max_steps=500, seed=7)
    assert estimate["fraction_found"] > 0.99
    assert abs(estimate["mean"] - exact) / exact < 0.1


def test_independent_marked_set_has_requested_size():
    graph = cycle_graph(12)
    marked = independent_marked(graph, 3, seed=1)
    assert len(set(marked)) == 3
    with pytest.raises(ValueError):
        independent_marked(graph, 13, seed=1)
