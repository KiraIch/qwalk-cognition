import pytest
import numpy as np

from src.cognitive import (
    absorbing_option_curve,
    decision_summary,
    first_passage_summary,
    quantum_option_curve,
    time_averaged_choice,
)
from src.noise import basis_ensembles, detection_curve, detection_option_curve, pure_ensemble
from src.szegedy import walk_operator_blocks
from src.graphs import branched_decision_graph, transition_matrix


def test_branched_decision_graph_structure():
    graph, terminals, branches = branched_decision_graph([4, 4, 4], coupling_pair=(1, 2), coupling_weight=0.5)
    assert graph.number_of_nodes() == 13
    assert terminals == (4, 8, 12)
    assert [len(branch) for branch in branches] == [4, 4, 4]
    assert graph.has_edge(branches[1][0], branches[2][0])
    assert graph[branches[1][0]][branches[2][0]]["weight"] == 0.5
    assert not graph.has_edge(branches[0][0], branches[1][0])


def test_classical_option_curve_is_monotone_and_normalized():
    graph, terminals, _ = branched_decision_graph([3, 3, 3], coupling_pair=(1, 2), coupling_weight=0.5)
    P = transition_matrix(graph, weight="weight")
    initial = np.zeros(P.shape[0])
    initial[0] = 1.0
    curve = absorbing_option_curve(P, [[terminal] for terminal in terminals], initial, 200)
    total = curve.sum(axis=1)
    assert np.all(np.diff(total) >= -1e-12)
    assert np.isclose(total[-1], 1.0, atol=1e-6)


def test_quantum_option_curve_is_bounded():
    graph, terminals, _ = branched_decision_graph([4, 4, 4], coupling_pair=(1, 2), coupling_weight=0.5)
    P = transition_matrix(graph, weight="weight")
    initial = np.zeros(P.shape[0])
    initial[0] = 1.0
    curve = quantum_option_curve(P, [[terminal] for terminal in terminals], initial, 0.9, 120)
    total = curve.sum(axis=1)
    assert curve.shape == (121, 3)
    assert np.all(curve >= -1e-12)
    assert np.all(total <= 1.0 + 1e-9)
    assert total.max() >= 0.5


def test_decision_summary_uses_first_threshold_crossing():
    curve = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.1, 0.2, 0.0],
            [0.2, 0.4, 0.1],
            [0.3, 0.6, 0.2],
        ]
    )
    summary = decision_summary(curve, threshold=0.5)
    assert summary["decision_time"] == 2
    assert np.isclose(sum(summary["choice_probabilities"]), 1.0)
    assert np.isclose(summary["total_probability"], 0.7)
    assert 0.0 <= summary["choice_entropy"] <= np.log2(3)


def _decision_setup(coupling=0.5, steps=60, s=0.9):
    graph, terminals, _ = branched_decision_graph([3, 3, 3], coupling_pair=(1, 2), coupling_weight=coupling)
    P = transition_matrix(graph, weight="weight")
    options = [[terminal] for terminal in terminals]
    nodes = sorted(terminals)
    initial = np.zeros(P.shape[0])
    initial[0] = 1.0
    blocks = walk_operator_blocks(P)
    positions, success = basis_ensembles(P, nodes, s, steps, blocks)
    pure_positions, pure_success = pure_ensemble(P, nodes, s, steps, initial, blocks)
    return P, options, nodes, initial, positions, success, pure_positions, pure_success


def test_detection_option_curve_limits():
    P, options, nodes, initial, positions, success, pure_positions, pure_success = _decision_setup()
    steps = positions.shape[1] - 1
    coherent = quantum_option_curve(P, options, initial, 0.9, steps)
    assert np.allclose(detection_option_curve(0.0, steps, positions, pure_positions, options), coherent)
    by_option = detection_option_curve(0.3, steps, positions, pure_positions, options)
    combined = detection_curve(0.3, steps, positions, success, pure_positions, pure_success, nodes)
    assert np.allclose(by_option.sum(axis=1), combined)
    found = detection_option_curve(0.3, steps, positions, pure_positions, options, final_readout=False)
    assert np.all(np.diff(found, axis=0) >= -1e-12)
    assert np.all(found <= by_option + 1e-12)


def test_detection_option_curve_rejects_overlapping_options():
    P, options, nodes, initial, positions, success, pure_positions, pure_success = _decision_setup(steps=5)
    with pytest.raises(ValueError):
        detection_option_curve(0.3, 5, positions, pure_positions, [options[0], options[0]])


def test_time_averaged_choice_and_first_passage_summary():
    curve = np.array([[0.0, 0.0], [0.2, 0.0], [0.0, 0.2], [0.4, 0.0]])
    assert np.allclose(time_averaged_choice(curve, 3), [0.75, 0.25])
    monotone = np.array([[0.0, 0.0], [0.2, 0.0], [0.3, 0.3], [0.4, 0.4]])
    summary = first_passage_summary(monotone, 3)
    assert np.allclose(summary["choice_probabilities"], [0.5, 0.5])
    assert np.isclose(summary["decided"], 0.8)
    assert np.isclose(summary["mean_time"], (1 * 0.2 + 2 * 0.4 + 3 * 0.2) / 0.8)
    assert summary["median_time"] == 2


def test_weight_jitter_is_seeded_and_bounded():
    first, _, _ = branched_decision_graph([3, 3, 3], (1, 2), 0.5, weight_jitter=0.2, seed=3)
    second, _, _ = branched_decision_graph([3, 3, 3], (1, 2), 0.5, weight_jitter=0.2, seed=3)
    base, _, _ = branched_decision_graph([3, 3, 3], (1, 2), 0.5)
    for u, v, data in first.edges(data=True):
        assert data["weight"] == second[u][v]["weight"]
        ratio = data["weight"] / base[u][v]["weight"]
        assert 0.8 <= ratio <= 1.2
