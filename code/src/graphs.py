"""Graph generators, transition matrices and marked-set helpers."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import networkx as nx
import numpy as np


def complete_graph(n: int) -> nx.Graph:
    return nx.complete_graph(n)


def cycle_graph(n: int) -> nx.Graph:
    return nx.cycle_graph(n)


def grid_graph(length: int) -> nx.Graph:
    return nx.convert_node_labels_to_integers(nx.grid_2d_graph(length, length))


def hypercube_graph(dim: int) -> nx.Graph:
    return nx.convert_node_labels_to_integers(nx.hypercube_graph(dim))


def random_regular_graph(n: int, degree: int, seed: int | None = None) -> nx.Graph:
    return nx.random_regular_graph(degree, n, seed=seed)


def barbell_graph(n_each: int) -> nx.Graph:
    return nx.barbell_graph(n_each, n_each)


def torus_graph(length: int) -> nx.Graph:
    return nx.convert_node_labels_to_integers(nx.grid_2d_graph(length, length, periodic=True))


def adversarial_torus_marked(
    length: int,
    d1: int = 1,
    k1: int | None = None,
    d: int | None = None,
) -> list[int]:
    if k1 is None or d is None:
        raise ValueError("k1 and d must be specified")
    if length % d != 0 or d % d1 != 0:
        raise ValueError("require d1 | d and d | length")
    dense = [(row * d1) * length + (column * d1) for row in range(k1) for column in range(k1)]
    sparse = [
        (row * d) * length + (column * d)
        for row in range(length // d)
        for column in range(length // d)
    ]
    return sorted(set(dense) | set(sparse))


TOY_SEMANTIC_NODES: tuple[str, ...] = (
    "animal",
    "dog",
    "cat",
    "wolf",
    "horse",
    "cow",
    "bird",
    "vehicle",
    "car",
    "bus",
    "train",
    "bicycle",
    "airplane",
    "instrument",
    "piano",
    "guitar",
    "violin",
    "drum",
    "flute",
)

TOY_SEMANTIC_EDGES: tuple[tuple[str, str], ...] = (
    ("animal", "dog"),
    ("animal", "cat"),
    ("animal", "wolf"),
    ("animal", "horse"),
    ("animal", "cow"),
    ("animal", "bird"),
    ("dog", "cat"),
    ("dog", "wolf"),
    ("dog", "horse"),
    ("cat", "horse"),
    ("horse", "cow"),
    ("vehicle", "car"),
    ("vehicle", "bus"),
    ("vehicle", "train"),
    ("vehicle", "bicycle"),
    ("vehicle", "airplane"),
    ("car", "bus"),
    ("car", "train"),
    ("car", "bicycle"),
    ("bus", "train"),
    ("train", "airplane"),
    ("instrument", "piano"),
    ("instrument", "guitar"),
    ("instrument", "violin"),
    ("instrument", "drum"),
    ("instrument", "flute"),
    ("piano", "guitar"),
    ("piano", "violin"),
    ("piano", "flute"),
    ("guitar", "violin"),
    ("guitar", "drum"),
    ("bird", "airplane"),
    ("bird", "flute"),
)


def toy_semantic_graph() -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(TOY_SEMANTIC_NODES)
    graph.add_edges_from(TOY_SEMANTIC_EDGES)
    return nx.convert_node_labels_to_integers(graph, label_attribute="concept")


def branched_decision_graph(
    branch_lengths: int | Sequence[int],
    coupling_pair: tuple[int, int] | None = None,
    coupling_weight: float = 0.0,
    weight_jitter: float = 0.0,
    seed: int | None = None,
) -> tuple[nx.Graph, tuple[int, ...], tuple[tuple[int, ...], ...]]:
    """Hub-and-branches decision graph.

    With weight_jitter > 0 every edge weight is multiplied by an independent
    factor drawn uniformly from [1 - jitter, 1 + jitter] (robustness checks).
    """
    if isinstance(branch_lengths, int):
        lengths = [branch_lengths] * 2
    else:
        lengths = [int(length) for length in branch_lengths]
    if len(lengths) < 2:
        raise ValueError("at least two branches are required")
    if any(length < 1 for length in lengths):
        raise ValueError("branch lengths must be positive")
    graph = nx.Graph()
    graph.add_node(0)
    branches: list[list[int]] = []
    terminals: list[int] = []
    for length in lengths:
        previous = 0
        branch: list[int] = []
        for _ in range(length):
            node = graph.number_of_nodes()
            graph.add_node(node)
            graph.add_edge(previous, node, weight=1.0)
            branch.append(node)
            previous = node
        branches.append(branch)
        terminals.append(previous)
    if coupling_pair is not None and coupling_weight > 0.0:
        first, second = coupling_pair
        if not (0 <= first < len(branches) and 0 <= second < len(branches)):
            raise ValueError("coupling pair is out of range")
        for depth in range(min(len(branches[first]), len(branches[second]))):
            graph.add_edge(
                branches[first][depth],
                branches[second][depth],
                weight=float(coupling_weight),
            )
    if weight_jitter > 0.0:
        if not weight_jitter < 1.0:
            raise ValueError("weight_jitter must lie in [0, 1)")
        rng = np.random.default_rng(seed)
        for u, v in sorted(graph.edges()):
            graph[u][v]["weight"] *= float(rng.uniform(1.0 - weight_jitter, 1.0 + weight_jitter))
    return graph, tuple(terminals), tuple(tuple(branch) for branch in branches)


def line_decision_graph(length: int) -> tuple[nx.Graph, tuple[int, ...]]:
    if length < 2:
        raise ValueError("length must be at least 2")
    graph = nx.path_graph(length)
    return graph, (0, length - 1)


def multi_branch_decision_graph(
    branch_length: int,
    n_options: int,
    rung_probability: float = 0.0,
    seed: int | None = None,
) -> tuple[nx.Graph, tuple[int, ...]]:
    if branch_length < 1:
        raise ValueError("branch_length must be positive")
    if n_options < 2:
        raise ValueError("n_options must be at least 2")
    graph = nx.Graph()
    graph.add_node(0)
    branches: list[list[int]] = []
    terminals: list[int] = []
    for _ in range(n_options):
        previous = 0
        branch: list[int] = []
        for _ in range(branch_length):
            node = graph.number_of_nodes()
            graph.add_node(node)
            graph.add_edge(previous, node)
            branch.append(node)
            previous = node
        branches.append(branch)
        terminals.append(previous)
    if rung_probability > 0.0:
        rng = np.random.default_rng(seed)
        for depth in range(branch_length):
            for option in range(n_options):
                if rng.random() < rung_probability:
                    graph.add_edge(branches[option][depth], branches[(option + 1) % n_options][depth])
    return graph, tuple(terminals)


def transition_matrix(
    graph: nx.Graph,
    self_loop: float = 0.0,
    weight: str | None = None,
) -> np.ndarray:
    nodes = list(graph.nodes())
    adjacency = nx.to_numpy_array(graph, nodelist=nodes, weight=weight, dtype=float)
    n = adjacency.shape[0]
    if self_loop:
        adjacency = adjacency + self_loop * np.eye(n)
    row_sums = adjacency.sum(axis=1)
    isolated = row_sums == 0.0
    if np.any(isolated):
        adjacency[isolated, isolated] = 1.0
        row_sums = adjacency.sum(axis=1)
    return adjacency / row_sums[:, None]


def lazy_transition_matrix(P: np.ndarray, stay_probability: float) -> np.ndarray:
    if not 0.0 <= stay_probability <= 1.0:
        raise ValueError("stay_probability must lie in [0, 1]")
    n = P.shape[0]
    return (1.0 - stay_probability) * P + stay_probability * np.eye(n)


def _farthest_point_sample(graph: nx.Graph, k: int, seed: int | None) -> list[int]:
    nodes = list(graph.nodes())
    if k > len(nodes):
        raise ValueError("k exceeds the number of vertices")
    rng = np.random.default_rng(seed)
    start = int(rng.integers(len(nodes)))
    selected = [nodes[start]]
    distances = nx.single_source_shortest_path_length(graph, nodes[start])
    while len(selected) < k:
        min_distance = np.array([distances.get(node, np.inf) for node in nodes])
        min_distance[np.isin(nodes, selected)] = -1.0
        selected.append(nodes[int(np.argmax(min_distance))])
        new_distances = nx.single_source_shortest_path_length(graph, selected[-1])
        for node, distance in new_distances.items():
            distances[node] = min(distances.get(node, np.inf), distance)
        if np.all(np.isin(nodes, selected)):
            break
    return selected


def single_marked(graph: nx.Graph, node: int | None = None, seed: int | None = None) -> list[int]:
    nodes = list(graph.nodes())
    if node is None:
        node = int(np.random.default_rng(seed).choice(nodes))
    return [node]


def independent_marked(graph: nx.Graph, k: int, seed: int | None = None) -> list[int]:
    return _farthest_point_sample(graph, k, seed)


def clustered_marked(
    graph: nx.Graph,
    k: int,
    seed: int | None = None,
    center: int | None = None,
) -> list[int]:
    nodes = list(graph.nodes())
    if center is None:
        center = int(np.random.default_rng(seed).choice(nodes))
    order = list(nx.bfs_tree(graph, center).nodes())
    return order[:k]


def marked_set(
    graph: nx.Graph,
    kind: str,
    k: int = 1,
    seed: int | None = None,
) -> list[int]:
    if kind == "single":
        return single_marked(graph, seed=seed)
    if kind == "independent":
        return independent_marked(graph, k, seed=seed)
    if kind == "clustered":
        return clustered_marked(graph, k, seed=seed)
    raise ValueError(f"unknown marked-set kind: {kind}")


def option_sets(
    terminals: Sequence[int],
    extra: Iterable[Sequence[int]] | None = None,
) -> list[list[int]]:
    sets = [[int(terminal)] for terminal in terminals]
    if extra is not None:
        for index, nodes in enumerate(extra):
            sets[index].extend(int(node) for node in nodes)
    return sets
