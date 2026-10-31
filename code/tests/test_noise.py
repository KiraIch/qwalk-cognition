import numpy as np

from src.graphs import cycle_graph, transition_matrix
from src.noise import basis_ensembles, detection_curve, measurement_curve, pure_ensemble


def setup_module(module):
    module.P = transition_matrix(cycle_graph(8), self_loop=0.1)
    module.MARKED = [3]
    module.CUE = 0
    module.T = 30
    module.POSITIONS, module.SUCCESS = basis_ensembles(
        module.P, module.MARKED, 0.0, module.T
    )
    initial = np.zeros(module.P.shape[0])
    initial[module.CUE] = 1.0
    module.PURE_POSITIONS, module.PURE_SUCCESS = pure_ensemble(
        module.P, module.MARKED, 0.0, module.T, initial
    )


def test_basis_ensembles_are_distributions():
    assert np.allclose(POSITIONS.sum(axis=2), 1.0)
    assert np.all(SUCCESS >= 0.0)
    assert np.all(SUCCESS <= 1.0 + 1e-12)


def test_fully_measured_walk_is_classical():
    curve = measurement_curve(1.0, T, POSITIONS, SUCCESS, PURE_POSITIONS, PURE_SUCCESS)
    transition = POSITIONS[:, 1, :]
    assert np.allclose(transition, P, atol=1e-10)
    distribution = np.zeros(P.shape[0])
    distribution[CUE] = 1.0
    expected = np.zeros(T + 1)
    for step in range(T + 1):
        expected[step] = distribution[MARKED].sum()
        distribution = distribution @ transition
    assert np.allclose(curve, expected)


def test_zero_measurement_is_pure_quantum_walk():
    curve = measurement_curve(0.0, T, POSITIONS, SUCCESS, PURE_POSITIONS, PURE_SUCCESS)
    assert np.allclose(curve, PURE_SUCCESS)


def test_measurement_curve_is_bounded():
    for probability in (0.1, 0.3, 0.5, 0.9):
        curve = measurement_curve(
            probability, T, POSITIONS, SUCCESS, PURE_POSITIONS, PURE_SUCCESS
        )
        assert np.all(curve >= -1e-12)
        assert np.all(curve <= 1.0 + 1e-12)


def _detection(probability):
    return detection_curve(
        probability, T, POSITIONS, SUCCESS, PURE_POSITIONS, PURE_SUCCESS, MARKED
    )


def test_detection_without_measurement_is_pure_readout():
    assert np.allclose(_detection(0.0), PURE_SUCCESS)


def test_fully_measured_detection_is_classical_first_passage():
    absorbing = P.copy()
    absorbing[MARKED, :] = 0.0
    absorbing[MARKED, MARKED] = 1.0
    distribution = np.zeros(P.shape[0])
    distribution[CUE] = 1.0
    expected = np.zeros(T + 1)
    for step in range(T + 1):
        expected[step] = distribution[MARKED].sum()
        distribution = distribution @ absorbing
    assert np.allclose(_detection(1.0), expected)


def test_detection_is_bounded_and_dominates_readout():
    for probability in (0.1, 0.3, 0.5, 0.9):
        found = _detection(probability)
        readout = measurement_curve(
            probability, T, POSITIONS, SUCCESS, PURE_POSITIONS, PURE_SUCCESS
        )
        assert np.all(found >= readout - 1e-12)
        assert np.all(found <= 1.0 + 1e-12)
