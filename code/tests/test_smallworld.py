import networkx as nx
import numpy as np

from src.experiments import run_e6, summarize_e6
from src.graphs import barabasi_albert, connected_watts_strogatz


def test_connected_watts_strogatz_is_connected_and_regular_at_beta_zero():
    graph = connected_watts_strogatz(32, 4, 0.0, seed=1)
    assert nx.is_connected(graph)
    assert {degree for _, degree in graph.degree()} == {4}


def test_rewiring_reduces_clustering_and_path_length():
    ring = connected_watts_strogatz(64, 4, 0.0, seed=2)
    rewired = connected_watts_strogatz(64, 4, 0.5, seed=2)
    assert nx.average_clustering(rewired) < nx.average_clustering(ring)
    assert nx.average_shortest_path_length(rewired) < nx.average_shortest_path_length(ring)


def test_barabasi_albert_is_connected_with_hubs():
    graph = barabasi_albert(64, 2, seed=3)
    degrees = np.array([degree for _, degree in graph.degree()])
    assert nx.is_connected(graph)
    assert degrees.max() > 3 * degrees.mean()


def test_e6_smoke_run_has_expected_columns():
    base = {
        "agjk": {
            "interpolation_grid": [0.9, 0.99],
            "time_window_sqrt_ht": 3.0,
            "time_window_padding": 5,
        },
        "walk": {"laziness": 0.1},
    }
    experiment = {
        "experiments": {
            "E6": {
                "watts_strogatz": {"n": [16], "k": 4, "beta": [0.0, 1.0]},
                "barabasi_albert": {"n": [16], "m": 2},
                "seeds": [0],
                "targets": ["hub", "peripheral"],
            }
        }
    }
    frame = run_e6(base, experiment)
    assert len(frame) == 2 * 2 + 2
    assert {"HT", "t_q", "p_max", "speedup", "clustering", "target_degree"}.issubset(frame.columns)
    assert (frame["speedup"] > 0.0).all()
    summary = summarize_e6(frame)
    assert len(summary) == 6
