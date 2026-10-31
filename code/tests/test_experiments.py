import numpy as np

from src.experiments import walk_transition
from src.graphs import cycle_graph, lazy_transition_matrix, transition_matrix


def test_walk_transition_uses_configured_laziness():
    graph = cycle_graph(6)
    config = {"walk": {"laziness": 0.1}}
    expected = lazy_transition_matrix(transition_matrix(graph), 0.1)
    assert np.allclose(walk_transition(graph, config), expected)
    assert np.allclose(np.diag(walk_transition(graph, config)), 0.1)
