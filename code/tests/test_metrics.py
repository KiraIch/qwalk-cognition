import numpy as np
import pytest

from src.metrics import (
    bootstrap_confidence_interval,
    choice_probabilities,
    deadline_win_rate,
    entropy,
    first_passage_time,
    normalized_entropy,
    oscillation_index,
    power_law_fit,
    success_metrics,
    time_averaged_success,
)


def test_success_metrics():
    curve = np.array([0.0, 0.1, 0.4, 0.8, 0.6])
    metrics = success_metrics(curve, threshold=0.5)
    assert metrics["p_max"] == 0.8
    assert metrics["t_opt"] == 3
    assert metrics["t_threshold"] == 3


def test_power_law_fit_recovers_exponent():
    x = np.array([1.0, 2.0, 4.0, 8.0])
    y = 3.0 * x**2
    fit = power_law_fit(x, y)
    assert np.isclose(fit["exponent"], 2.0)
    assert np.isclose(fit["prefactor"], 3.0)
    assert np.isclose(fit["r_squared"], 1.0)


def test_entropy_of_uniform_distribution():
    p = np.ones(8) / 8
    assert np.isclose(entropy(p), 3.0)
    assert np.isclose(normalized_entropy(p), 1.0)


def test_choice_probabilities_and_first_passage_time():
    distribution = np.array([0.1, 0.2, 0.3, 0.4])
    probabilities = choice_probabilities(distribution, [[0, 1], [2, 3]])
    assert np.allclose(probabilities, [0.3, 0.7])
    assert first_passage_time([0.0, 0.2, 0.6, 0.9], 0.5) == 2
    assert first_passage_time([0.0, 0.2], 0.5) == -1


def test_bootstrap_interval_contains_sample_mean():
    rng = np.random.default_rng(3)
    samples = rng.normal(loc=2.0, scale=0.5, size=200)
    low, high = bootstrap_confidence_interval(samples, n_resamples=500, seed=4)
    assert low < samples.mean() < high


def test_power_law_rejects_non_positive_values():
    with pytest.raises(ValueError):
        power_law_fit([0.0, 1.0], [1.0, 2.0])


def test_deadline_robustness_metrics():
    curve = np.array([0.0, 0.2, 0.4, 0.2, 0.4])
    flat = np.array([0.0, 0.3, 0.3, 0.3, 0.3])
    assert np.isclose(time_averaged_success(curve, 4), 0.3)
    assert np.isclose(time_averaged_success(curve, 2), 0.3)
    assert np.isclose(oscillation_index(flat, 4), 0.0)
    assert np.isclose(oscillation_index(curve, 4), 0.1 / 0.3)
    assert np.isclose(deadline_win_rate(flat, curve, 4), 0.5)
    with pytest.raises(ValueError):
        time_averaged_success(curve, 5)


def test_power_law_fit_reports_confidence_interval():
    x = np.array([8.0, 16.0, 32.0, 64.0])
    y = x**0.5 * np.array([1.0, 1.05, 0.97, 1.02])
    fit = power_law_fit(x, y)
    low, high = fit["exponent_ci95"]
    assert low < 0.5 < high
    assert fit["exponent_se"] > 0.0
