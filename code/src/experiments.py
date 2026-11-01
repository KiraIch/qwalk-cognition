"""Experiment matrix runner.

Reads configs/base.yaml and configs/experiments.yaml, runs the requested
experiments, and writes raw CSV and processed JSON output.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import yaml

from .agjk import ht_extended, interpolated_lower_bound, interpolated_success_curve
from .classical import mean_hitting_time
from .cognitive import (
    absorbing_option_curve,
    decision_summary,
    first_passage_summary,
    quantum_option_curve,
    time_averaged_choice,
)
from .graphs import (
    adversarial_torus_marked,
    barbell_graph,
    barabasi_albert,
    connected_watts_strogatz,
    branched_decision_graph,
    complete_graph,
    cycle_graph,
    grid_graph,
    hypercube_graph,
    lazy_transition_matrix,
    marked_set,
    torus_graph,
    toy_semantic_graph,
    transition_matrix,
)
from .metrics import (
    deadline_win_rate,
    oscillation_index,
    power_law_fit,
    time_averaged_success,
)
from .noise import (
    basis_ensembles,
    detection_curve,
    detection_option_curve,
    measurement_curve,
    pure_ensemble,
)
from .plotting import (
    plot_e1_scaling,
    plot_e1_speedup,
    plot_e2_ht,
    plot_e2_success,
    plot_e3_semantic,
    plot_e4_decision,
    plot_e4_robustness,
    plot_e6_smallworld,
    plot_e5_decoherence,
    plot_e5_robustness,
)
from .semantic import (
    crw_trajectory,
    ctqw_trajectory,
    normalized_laplacian,
    semantic_metrics,
    spectral_gap as laplacian_spectral_gap,
)
from .szegedy import phase_gap, spectral_gap, walk_operator_blocks


def load_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def walk_transition(graph: nx.Graph, base_config: dict, weight: str | None = None) -> np.ndarray:
    """Lazy walk (1 - eta) P + eta I with eta = walk.laziness, used by every walk experiment."""
    eta = float(base_config["walk"]["laziness"])
    return lazy_transition_matrix(transition_matrix(graph, weight=weight), eta)


def e1_cases(experiment_config: dict) -> list[dict]:
    cases: list[dict] = []
    graph_config = experiment_config["experiments"]["E1"]["graphs"]
    for n in graph_config["complete"]["n"]:
        cases.append(
            {
                "family": "complete",
                "parameter": n,
                "N": n,
                "graph": complete_graph(n),
                "marked": 0,
            }
        )
    for n in graph_config["cycle"]["n"]:
        cases.append(
            {
                "family": "cycle",
                "parameter": n,
                "N": n,
                "graph": cycle_graph(n),
                "marked": 0,
            }
        )
    for length in graph_config["grid"]["length"]:
        cases.append(
            {
                "family": "grid",
                "parameter": length,
                "N": length * length,
                "graph": grid_graph(length),
                "marked": (length // 2) * length + (length // 2),
            }
        )
    for dim in graph_config["hypercube"]["dim"]:
        cases.append(
            {
                "family": "hypercube",
                "parameter": dim,
                "N": 2**dim,
                "graph": hypercube_graph(dim),
                "marked": 0,
            }
        )
    return cases


def run_e1(base_config: dict, experiment_config: dict) -> pd.DataFrame:
    s_grid = np.asarray(base_config["agjk"]["interpolation_grid"], dtype=float)
    window = float(base_config["agjk"]["time_window_sqrt_ht"])
    padding = int(base_config["agjk"]["time_window_padding"])
    records: list[dict] = []
    for case in e1_cases(experiment_config):
        P = walk_transition(case["graph"], base_config)
        marked = [case["marked"]]
        ht = mean_hitting_time(P, marked)
        ht_nonlazy = mean_hitting_time(transition_matrix(case["graph"]), marked)
        gap = spectral_gap(P)
        max_steps = int(np.ceil(window * np.sqrt(ht))) + padding
        best_s = float(s_grid[0])
        best_q = -np.inf
        for s in s_grid:
            bound = interpolated_lower_bound(P, marked, float(s), max_steps)
            peak = float(bound.max())
            if peak > best_q:
                best_q = peak
                best_s = float(s)
        curve = interpolated_success_curve(P, marked, best_s, max_steps)
        t_q = int(np.argmax(curve[1:]) + 1)
        p_max = float(curve[t_q])
        records.append(
            {
                "family": case["family"],
                "parameter": case["parameter"],
                "N": case["N"],
                "marked": case["marked"],
                "HT": ht,
                "spectral_gap": gap,
                "phase_gap": phase_gap(P),
                "HT_lazy_ratio": ht / ht_nonlazy,
                "s": best_s,
                "t_q": t_q,
                "p_max": p_max,
                "q_max": best_q,
                "max_steps": max_steps,
                "speedup": ht / t_q,
            }
        )
    return pd.DataFrame.from_records(records)


def summarize_e1(frame: pd.DataFrame) -> dict:
    summary: dict[str, dict] = {}
    for family, group in frame.groupby("family"):
        group = group.sort_values("N")
        summary[family] = {
            "N": group["N"].astype(int).tolist(),
            "HT": group["HT"].astype(float).tolist(),
            "t_q": group["t_q"].astype(int).tolist(),
            "p_max": group["p_max"].astype(float).tolist(),
            "speedup": group["speedup"].astype(float).tolist(),
            "fit_HT_vs_N": power_law_fit(group["N"], group["HT"]),
            "fit_tq_vs_N": power_law_fit(group["N"], group["t_q"]),
            "fit_tq_vs_HT": power_law_fit(group["HT"], group["t_q"]),
        }
    return summary


def e2_cases(experiment_config: dict) -> list[dict]:
    config = experiment_config["experiments"]["E2"]
    cases: list[dict] = []
    for length in config["graphs"]["grid"]["length"]:
        cases.append(
            {
                "family": "grid",
                "parameter": length,
                "N": length * length,
                "graph": grid_graph(length),
                "single": [(length // 2) * length + (length // 2)],
            }
        )
    for n_each in config["graphs"]["barbell"]["n_each"]:
        cases.append(
            {
                "family": "barbell",
                "parameter": n_each,
                "N": 3 * n_each,
                "graph": barbell_graph(n_each),
                "single": [0],
            }
        )
    return cases


def _select_interpolation(
    P: np.ndarray,
    marked: list[int],
    s_grid: np.ndarray,
    max_steps: int,
) -> tuple[float, float]:
    best_s = float(s_grid[0])
    best_q = -np.inf
    for s in s_grid:
        bound = interpolated_lower_bound(P, marked, float(s), max_steps)
        peak = float(bound.max())
        if peak > best_q:
            best_q = peak
            best_s = float(s)
    return best_s, best_q


def run_e2(base_config: dict, experiment_config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    config = experiment_config["experiments"]["E2"]
    s_grid = np.asarray(base_config["agjk"]["interpolation_grid"], dtype=float)
    window = float(base_config["agjk"]["time_window_sqrt_ht"])
    padding = int(base_config["agjk"]["time_window_padding"])
    epsilon = float(base_config["agjk"].get("ht_plus_epsilon", 1e-6))
    marked_size = int(config["marked_size"])
    seeds = [int(seed) for seed in config["seeds"]]
    records: list[dict] = []
    curve_records: list[dict] = []
    for case in e2_cases(experiment_config):
        graph = case["graph"]
        P = walk_transition(graph, base_config)
        blocks = walk_operator_blocks(P)
        for kind in ("single", "independent", "clustered"):
            kind_seeds = [0] if kind == "single" else seeds
            seen_sets: set[tuple[int, ...]] = set()
            for seed in kind_seeds:
                if kind == "single":
                    marked = list(case["single"])
                else:
                    marked = marked_set(graph, kind, k=marked_size, seed=seed)
                    # different seeds can give the same set; average over distinct sets only
                    key = tuple(sorted(marked))
                    if key in seen_sets:
                        continue
                    seen_sets.add(key)
                ht = mean_hitting_time(P, marked)
                ht_plus = ht_extended(P, marked, epsilon=epsilon)
                max_steps = int(np.ceil(window * np.sqrt(ht))) + padding
                best_s, best_q = _select_interpolation(P, marked, s_grid, max_steps)
                curve = interpolated_success_curve(P, marked, best_s, max_steps, blocks=blocks)
                t_q = int(np.argmax(curve[1:]) + 1)
                p_max = float(curve[t_q])
                records.append(
                    {
                        "family": case["family"],
                        "parameter": case["parameter"],
                        "N": case["N"],
                        "kind": kind,
                        "seed": seed,
                        "marked": " ".join(str(node) for node in marked),
                        "k": len(marked),
                        "HT": ht,
                        "HT_plus": ht_plus,
                        "HT_plus_ratio": ht_plus / ht,
                        "s": best_s,
                        "q_max": best_q,
                        "t_q": t_q,
                        "p_max": p_max,
                        "max_steps": max_steps,
                        "speedup": ht / t_q,
                    }
                )
                for step, probability in enumerate(curve):
                    curve_records.append(
                        {
                            "family": case["family"],
                            "parameter": case["parameter"],
                            "N": case["N"],
                            "kind": kind,
                            "seed": seed,
                            "t": step,
                            "p": float(probability),
                        }
                    )
    return pd.DataFrame.from_records(records), pd.DataFrame.from_records(curve_records)


def summarize_e2(frame: pd.DataFrame) -> dict:
    summary: dict[str, dict] = {}
    keys = ["family", "parameter", "N", "kind"]
    for key, group in frame.groupby(keys):
        family, parameter, n_vertices, kind = key
        summary[f"{family}_{parameter}_{kind}"] = {
            "family": family,
            "parameter": int(parameter),
            "N": int(n_vertices),
            "kind": kind,
            "seeds": group["seed"].astype(int).tolist(),
            "n_distinct_sets": int(group["marked"].nunique()),
            "marked_sets": group["marked"].tolist(),
            "HT_mean": float(group["HT"].mean()),
            "HT_std": float(group["HT"].std(ddof=0)),
            "HT_plus_mean": float(group["HT_plus"].mean()),
            "HT_plus_std": float(group["HT_plus"].std(ddof=0)),
            "HT_plus_ratio_mean": float(group["HT_plus_ratio"].mean()),
            "t_q_mean": float(group["t_q"].mean()),
            "t_q_std": float(group["t_q"].std(ddof=0)),
            "p_max_mean": float(group["p_max"].mean()),
            "p_max_std": float(group["p_max"].std(ddof=0)),
            "speedup_mean": float(group["speedup"].mean()),
        }
    return summary


def run_e3(base_config: dict, experiment_config: dict):
    config = experiment_config["experiments"]["E3"]
    graph = toy_semantic_graph()
    labels = {data["concept"]: node for node, data in graph.nodes(data=True)}
    cue_name = config["cue"]
    target_names = list(config["targets"])
    cue = labels[cue_name]
    laplacian, degree, _ = normalized_laplacian(graph)
    gap = laplacian_spectral_gap(laplacian)
    max_time = float(config["time_window_relaxation"]) / gap
    auc_tau = float(config["auc_window_relaxation"])
    times = np.linspace(0.0, max_time, int(config["n_time_points"]))
    initial_quantum = np.zeros(graph.number_of_nodes(), dtype=complex)
    initial_quantum[cue] = 1.0
    initial_classical = np.zeros(graph.number_of_nodes())
    initial_classical[cue] = 1.0
    quantum_states = ctqw_trajectory(laplacian, initial_quantum, times)
    quantum_probabilities = np.abs(quantum_states) ** 2
    classical_probabilities = crw_trajectory(laplacian, degree, initial_classical, times)
    metrics_records: list[dict] = []
    curve_records: list[dict] = []
    for target_name in target_names:
        target = labels[target_name]
        distance = nx.shortest_path_length(graph, cue, target)
        for model, trajectory in (
            ("quantum", quantum_probabilities),
            ("classical", classical_probabilities),
        ):
            metrics = semantic_metrics(trajectory, times, target, graph, cue, gap, auc_tau)
            metrics_records.append(
                {
                    "cue": cue_name,
                    "target": target_name,
                    "target_distance": distance,
                    "model": model,
                    "relaxation_time": 1.0 / gap,
                    **metrics,
                }
            )
            for time, tau, probability in zip(times, gap * times, trajectory[target]):
                curve_records.append(
                    {
                        "cue": cue_name,
                        "target": target_name,
                        "target_distance": distance,
                        "model": model,
                        "t": float(time),
                        "tau": float(tau),
                        "p": float(probability),
                    }
                )
    return (
        pd.DataFrame.from_records(metrics_records),
        pd.DataFrame.from_records(curve_records),
        graph,
        gap,
        cue_name,
        target_names,
    )


def summarize_e3(metrics: pd.DataFrame, gap: float) -> dict:
    return {
        "spectral_gap": gap,
        "relaxation_time": 1.0 / gap,
        "cue": metrics["cue"].iloc[0],
        "targets": metrics["target"].drop_duplicates().tolist(),
        "metrics": metrics.to_dict(orient="records"),
    }


def run_e4(base_config: dict, experiment_config: dict):
    config = experiment_config["experiments"]["E4"]
    s = float(config["interpolation_s"])
    threshold = float(config["decision_threshold"])
    max_steps = int(config["max_steps"])
    coupling_grid = [float(value) for value in config["coupling_grid"]]
    records: list[dict] = []
    choices: list[dict] = []
    curves: list[dict] = []
    for case in config["cases"]:
        case_id = str(case["id"])
        lengths = [int(length) for length in case["branch_lengths"]]
        n_options = len(lengths)
        pair = tuple(int(value) for value in case["coupling_pair"]) if case.get("coupling_pair") else None
        for coupling in coupling_grid:
            graph, terminals, _ = branched_decision_graph(lengths, pair, coupling)
            P = walk_transition(graph, base_config, weight="weight")
            option_sets = [[terminal] for terminal in terminals]
            initial = np.zeros(P.shape[0])
            initial[0] = 1.0
            for model in ("quantum", "classical"):
                if model == "quantum":
                    curve = quantum_option_curve(P, option_sets, initial, s, max_steps)
                else:
                    curve = absorbing_option_curve(P, option_sets, initial, max_steps)
                summary = decision_summary(curve, threshold)
                record = {
                    "case": case_id,
                    "n_options": n_options,
                    "branch_lengths": "-".join(str(length) for length in lengths),
                    "coupling": coupling,
                    "model": model,
                    "s": s if model == "quantum" else None,
                    "decision_time": summary["decision_time"],
                    "total_probability": summary["total_probability"],
                    "max_total": summary["max_total"],
                    "time_max_total": summary["time_max_total"],
                    "choice_entropy": summary["choice_entropy"],
                    "max_choice": summary["max_choice"],
                    "choice_bias": summary["choice_bias"],
                }
                for index, probability in enumerate(summary["choice_probabilities"]):
                    record[f"p{index}"] = float(probability)
                    choices.append(
                        {
                            "case": case_id,
                            "n_options": n_options,
                            "coupling": coupling,
                            "model": model,
                            "option": index,
                            "probability": float(probability),
                        }
                    )
                records.append(record)
                for step in range(max_steps + 1):
                    for index in range(n_options):
                        curves.append(
                            {
                                "case": case_id,
                                "coupling": coupling,
                                "model": model,
                                "t": step,
                                "option": index,
                                "probability": float(curve[step, index]),
                            }
                        )
    return (
        pd.DataFrame.from_records(records),
        pd.DataFrame.from_records(choices),
        pd.DataFrame.from_records(curves),
    )


E4_READOUTS = ("quantum_threshold", "quantum_average", "quantum_detect", "classical")


def e4_readouts(
    P: np.ndarray,
    option_sets: list[list[int]],
    s: float,
    max_steps: int,
    threshold: float,
    detection_probability: float,
) -> dict[str, dict]:
    """Choice probabilities and response time of one decision graph under every readout.

    quantum_threshold is the original first-crossing readout (phase sensitive);
    quantum_average uses a uniform random stopping time on 1..max_steps;
    quantum_detect lets an intermediate measurement at rate p end the decision;
    classical is the absorbing random walk. Times are mean first-passage times
    conditional on deciding by max_steps (NaN when undefined).
    """
    initial = np.zeros(P.shape[0])
    initial[0] = 1.0
    option_nodes = sorted({node for option in option_sets for node in option})
    blocks = walk_operator_blocks(P)
    coherent = quantum_option_curve(P, option_sets, initial, s, max_steps, blocks)
    legacy = decision_summary(coherent, threshold)
    positions, _ = basis_ensembles(P, option_nodes, s, max_steps, blocks)
    pure_positions, _ = pure_ensemble(P, option_nodes, s, max_steps, initial, blocks)
    detected = first_passage_summary(
        detection_option_curve(
            detection_probability,
            max_steps,
            positions,
            pure_positions,
            option_sets,
            final_readout=False,
        ),
        max_steps,
    )
    classical = first_passage_summary(
        absorbing_option_curve(P, option_sets, initial, max_steps), max_steps
    )
    return {
        "quantum_threshold": {
            "choice": np.asarray(legacy["choice_probabilities"]),
            "time": float(legacy["decision_time"]),
            "decided": float(legacy["total_probability"]),
        },
        "quantum_average": {
            "choice": time_averaged_choice(coherent, max_steps),
            "time": float("nan"),
            "decided": float(coherent[1:].sum(axis=1).mean()),
        },
        "quantum_detect": {
            "choice": np.asarray(detected["choice_probabilities"]),
            "time": detected["mean_time"],
            "decided": detected["decided"],
        },
        "classical": {
            "choice": np.asarray(classical["choice_probabilities"]),
            "time": classical["mean_time"],
            "decided": classical["decided"],
        },
    }


def run_e4_robustness(base_config: dict, experiment_config: dict) -> pd.DataFrame:
    """Every readout under the nominal graph, a laziness sweep, and edge-weight jitter."""
    config = experiment_config["experiments"]["E4"]
    robust = config["robustness"]
    s = float(config["interpolation_s"])
    threshold = float(config["decision_threshold"])
    max_steps = int(config["max_steps"])
    detection_probability = float(robust["detection_probability"])
    nominal_eta = float(base_config["walk"]["laziness"])
    jitter = float(robust["weight_jitter"])
    variants = [("nominal", nominal_eta, None)]
    variants += [("laziness", float(eta), None) for eta in robust["laziness_grid"]]
    variants += [("jitter", nominal_eta, int(seed)) for seed in range(int(robust["jitter_seeds"]))]
    records: list[dict] = []
    for case in config["cases"]:
        case_id = str(case["id"])
        lengths = [int(length) for length in case["branch_lengths"]]
        pair = tuple(int(value) for value in case["coupling_pair"])
        uncoupled = [index for index in range(len(lengths)) if index not in pair]
        for coupling in [float(value) for value in config["coupling_grid"]]:
            for variant, eta, seed in variants:
                graph, terminals, _ = branched_decision_graph(
                    lengths,
                    pair,
                    coupling,
                    weight_jitter=jitter if seed is not None else 0.0,
                    seed=seed,
                )
                P = lazy_transition_matrix(transition_matrix(graph, weight="weight"), eta)
                option_sets = [[terminal] for terminal in terminals]
                readouts = e4_readouts(
                    P, option_sets, s, max_steps, threshold, detection_probability
                )
                for readout, result in readouts.items():
                    choice = result["choice"]
                    record = {
                        "case": case_id,
                        "n_options": len(lengths),
                        "coupling": coupling,
                        "variant": variant,
                        "eta": eta,
                        "seed": -1 if seed is None else seed,
                        "readout": readout,
                        "p_uncoupled": float(choice[uncoupled].sum()),
                        "time": result["time"],
                        "decided": result["decided"],
                    }
                    for index, probability in enumerate(choice):
                        record[f"p{index}"] = float(probability)
                    records.append(record)
    return pd.DataFrame.from_records(records)


def summarize_e4_robustness(frame: pd.DataFrame) -> dict:
    """Spread of P(uncoupled) across laziness and jitter variants, per readout."""
    spread = (
        frame[frame["variant"] != "nominal"]
        .groupby(["readout", "case", "coupling"])["p_uncoupled"]
        .agg(lambda values: float(values.max() - values.min()))
        .rename("spread")
        .reset_index()
    )
    per_readout = spread.groupby("readout")["spread"].agg(["median", "max"]).to_dict(orient="index")
    nominal = frame[frame["variant"] == "nominal"]
    monotone: dict[str, dict] = {}
    for (readout, case), group in nominal.groupby(["readout", "case"]):
        values = group.sort_values("coupling")["p_uncoupled"].to_numpy()
        steps = np.diff(values)
        monotone.setdefault(readout, {})[case] = bool(np.all(steps >= -1e-3))
    return {
        "spread_by_readout": per_readout,
        "monotone_in_coupling": monotone,
        "nominal": nominal.to_dict(orient="records"),
    }


def summarize_e4(frame: pd.DataFrame, threshold: float) -> dict:
    return {
        "decision_threshold": threshold,
        "cases": frame["case"].drop_duplicates().tolist(),
        "coupling_grid": frame["coupling"].drop_duplicates().tolist(),
        "metrics": frame.to_dict(orient="records"),
    }


def e5_case(case: dict) -> tuple[object, int, list[int]]:
    if case["graph"] == "grid":
        graph = grid_graph(int(case["length"]))
        cue = int(case["cue"])
        targets = [int(target) for target in case["targets"]]
    elif case["graph"] == "toy_semantic":
        graph = toy_semantic_graph()
        labels = {data["concept"]: node for node, data in graph.nodes(data=True)}
        cue = labels[case["cue"]]
        targets = [labels[target] for target in case["targets"]]
    else:
        raise ValueError(f"unknown E5 graph: {case['graph']}")
    return graph, cue, targets


def run_e5(base_config: dict, experiment_config: dict):
    config = experiment_config["experiments"]["E5"]
    s = float(config["interpolation_s"])
    max_steps = int(config["max_steps"])
    deadline = int(config["deadline"])
    horizons = [int(value) for value in config["horizons"]]
    if max(horizons) > max_steps or deadline > max_steps:
        raise ValueError("E5 horizons and deadline must not exceed max_steps")
    if 40 not in horizons:
        raise ValueError("E5 horizons must include 40 (used by plot_e5_robustness)")
    probabilities = [float(value) for value in config["measurement_probabilities"]]
    records: list[dict] = []
    curves: list[dict] = []
    for case in config["cases"]:
        case_id = str(case["id"])
        graph, cue, targets = e5_case(case)
        P = walk_transition(graph, base_config)
        blocks = walk_operator_blocks(P)
        positions, success = basis_ensembles(P, targets, s, max_steps, blocks)
        initial = np.zeros(P.shape[0])
        initial[cue] = 1.0
        pure_positions, pure_success = pure_ensemble(
            P, targets, s, max_steps, initial, blocks
        )
        marked_kind = "single" if len(targets) == 1 else "clustered"
        ensemble = (positions, success, pure_positions, pure_success)
        readout = {
            probability: measurement_curve(probability, max_steps, *ensemble)
            for probability in probabilities
        }
        detect = {
            probability: detection_curve(probability, max_steps, *ensemble, targets)
            for probability in probabilities
        }
        baseline = readout[0.0] if 0.0 in readout else None
        for probability in probabilities:
            curve = readout[probability]
            found = detect[probability]
            peak = float(curve.max())
            peak_time = int(np.argmax(curve))
            half = np.flatnonzero(curve >= 0.5 * peak) if peak > 0.0 else np.array([])
            half_time = int(half[0]) if half.size else -1
            record = {
                "case": case_id,
                "graph": case["graph"],
                "marked_kind": marked_kind,
                "n_marked": len(targets),
                "p": probability,
                "p_max": peak,
                "t_opt": peak_time,
                "p_deadline": float(curve[deadline]),
                "t_half_max": half_time,
                "deadline": deadline,
                "oscillation": oscillation_index(curve, max_steps),
                "win_rate": (
                    deadline_win_rate(curve, baseline, max_steps)
                    if baseline is not None
                    else np.nan
                ),
                "detect_max": float(found.max()),
            }
            for horizon in horizons:
                record[f"p_avg_{horizon}"] = time_averaged_success(curve, horizon)
                record[f"detect_{horizon}"] = float(found[horizon])
            records.append(record)
            for step, value in enumerate(curve):
                curves.append(
                    {
                        "case": case_id,
                        "graph": case["graph"],
                        "marked_kind": marked_kind,
                        "p": probability,
                        "t": step,
                        "success": float(value),
                        "detect": float(found[step]),
                    }
                )
    frame = pd.DataFrame.from_records(records)
    for _, group in frame.groupby("case"):
        baseline = group.loc[group["p"] == 0.0, "p_deadline"]
        if len(baseline) and baseline.iloc[0] > 0.0:
            frame.loc[group.index, "p_deadline_ratio"] = group["p_deadline"] / baseline.iloc[0]
        else:
            frame.loc[group.index, "p_deadline_ratio"] = np.nan
    return frame, pd.DataFrame.from_records(curves), deadline


def summarize_e5(frame: pd.DataFrame, deadline: int) -> dict:
    optimal: dict[str, dict] = {}
    for case, group in frame.groupby("case"):
        best = group.loc[group["p_deadline"].idxmax()]
        optimal[case] = {
            "p_opt_deadline": float(best["p"]),
            "p_deadline": float(best["p_deadline"]),
            "p_deadline_ratio": float(best["p_deadline_ratio"]),
        }
    robust_columns = [
        column
        for column in frame.columns
        if column.startswith(("p_avg_", "detect_")) or column == "p_max"
    ]
    best_by_metric: dict[str, dict] = {}
    for case, group in frame.groupby("case"):
        baseline = group.loc[group["p"] == 0.0]
        best_by_metric[case] = {}
        for column in robust_columns:
            best = group.loc[group[column].idxmax()]
            entry = {"p_opt": float(best["p"]), "value": float(best[column])}
            if len(baseline):
                entry["value_at_p0"] = float(baseline[column].iloc[0])
            best_by_metric[case][column] = entry
    return {
        "deadline": deadline,
        "cases": frame["case"].drop_duplicates().tolist(),
        "optimal_at_deadline": optimal,
        "optimal_by_metric": best_by_metric,
        "metrics": frame.to_dict(orient="records"),
    }


def run_e2_adversarial(base_config: dict, experiment_config: dict) -> pd.DataFrame:
    config = experiment_config["experiments"]["E2"]["adversarial_torus"]
    s_grid = np.asarray(base_config["agjk"]["interpolation_grid"], dtype=float)
    window = float(base_config["agjk"]["time_window_sqrt_ht"])
    padding = int(base_config["agjk"]["time_window_padding"])
    epsilon = float(base_config["agjk"].get("ht_plus_epsilon", 1e-6))
    simulate_max_length = int(config.get("simulate_max_length", 0))
    records: list[dict] = []
    for case in config["cases"]:
        length = int(case["length"])
        graph = torus_graph(length)
        P = lazy_transition_matrix(transition_matrix(graph), float(config["laziness"]))
        marked = adversarial_torus_marked(
            length,
            d1=int(case["d1"]),
            k1=int(case["k1"]),
            d=int(case["d"]),
        )
        ht = mean_hitting_time(P, marked)
        ht_plus = ht_extended(P, marked, epsilon=epsilon)
        record = {
            "length": length,
            "N": length * length,
            "d1": int(case["d1"]),
            "k1": int(case["k1"]),
            "d": int(case["d"]),
            "k": len(marked),
            "p_M": len(marked) / (length * length),
            "HT": ht,
            "HT_plus": ht_plus,
            "HT_plus_ratio": ht_plus / ht,
            "s": None,
            "t_q": None,
            "p_max": None,
        }
        if length <= simulate_max_length:
            max_steps = int(np.ceil(window * np.sqrt(ht))) + padding
            best_s, _ = _select_interpolation(P, marked, s_grid, max_steps)
            curve = interpolated_success_curve(P, marked, best_s, max_steps)
            t_q = int(np.argmax(curve[1:]) + 1)
            record.update({"s": best_s, "t_q": t_q, "p_max": float(curve[t_q])})
        records.append(record)
    return pd.DataFrame.from_records(records)


def _json_ready(value):
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return value


def run(config_path: Path, experiment_path: Path, only: list[str] | None) -> None:
    base_config = load_yaml(config_path)
    experiment_config = load_yaml(experiment_path)
    selected = set(only) if only else {"E1", "E2", "E3", "E4", "E5", "E6"}
    root = Path(config_path).resolve().parent.parent
    raw_dir = root / base_config["paths"]["raw"]
    processed_dir = root / base_config["paths"]["processed"]
    figure_dir = root / base_config["paths"]["figures"]
    for directory in (raw_dir, processed_dir, figure_dir):
        directory.mkdir(parents=True, exist_ok=True)
    if "E1" in selected:
        frame = run_e1(base_config, experiment_config)
        raw_path = raw_dir / "E1_scaling.csv"
        frame.to_csv(raw_path, index=False, float_format="%.8g")
        summary = summarize_e1(frame)
        processed_path = processed_dir / "E1_scaling.json"
        with open(processed_path, "w", encoding="utf-8") as handle:
            json.dump(_json_ready(summary), handle, indent=2)
        plot_e1_scaling(frame, summary, figure_dir / "E1_scaling.pdf")
        plot_e1_speedup(frame, figure_dir / "E1_speedup.pdf")
        print(frame.to_string(index=False))
        print(f"saved {raw_path}")
        print(f"saved {processed_path}")
        print(f"saved {figure_dir / 'E1_scaling.pdf'}")
        print(f"saved {figure_dir / 'E1_speedup.pdf'}")
    if "E3" in selected:
        metrics, curves, graph, gap, cue_name, target_names = run_e3(base_config, experiment_config)
        metrics_path = raw_dir / "E3_semantic_metrics.csv"
        curves_path = raw_dir / "E3_semantic_curves.csv"
        metrics.to_csv(metrics_path, index=False, float_format="%.8g")
        curves.to_csv(curves_path, index=False, float_format="%.8g")
        processed_path = processed_dir / "E3_semantic.json"
        summary = summarize_e3(metrics, gap)
        with open(processed_path, "w", encoding="utf-8") as handle:
            json.dump(_json_ready(summary), handle, indent=2)
        plot_e3_semantic(
            graph,
            metrics,
            curves,
            cue_name,
            target_names,
            figure_dir / "E3_semantic.pdf",
        )
        print(metrics.to_string(index=False))
        print(f"saved {metrics_path}")
        print(f"saved {curves_path}")
        print(f"saved {processed_path}")
        print(f"saved {figure_dir / 'E3_semantic.pdf'}")
    if "E4" in selected:
        frame, choices, curves = run_e4(base_config, experiment_config)
        metrics_path = raw_dir / "E4_metrics.csv"
        choices_path = raw_dir / "E4_choices.csv"
        curves_path = raw_dir / "E4_curves.csv"
        frame.to_csv(metrics_path, index=False, float_format="%.8g")
        choices.to_csv(choices_path, index=False, float_format="%.8g")
        curves.to_csv(curves_path, index=False, float_format="%.8g")
        processed_path = processed_dir / "E4_decision.json"
        threshold = float(experiment_config["experiments"]["E4"]["decision_threshold"])
        summary = summarize_e4(frame, threshold)
        with open(processed_path, "w", encoding="utf-8") as handle:
            json.dump(_json_ready(summary), handle, indent=2)
        plot_e4_decision(frame, choices, figure_dir / "E4_decision.pdf")
        robust = run_e4_robustness(base_config, experiment_config)
        robust_path = raw_dir / "E4_robustness.csv"
        robust.to_csv(robust_path, index=False, float_format="%.8g")
        robust_summary = summarize_e4_robustness(robust)
        with open(processed_dir / "E4_robustness.json", "w", encoding="utf-8") as handle:
            json.dump(_json_ready(robust_summary), handle, indent=2)
        plot_e4_robustness(robust, figure_dir / "E4_robustness.pdf")
        print(f"saved {robust_path}")
        print(f"saved {figure_dir / 'E4_robustness.pdf'}")
        print(frame.to_string(index=False))
        print(f"saved {metrics_path}")
        print(f"saved {choices_path}")
        print(f"saved {curves_path}")
        print(f"saved {processed_path}")
        print(f"saved {figure_dir / 'E4_decision.pdf'}")
    if "E6" in selected:
        frame = run_e6(base_config, experiment_config)
        raw_path = raw_dir / "E6_smallworld.csv"
        frame.to_csv(raw_path, index=False, float_format="%.8g")
        summary = summarize_e6(frame)
        processed_path = processed_dir / "E6_smallworld.json"
        with open(processed_path, "w", encoding="utf-8") as handle:
            json.dump(_json_ready(summary), handle, indent=2)
        plot_e6_smallworld(frame, figure_dir / "E6_smallworld.pdf")
        print(f"saved {raw_path}")
        print(f"saved {processed_path}")
        print(f"saved {figure_dir / 'E6_smallworld.pdf'}")
    if "E5" in selected:
        frame, curves, deadline = run_e5(base_config, experiment_config)
        metrics_path = raw_dir / "E5_sweep.csv"
        curves_path = raw_dir / "E5_curves.csv"
        frame.to_csv(metrics_path, index=False, float_format="%.8g")
        curves.to_csv(curves_path, index=False, float_format="%.8g")
        processed_path = processed_dir / "E5_decoherence.json"
        summary = summarize_e5(frame, deadline)
        with open(processed_path, "w", encoding="utf-8") as handle:
            json.dump(_json_ready(summary), handle, indent=2)
        plot_e5_decoherence(frame, curves, deadline, figure_dir / "E5_decoherence.pdf")
        plot_e5_robustness(frame, curves, deadline, figure_dir / "E5_robustness.pdf")
        print(frame.to_string(index=False))
        print(f"saved {metrics_path}")
        print(f"saved {curves_path}")
        print(f"saved {processed_path}")
        print(f"saved {figure_dir / 'E5_decoherence.pdf'}")
        print(f"saved {figure_dir / 'E5_robustness.pdf'}")
    if "E2" in selected:
        frame, curves = run_e2(base_config, experiment_config)
        raw_path = raw_dir / "E2_marked.csv"
        curves_path = raw_dir / "E2_curves.csv"
        frame.to_csv(raw_path, index=False, float_format="%.8g")
        curves.to_csv(curves_path, index=False, float_format="%.8g")
        summary = summarize_e2(frame)
        processed_path = processed_dir / "E2_marked.json"
        with open(processed_path, "w", encoding="utf-8") as handle:
            json.dump(_json_ready(summary), handle, indent=2)
        adversarial = run_e2_adversarial(base_config, experiment_config)
        adversarial_raw = raw_dir / "E2_adversarial_torus.csv"
        adversarial_processed = processed_dir / "E2_adversarial_torus.json"
        adversarial.to_csv(adversarial_raw, index=False, float_format="%.8g")
        with open(adversarial_processed, "w", encoding="utf-8") as handle:
            json.dump(_json_ready(adversarial.to_dict(orient="records")), handle, indent=2)
        plot_e2_success(frame, curves, figure_dir / "E2_success.pdf")
        plot_e2_ht(frame, adversarial, figure_dir / "E2_ht.pdf")
        print(frame.to_string(index=False))
        print(adversarial.to_string(index=False))
        print(f"saved {raw_path}")
        print(f"saved {curves_path}")
        print(f"saved {processed_path}")
        print(f"saved {adversarial_raw}")
        print(f"saved {adversarial_processed}")
        print(f"saved {figure_dir / 'E2_success.pdf'}")
        print(f"saved {figure_dir / 'E2_ht.pdf'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run quantum walk search experiments")
    parser.add_argument("--config", type=Path, default=Path("configs/base.yaml"))
    parser.add_argument("--experiments", type=Path, default=Path("configs/experiments.yaml"))
    parser.add_argument("--only", nargs="*", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(args.config, args.experiments, args.only)


def e6_cases(experiment_config: dict) -> list[dict]:
    config = experiment_config["experiments"]["E6"]
    seeds = [int(seed) for seed in config["seeds"]]
    cases: list[dict] = []
    ws = config["watts_strogatz"]
    for n in ws["n"]:
        for beta in ws["beta"]:
            for seed in seeds:
                cases.append(
                    {
                        "family": "watts_strogatz",
                        "n": int(n),
                        "parameter": float(beta),
                        "seed": seed,
                        "graph": connected_watts_strogatz(int(n), int(ws["k"]), float(beta), seed=seed),
                    }
                )
    ba = config["barabasi_albert"]
    for n in ba["n"]:
        for seed in seeds:
            cases.append(
                {
                    "family": "barabasi_albert",
                    "n": int(n),
                    "parameter": float(ba["m"]),
                    "seed": seed,
                    "graph": barabasi_albert(int(n), int(ba["m"]), seed=seed),
                }
            )
    return cases


def run_e6(base_config: dict, experiment_config: dict) -> pd.DataFrame:
    """Scaling of T_q versus HT on small-world and scale-free graphs.

    For each graph the marked vertex is the highest-degree ("hub") or the
    lowest-degree ("peripheral") vertex; the interpolation parameter is chosen
    exactly as in E1, so the columns are directly comparable to E1.
    """
    config = experiment_config["experiments"]["E6"]
    s_grid = np.asarray(base_config["agjk"]["interpolation_grid"], dtype=float)
    window = float(base_config["agjk"]["time_window_sqrt_ht"])
    padding = int(base_config["agjk"]["time_window_padding"])
    records: list[dict] = []
    for case in e6_cases(experiment_config):
        graph = case["graph"]
        degrees = dict(graph.degree())
        nodes = sorted(graph.nodes())
        P = walk_transition(graph, base_config)
        blocks = walk_operator_blocks(P)
        clustering = float(nx.average_clustering(graph))
        path_length = float(nx.average_shortest_path_length(graph))
        for target_type in config["targets"]:
            if target_type == "hub":
                node = max(nodes, key=lambda v: (degrees[v], -v))
            else:
                node = min(nodes, key=lambda v: (degrees[v], v))
            marked = [node]
            ht = mean_hitting_time(P, marked)
            max_steps = int(np.ceil(window * np.sqrt(ht))) + padding
            best_s, best_q = _select_interpolation(P, marked, s_grid, max_steps)
            curve = interpolated_success_curve(P, marked, best_s, max_steps, blocks=blocks)
            t_q = int(np.argmax(curve[1:]) + 1)
            records.append(
                {
                    "family": case["family"],
                    "n": case["n"],
                    "parameter": case["parameter"],
                    "seed": case["seed"],
                    "target": target_type,
                    "target_degree": degrees[node],
                    "clustering": clustering,
                    "avg_path_length": path_length,
                    "HT": ht,
                    "s": best_s,
                    "q_max": best_q,
                    "t_q": t_q,
                    "p_max": float(curve[t_q]),
                    "speedup": ht / t_q,
                }
            )
    return pd.DataFrame.from_records(records)


def summarize_e6(frame: pd.DataFrame) -> dict:
    summary: dict[str, dict] = {}
    for key, group in frame.groupby(["family", "n", "parameter", "target"]):
        family, n_vertices, parameter, target = key
        summary[f"{family}_{n_vertices}_{parameter:g}_{target}"] = {
            "family": family,
            "N": int(n_vertices),
            "parameter": float(parameter),
            "target": target,
            "clustering": float(group["clustering"].mean()),
            "avg_path_length": float(group["avg_path_length"].mean()),
            "HT_median": float(group["HT"].median()),
            "t_q_median": float(group["t_q"].median()),
            "speedup_median": float(group["speedup"].median()),
            "speedup_min": float(group["speedup"].min()),
            "speedup_max": float(group["speedup"].max()),
            "p_max_min": float(group["p_max"].min()),
        }
    return summary


if __name__ == "__main__":
    main()
