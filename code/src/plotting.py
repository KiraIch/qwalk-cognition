"""Shared figure style and plotting helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

FAMILY_ORDER = ("complete", "cycle", "grid", "hypercube")
FAMILY_LABELS = {
    "complete": r"Complete graph $K_N$",
    "cycle": r"Cycle $C_N$",
    "grid": r"2D grid $L \times L$",
    "hypercube": r"Hypercube $Q_d$",
}


def set_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
            "legend.fontsize": 7,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "lines.linewidth": 1.4,
            "figure.constrained_layout.use": True,
        }
    )


def save_figure(figure, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, bbox_inches="tight")
    figure.savefig(path.with_suffix(".png"), bbox_inches="tight", dpi=220)


def plot_curve(
    x: np.ndarray,
    y: np.ndarray,
    label: str,
    xlabel: str,
    ylabel: str,
    path: str | Path,
) -> None:
    set_style()
    figure, axis = plt.subplots()
    axis.plot(np.asarray(x), np.asarray(y), label=label)
    axis.set_xlabel(xlabel)
    axis.set_ylabel(ylabel)
    axis.legend()
    save_figure(figure, path)
    plt.close(figure)


def plot_e1_scaling(frame, summary: dict, path: str | Path) -> None:
    set_style()
    figure, axes = plt.subplots(2, 2, figsize=(7.2, 5.6))
    for axis, family in zip(axes.flat, FAMILY_ORDER):
        group = frame[frame["family"] == family].sort_values("N")
        axis.loglog(group["N"], group["HT"], "o-", color="#1f4e79", label="classical $\\mathrm{HT}$")
        axis.loglog(group["N"], group["t_q"], "s-", color="#c55a11", label="quantum $T_q$")
        fit_classical = summary[family]["fit_HT_vs_N"]["exponent"]
        fit_quantum = summary[family]["fit_tq_vs_N"]["exponent"]
        fit_against_ht = summary[family]["fit_tq_vs_HT"]["exponent"]
        axis.set_title(FAMILY_LABELS[family])
        axis.set_xlabel("$N$")
        axis.set_ylabel("steps")
        axis.text(
            0.04,
            0.96,
            f"$\\mathrm{{HT}} \\sim N^{{{fit_classical:.2f}}}$\n"
            f"$T_q \\sim N^{{{fit_quantum:.2f}}}$\n"
            f"$T_q \\sim \\mathrm{{HT}}^{{{fit_against_ht:.2f}}}$",
            transform=axis.transAxes,
            va="top",
            ha="left",
            fontsize=7,
        )
        axis.legend(frameon=False, loc="lower right")
    figure.suptitle("E1: classical versus quantum search time", fontsize=10)
    save_figure(figure, path)
    plt.close(figure)


E2_KIND_ORDER = ("single", "independent", "clustered")
E2_KIND_COLORS = {
    "single": "#1f4e79",
    "independent": "#c55a11",
    "clustered": "#548235",
}
E2_KIND_MARKERS = {"single": "o", "independent": "s", "clustered": "^"}
E2_CASE_ORDER = (("grid", 6), ("grid", 8), ("barbell", 8), ("barbell", 16))


def _e2_case_label(family: str, parameter: int, n_vertices: int) -> str:
    if family == "grid":
        return rf"Grid ${parameter} \times {parameter}$ ($N={n_vertices}$)"
    return rf"Barbell $n_{{\mathrm{{each}}}}={parameter}$ ($N={n_vertices}$)"


def plot_e2_success(frame, curves, path: str | Path) -> None:
    set_style()
    figure, axes = plt.subplots(2, 2, figsize=(7.2, 5.4))
    for axis, (family, parameter) in zip(axes.flat, E2_CASE_ORDER):
        case = curves[(curves["family"] == family) & (curves["parameter"] == parameter)]
        n_vertices = int(case["N"].iloc[0])
        for kind in E2_KIND_ORDER:
            subset = case[case["kind"] == kind]
            if subset.empty:
                continue
            summary = subset.groupby("t")["p"].agg(["mean", "min", "max"])
            axis.plot(
                summary.index,
                summary["mean"],
                color=E2_KIND_COLORS[kind],
                label=kind,
            )
            axis.fill_between(
                summary.index,
                summary["min"],
                summary["max"],
                color=E2_KIND_COLORS[kind],
                alpha=0.18,
                linewidth=0.0,
            )
        axis.set_title(_e2_case_label(family, parameter, n_vertices))
        axis.set_xlabel("walk steps $t$")
        axis.set_ylabel("success probability $p_M(t)$")
        axis.set_ylim(0.0, 1.02)
        axis.legend(frameon=False, fontsize=6, loc="lower right")
    figure.suptitle("E2: single versus multiple marked vertices", fontsize=10)
    save_figure(figure, path)
    plt.close(figure)


def plot_e2_ht(frame, adversarial, path: str | Path) -> None:
    set_style()
    figure, (left, right) = plt.subplots(1, 2, figsize=(7.6, 3.3))
    for kind in E2_KIND_ORDER:
        subset = frame[frame["kind"] == kind]
        grouped = subset.groupby(["family", "parameter", "N"])[["HT", "HT_plus"]].mean().reset_index()
        left.scatter(
            grouped["HT"],
            grouped["HT_plus"],
            marker=E2_KIND_MARKERS[kind],
            color=E2_KIND_COLORS[kind],
            label=kind,
            zorder=3,
        )
        offsets = {"single": (4, 4), "independent": (4, -9), "clustered": (-20, 4)}
        for _, row in grouped.iterrows():
            prefix = "G" if row["family"] == "grid" else "B"
            left.annotate(
                f"{prefix}{int(row['parameter'])}-{kind[0]}",
                (row["HT"], row["HT_plus"]),
                textcoords="offset points",
                xytext=offsets[kind],
                fontsize=6,
            )
    limits = [
        min(frame["HT"].min(), frame["HT_plus"].min()) * 0.7,
        max(frame["HT"].max(), frame["HT_plus"].max()) * 1.4,
    ]
    left.plot(limits, limits, color="0.6", linestyle="--", linewidth=0.8, label="$\\mathrm{HT}=\\mathrm{HT}^+$")
    left.set_xscale("log")
    left.set_yscale("log")
    left.set_xlim(limits)
    left.set_ylim(limits)
    left.set_xlabel("classical $\\mathrm{HT}$")
    left.set_ylabel("extended $\\mathrm{HT}^{+}$")
    left.set_title("Grid and barbell marked sets")
    left.legend(frameon=False, fontsize=6, loc="upper left")

    right.plot(adversarial["N"], adversarial["HT"], "o-", color="#1f4e79", label="classical $\\mathrm{HT}$")
    right.plot(adversarial["N"], adversarial["HT_plus"], "s-", color="#c55a11", label="extended $\\mathrm{HT}^{+}$")
    for _, row in adversarial.iterrows():
        right.annotate(
            f"{row['HT_plus_ratio']:.1f}x",
            (row["N"], row["HT_plus"]),
            textcoords="offset points",
            xytext=(5, 2),
            fontsize=6,
        )
    right.set_xscale("log")
    right.set_yscale("log")
    right.set_xlabel("$N$")
    right.set_ylabel("steps")
    right.set_title("AGJK adversarial torus")
    right.legend(frameon=False, fontsize=6, loc="upper left")
    figure.suptitle("E2: extended hitting time and multiple targets", fontsize=10)
    save_figure(figure, path)
    plt.close(figure)


def plot_e1_speedup(frame, path: str | Path) -> None:
    set_style()
    figure, axis = plt.subplots(figsize=(4.2, 3.0))
    colors = {
        "complete": "#1f4e79",
        "cycle": "#c55a11",
        "grid": "#548235",
        "hypercube": "#7030a0",
    }
    for family in FAMILY_ORDER:
        group = frame[frame["family"] == family].sort_values("N")
        axis.loglog(group["N"], group["speedup"], "o-", color=colors[family], label=FAMILY_LABELS[family])
    axis.axhline(1.0, color="0.5", linestyle="--", linewidth=0.8)
    axis.set_xlabel("$N$")
    axis.set_ylabel("$\\mathrm{HT} / T_q$")
    axis.set_title("Classical-to-quantum speedup")
    axis.legend(frameon=False)
    save_figure(figure, path)
    plt.close(figure)


SEMANTIC_GROUP_COLORS = {
    "animal": "#4c72b0",
    "vehicle": "#dd8452",
    "instrument": "#55a868",
}
SEMANTIC_GROUPS = {
    "animal": {"animal", "dog", "cat", "wolf", "horse", "cow", "bird"},
    "vehicle": {"vehicle", "car", "bus", "train", "bicycle", "airplane"},
    "instrument": {"instrument", "piano", "guitar", "violin", "drum", "flute"},
}


def _semantic_group(concept: str) -> str:
    for group, members in SEMANTIC_GROUPS.items():
        if concept in members:
            return group
    return "animal"


def plot_e3_semantic(
    graph,
    metrics,
    curves,
    cue_name: str,
    target_names,
    path: str | Path,
) -> None:
    set_style()
    figure, axes = plt.subplots(2, 2, figsize=(7.6, 6.2))
    graph_axis = axes[0, 0]
    positions = nx.kamada_kawai_layout(graph)
    concepts = {node: data["concept"] for node, data in graph.nodes(data=True)}
    inverse = {concept: node for node, concept in concepts.items()}
    node_colors = [SEMANTIC_GROUP_COLORS[_semantic_group(concepts[node])] for node in graph.nodes()]
    nx.draw_networkx_edges(graph, positions, ax=graph_axis, edge_color="0.82", width=0.8)
    nx.draw_networkx_nodes(
        graph,
        positions,
        ax=graph_axis,
        node_color=node_colors,
        node_size=230,
        edgecolors="white",
        linewidths=0.6,
    )
    nx.draw_networkx_labels(graph, positions, labels=concepts, ax=graph_axis, font_size=5.5)
    cue = inverse[cue_name]
    targets = [inverse[target] for target in target_names]
    nx.draw_networkx_nodes(
        graph,
        positions,
        nodelist=[cue],
        ax=graph_axis,
        node_shape="*",
        node_size=620,
        node_color="#c00000",
        edgecolors="white",
        linewidths=0.8,
    )
    nx.draw_networkx_nodes(
        graph,
        positions,
        nodelist=targets,
        ax=graph_axis,
        node_shape="s",
        node_size=260,
        node_color="white",
        edgecolors="#c00000",
        linewidths=1.6,
    )
    graph_axis.set_title("Toy semantic graph")
    graph_axis.set_axis_off()

    curve_axes = [axes[0, 1], axes[1, 0]]
    for axis, target_name in zip(curve_axes, target_names[:2]):
        subset = curves[curves["target"] == target_name]
        distance = int(subset["target_distance"].iloc[0])
        for model, label, color in (
            ("quantum", "CTQW", "#c55a11"),
            ("classical", "CRW", "#1f4e79"),
        ):
            model_curve = subset[subset["model"] == model]
            axis.plot(model_curve["tau"], model_curve["p"], color=color, label=label)
            row = metrics[(metrics["target"] == target_name) & (metrics["model"] == model)].iloc[0]
            axis.scatter(
                [row["tau_peak"]],
                [row["p_peak"]],
                color=color,
                s=16,
                zorder=3,
            )
        axis.set_title(f"Cue {cue_name} to {target_name} (distance {distance})")
        axis.set_xlabel(r"$\tau = \lambda_1 t$")
        axis.set_ylabel("target activation $p_T$")
        axis.legend(frameon=False)

    metric_axis = axes[1, 1]
    present_targets = [target for target in target_names if target in metrics["target"].values]
    positions_x = np.arange(len(present_targets))
    width = 0.36
    for index, (model, label, color) in enumerate(
        (("quantum", "CTQW", "#c55a11"), ("classical", "CRW", "#1f4e79"))
    ):
        heights = [
            float(
                metrics[(metrics["target"] == target) & (metrics["model"] == model)]["p_peak"].iloc[0]
            )
            for target in present_targets
        ]
        metric_axis.bar(
            positions_x + (index - 0.5) * width,
            heights,
            width=width,
            color=color,
            label=label,
        )
    metric_axis.set_xticks(positions_x)
    metric_axis.set_xticklabels(present_targets)
    metric_axis.set_ylabel("peak activation")
    metric_axis.set_title("Peak target activation")
    metric_axis.legend(frameon=False)
    figure.suptitle("E3: semantic activation from a cue", fontsize=10)
    save_figure(figure, path)
    plt.close(figure)


E4_OPTION_COLORS = ["#1f4e79", "#c55a11", "#548235", "#7030a0", "#b8860b"]
E4_OPTION_LABELS = ["A", "B", "C", "D", "E"]


def plot_e4_decision(frame, choices, path: str | Path) -> None:
    set_style()
    figure, axes = plt.subplots(2, 2, figsize=(7.4, 5.6))
    panels = (
        ("symmetric3", "quantum", "Symmetric branches, CTQW"),
        ("symmetric3", "classical", "Symmetric branches, CRW"),
        ("asymmetric3", "quantum", "Asymmetric branches, CTQW"),
    )
    for axis, (case, model, title) in zip(axes.flat[:3], panels):
        subset = choices[(choices["case"] == case) & (choices["model"] == model)]
        n_options = int(subset["n_options"].iloc[0])
        for option in range(n_options):
            data = subset[subset["option"] == option].sort_values("coupling")
            axis.plot(
                data["coupling"],
                data["probability"],
                marker="o",
                linestyle=("-", "--", ":", "-.")[option % 4],
                color=E4_OPTION_COLORS[option],
                label=E4_OPTION_LABELS[option],
                markersize=3,
            )
        axis.axhline(1.0 / n_options, color="0.6", linestyle="--", linewidth=0.8)
        axis.set_xlabel("coupling strength $c$")
        axis.set_ylabel("choice probability")
        axis.set_title(title)
        axis.set_ylim(0.0, 1.02)
        axis.legend(frameon=False, fontsize=6)
    time_axis = axes[1, 1]
    styles = {
        ("symmetric3", "quantum"): ("#c55a11", "o", "-"),
        ("symmetric3", "classical"): ("#1f4e79", "o", "-"),
        ("asymmetric3", "quantum"): ("#c55a11", "s", "--"),
        ("asymmetric3", "classical"): ("#1f4e79", "s", "--"),
    }
    for (case, model), (color, marker, linestyle) in styles.items():
        subset = frame[(frame["case"] == case) & (frame["model"] == model)].sort_values("coupling")
        time_axis.plot(
            subset["coupling"],
            subset["decision_time"],
            marker=marker,
            linestyle=linestyle,
            color=color,
            markersize=3,
            label=f"{case} {model}",
        )
    time_axis.set_yscale("log")
    time_axis.set_xlabel("coupling strength $c$")
    time_axis.set_ylabel("decision time")
    time_axis.set_title("Decision time versus coupling")
    time_axis.legend(frameon=False, fontsize=5)
    figure.suptitle("E4: choice probabilities under option coupling", fontsize=10)
    save_figure(figure, path)
    plt.close(figure)


E5_CASE_COLORS = {
    "grid_single": "#1f4e79",
    "grid_clustered": "#2e86c1",
    "toy_single": "#c55a11",
    "toy_clustered": "#e59866",
}
E5_CASE_STYLES = {
    "grid_single": "-",
    "grid_clustered": "--",
    "toy_single": "-",
    "toy_clustered": "--",
}


def plot_e5_decoherence(frame, curves, deadline: int, path: str | Path) -> None:
    set_style()
    figure, axes = plt.subplots(2, 2, figsize=(7.6, 5.6))
    selected_probabilities = [0.0, 0.1, 0.2, 0.5, 1.0]
    colors = plt.cm.viridis(np.linspace(0.05, 0.95, len(selected_probabilities)))
    for axis, case, title in (
        (axes[0, 0], "grid_single", "Grid, single target"),
        (axes[0, 1], "toy_single", "Toy semantic graph, single target"),
    ):
        subset = curves[curves["case"] == case]
        for color, probability in zip(colors, selected_probabilities):
            data = subset[subset["p"] == probability].sort_values("t")
            axis.plot(data["t"], data["success"], color=color, label=f"$p={probability:g}$")
        axis.axvline(deadline, color="0.5", linestyle=":", linewidth=0.9)
        axis.set_xlabel("walk steps $t$")
        axis.set_ylabel("success probability")
        axis.set_title(title)
        axis.legend(frameon=False, fontsize=6)
    metric_axis = axes[1, 0]
    time_axis = axes[1, 1]
    for case, group in frame.groupby("case"):
        group = group.sort_values("p")
        color = E5_CASE_COLORS.get(case, None)
        style = E5_CASE_STYLES.get(case, "-")
        metric_axis.plot(
            group["p"],
            group["p_deadline"],
            marker="o",
            linestyle=style,
            color=color,
            markersize=3,
            label=case,
        )
        best = group.loc[group["p_deadline"].idxmax()]
        metric_axis.scatter(
            [best["p"]],
            [best["p_deadline"]],
            marker="*",
            s=70,
            color=color,
            zorder=4,
        )
        valid = group[group["t_half_max"] >= 0]
        time_axis.plot(
            valid["p"],
            valid["t_half_max"],
            marker="o",
            linestyle=style,
            color=color,
            markersize=3,
            label=case,
        )
    metric_axis.set_xlabel("measurement probability $p$")
    metric_axis.set_ylabel(f"success at $t={deadline}$")
    metric_axis.set_title("Deadline success versus decoherence")
    metric_axis.legend(frameon=False, fontsize=6)
    time_axis.set_yscale("log")
    time_axis.set_xlabel("measurement probability $p$")
    time_axis.set_ylabel("time to half-maximum")
    time_axis.set_title("Search time versus decoherence")
    time_axis.legend(frameon=False, fontsize=6)
    figure.suptitle("E5: decoherence-assisted search", fontsize=10)
    save_figure(figure, path)
    plt.close(figure)


def plot_e5_robustness(
    frame,
    curves,
    deadline: int,
    path: str | Path,
    heat_case: str = "grid_single",
    detect_case: str = "grid_clustered",
    compare_horizon: int = 40,
) -> None:
    set_style()
    figure, axes = plt.subplots(2, 2, figsize=(7.6, 5.6))
    probabilities = sorted(curves["p"].unique())
    heat = (
        curves[curves["case"] == heat_case]
        .pivot(index="p", columns="t", values="success")
        .loc[probabilities]
    )
    heat_axis = axes[0, 0]
    image = heat_axis.imshow(
        heat.to_numpy(),
        aspect="auto",
        origin="lower",
        cmap="viridis",
        extent=(heat.columns.min() - 0.5, heat.columns.max() + 0.5, -0.5, len(probabilities) - 0.5),
    )
    heat_axis.set_yticks(range(len(probabilities)))
    heat_axis.set_yticklabels([f"{value:g}" for value in probabilities])
    heat_axis.axvline(deadline, color="white", linestyle=":", linewidth=0.9)
    heat_axis.set_xlabel("readout time $T$")
    heat_axis.set_ylabel("measurement probability $p$")
    heat_axis.set_title("Readout success $p_T$ (grid, single)")
    figure.colorbar(image, ax=heat_axis, fraction=0.046, pad=0.02)

    detect_axis = axes[0, 1]
    selected = [0.0, 0.1, 0.3, 1.0]
    colors = plt.cm.viridis(np.linspace(0.05, 0.95, len(selected)))
    subset = curves[curves["case"] == detect_case]
    for color, probability in zip(colors, selected):
        data = subset[subset["p"] == probability].sort_values("t")
        label = f"$p={probability:g}$" + (" (classical)" if probability == 1.0 else "")
        detect_axis.plot(data["t"], data["detect"], color=color, label=label)
    detect_axis.set_xlabel("deadline $T$")
    detect_axis.set_ylabel("found by $T$")
    detect_axis.set_title("Detection with absorbing measurement (grid, cluster)")
    detect_axis.legend(frameon=False, fontsize=6)

    optimum_axis = axes[1, 0]
    compare_axis = axes[1, 1]
    for case, group in curves.groupby("case"):
        color = E5_CASE_COLORS.get(case, None)
        style = E5_CASE_STYLES.get(case, "-")
        best = group.loc[group.groupby("t")["detect"].idxmax()]
        # p* is undefined while no rate has found anything yet (all ties at zero).
        best = best[best["detect"] >= 0.01]
        optimum_axis.step(best["t"], best["p"], where="mid", color=color, linestyle=style, label=case)
        rows = frame[frame["case"] == case].sort_values("p")
        compare_axis.plot(
            rows["p"],
            rows[f"detect_{compare_horizon}"],
            marker="o",
            markersize=3,
            color=color,
            linestyle=style,
            label=case,
        )
    optimum_axis.set_xlabel("deadline $T$")
    optimum_axis.set_ylabel("optimal $p^\\ast(T)$")
    optimum_axis.set_title("Best measurement rate versus deadline")
    optimum_axis.legend(frameon=False, fontsize=6)
    compare_axis.set_xlabel("measurement probability $p$")
    compare_axis.set_ylabel(f"found by $T={compare_horizon}$")
    compare_axis.set_title("Detection at a fixed deadline")
    compare_axis.legend(frameon=False, fontsize=6)
    figure.suptitle("E5: coherence versus intermediate measurement", fontsize=10)
    save_figure(figure, path)
    plt.close(figure)


E4_READOUT_STYLES = {
    "quantum_threshold": ("#999999", ":", "quantum, first crossing (v1)"),
    "quantum_average": ("#c55a11", "-", "quantum, random stopping"),
    "quantum_detect": ("#7d3c98", "--", "quantum, detection $p=0.2$"),
    "classical": ("#1f4e79", "-", "classical, absorbing"),
}


def plot_e4_robustness(frame, path: str | Path) -> None:
    set_style()
    figure, axes = plt.subplots(2, 2, figsize=(7.6, 5.8))
    cases = (
        ("symmetric3", "Symmetric, 3 options"),
        ("asymmetric3", "Asymmetric (3-4-5), 3 options"),
        ("symmetric4", "Symmetric, 4 options"),
    )
    for axis, (case, title) in zip(axes.flat[:3], cases):
        subset = frame[frame["case"] == case]
        n_options = int(subset["n_options"].iloc[0])
        for readout, (color, linestyle, label) in E4_READOUT_STYLES.items():
            data = subset[subset["readout"] == readout]
            nominal = data[data["variant"] == "nominal"].sort_values("coupling")
            band = data[data["variant"] != "nominal"].groupby("coupling")["p_uncoupled"]
            low, high = band.min(), band.max()
            axis.fill_between(low.index, low.to_numpy(), high.to_numpy(), color=color, alpha=0.15, linewidth=0)
            axis.plot(
                nominal["coupling"],
                nominal["p_uncoupled"],
                color=color,
                linestyle=linestyle,
                marker="o",
                markersize=2.5,
                label=label,
            )
        axis.axhline((n_options - 2) / n_options, color="0.6", linestyle="--", linewidth=0.8)
        axis.set_xlabel("coupling strength $c$")
        axis.set_ylabel("P(uncoupled option)")
        axis.set_title(title)
        axis.set_ylim(0.0, 1.02)
    axes[0, 0].legend(frameon=False, fontsize=5.5, loc="upper left")
    spread = (
        frame[frame["variant"] != "nominal"]
        .groupby(["readout", "case", "coupling"])["p_uncoupled"]
        .agg(lambda values: values.max() - values.min())
        .reset_index()
    )
    bar_axis = axes[1, 1]
    names = list(E4_READOUT_STYLES)
    medians = [spread.loc[spread["readout"] == name, "p_uncoupled"].median() for name in names]
    maxima = [spread.loc[spread["readout"] == name, "p_uncoupled"].max() for name in names]
    positions = np.arange(len(names))
    bar_axis.bar(positions - 0.18, medians, width=0.36, color=[E4_READOUT_STYLES[n][0] for n in names], label="median")
    bar_axis.bar(positions + 0.18, maxima, width=0.36, color=[E4_READOUT_STYLES[n][0] for n in names], alpha=0.4, label="max")
    bar_axis.set_xticks(positions)
    bar_axis.set_xticklabels(["first\ncrossing", "random\nstopping", "detection", "classical"], fontsize=7)
    bar_axis.set_ylabel("spread of P(uncoupled)")
    bar_axis.set_title("Sensitivity to laziness and weight jitter")
    bar_axis.legend(frameon=False, fontsize=6)
    figure.suptitle("E4: readout robustness under option coupling", fontsize=10)
    save_figure(figure, path)
    plt.close(figure)



def _median_range(values):
    values = np.asarray(values, dtype=float)
    median = float(np.median(values))
    return median, median - float(values.min()), float(values.max()) - median


def plot_e6_smallworld(frame, path: str | Path) -> None:
    set_style()
    figure, axes = plt.subplots(1, 2, figsize=(7.4, 3.2))
    ws = frame[frame["family"] == "watts_strogatz"]
    styles = {"hub": ("#c55a11", "-"), "peripheral": ("#1f4e79", "--")}
    for n_vertices, marker in ((32, "o"), (64, "s")):
        for target, (color, linestyle) in styles.items():
            subset = ws[(ws["n"] == n_vertices) & (ws["target"] == target)]
            betas = sorted(subset["parameter"].unique())
            for axis, column in ((axes[0], "HT"), (axes[1], "speedup")):
                stats = [_median_range(subset[subset["parameter"] == beta][column]) for beta in betas]
                axis.errorbar(
                    betas,
                    [item[0] for item in stats],
                    yerr=[[item[1] for item in stats], [item[2] for item in stats]],
                    color=color,
                    linestyle=linestyle,
                    marker=marker,
                    markersize=3,
                    capsize=2,
                    label=f"N={n_vertices}, {target}",
                )
    for axis, ylabel in ((axes[0], "classical hitting time HT"), (axes[1], r"speedup $HT/T_q$")):
        axis.set_xscale("symlog", linthresh=0.01)
        axis.set_xlabel(r"rewiring probability $\beta$")
        axis.set_ylabel(ylabel)
        axis.legend(frameon=False, fontsize=5.5)
    axes[0].set_yscale("log")
    axes[0].set_title("Hitting time versus rewiring")
    axes[1].set_title("Quantum speedup versus rewiring")
    figure.suptitle("E6: small-world graphs (median and range over 5 seeds)", fontsize=9)
    save_figure(figure, path)
    plt.close(figure)
