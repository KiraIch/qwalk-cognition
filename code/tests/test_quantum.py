import numpy as np
import pytest

from src.agjk import (
    apply_interpolated_walk,
    ht_extended,
    interpolated_initial_state,
    interpolated_lower_bound,
    interpolated_success_curve,
    interpolated_walk_matrix,
)
from src.classical import mean_hitting_time
from src.graphs import (
    adversarial_torus_marked,
    complete_graph,
    cycle_graph,
    grid_graph,
    hypercube_graph,
    lazy_transition_matrix,
    torus_graph,
    transition_matrix,
)
from src.szegedy import (
    apply_walk,
    check_unitarity,
    chebyshev_lower_bound,
    discriminant_matrix,
    initial_state,
    phase_gap,
    spectral_gap,
    success_probability_curve,
    walk_matrix,
    walk_operator_blocks,
)


@pytest.fixture(params=["complete", "cycle"])
def transition(request):
    if request.param == "complete":
        return transition_matrix(complete_graph(4))
    return transition_matrix(cycle_graph(5), self_loop=0.1)


def test_walk_matrix_is_unitary(transition):
    matrix = walk_matrix(transition)
    assert check_unitarity(matrix)


def test_top_left_block_is_discriminant_matrix(transition):
    matrix = walk_matrix(transition)
    n = transition.shape[0]
    assert np.allclose(matrix[:n, :n], discriminant_matrix(transition))


def test_apply_walk_matches_dense_matrix(transition):
    n = transition.shape[0]
    state = initial_state(transition)
    expected = (walk_matrix(transition) @ state.reshape(-1)).reshape(n, n)
    actual = apply_walk(state, transition)
    assert np.allclose(actual, expected)


def test_norm_is_preserved(transition):
    blocks = walk_operator_blocks(transition)
    state = initial_state(transition)
    for _ in range(10):
        state = apply_walk(state, transition, blocks)
        assert np.isclose(np.linalg.norm(state), 1.0)


def test_success_curve_is_bounded_by_chebyshev_bound(transition):
    marked = [0]
    curve = success_probability_curve(transition, marked, 20)
    bound = chebyshev_lower_bound(transition, marked, 20)
    assert np.all(curve >= -1e-12)
    assert np.all(curve <= 1.0 + 1e-12)
    assert np.all(bound <= curve + 1e-9)


def test_spectral_gap_is_positive(transition):
    gap = spectral_gap(transition)
    assert 0.0 < gap <= 1.0


@pytest.mark.parametrize("graph", [cycle_graph(16), grid_graph(4), hypercube_graph(4)])
def test_laziness_removes_bipartite_zero_gap(graph):
    P = transition_matrix(graph)
    assert spectral_gap(P) < 1e-9
    lazy = lazy_transition_matrix(P, 0.1)
    assert spectral_gap(lazy) > 1e-3
    assert phase_gap(lazy) >= spectral_gap(lazy) - 1e-12


@pytest.mark.parametrize("eta", [0.1, 0.2])
def test_laziness_rescales_hitting_time(eta):
    P = transition_matrix(grid_graph(5))
    ht = mean_hitting_time(P, [12])
    lazy_ht = mean_hitting_time(lazy_transition_matrix(P, eta), [12])
    assert np.isclose(lazy_ht, ht / (1.0 - eta), rtol=1e-8)


def test_interpolated_walk_is_unitary():
    P = transition_matrix(complete_graph(4))
    for s in (0.0, 0.3, 0.9):
        matrix = interpolated_walk_matrix(P, [0], s)
        assert check_unitarity(matrix)


def test_interpolated_walk_preserves_norm():
    P = transition_matrix(cycle_graph(6), self_loop=0.1)
    state = interpolated_initial_state(P)
    for _ in range(10):
        state = apply_interpolated_walk(state, P, [0], 0.5)
        assert np.isclose(np.linalg.norm(state), 1.0)


def test_interpolated_walk_is_stationary_at_zero_interpolation():
    P = transition_matrix(cycle_graph(8), self_loop=0.1)
    curve = interpolated_success_curve(P, [0], 0.0, 20)
    assert np.allclose(curve, 1.0 / P.shape[0])


def test_interpolation_amplifies_the_marked_vertex():
    P = transition_matrix(cycle_graph(8), self_loop=0.1)
    curve = interpolated_success_curve(P, [0], 0.9, 60)
    assert curve.max() > 0.5


def test_interpolated_lower_bound_is_below_success_curve():
    P = transition_matrix(cycle_graph(8), self_loop=0.1)
    curve = interpolated_success_curve(P, [0], 0.5, 60)
    bound = interpolated_lower_bound(P, [0], 0.5, 60)
    assert np.all(bound <= curve + 1e-9)


def test_extended_hitting_time_matches_classical_for_single_marked():
    P = transition_matrix(cycle_graph(8))
    ht = mean_hitting_time(P, [0])
    extended = ht_extended(P, [0], epsilon=1e-6)
    assert np.isclose(extended, ht, rtol=2e-2)


def test_extended_hitting_time_is_at_least_classical_for_multiple_marked():
    P = transition_matrix(grid_graph(4))
    marked = [0, 1, 4, 5]
    ht = mean_hitting_time(P, marked)
    extended = ht_extended(P, marked, epsilon=1e-6)
    assert extended >= 0.95 * ht


def test_torus_and_adversarial_marked_set():
    graph = torus_graph(18)
    assert graph.number_of_nodes() == 324
    assert np.all([degree == 4 for _, degree in graph.degree()])
    marked = adversarial_torus_marked(18, d1=1, k1=7, d=3)
    assert len(marked) == 76
    assert len(set(marked)) == len(marked)
    assert all(0 <= node < 324 for node in marked)
