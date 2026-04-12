"""
Utility functions to generate common graph types.
"""
import random
from .graph import Graph


def random_graph(n, edge_probability=0.3, directed=False, weighted=False, seed=None):
    """
    Erdos–Renyi random graph G(n, p).

    Parameters
    ----------
    n : int
        Number of nodes.
    edge_probability : float
        Probability of each edge existing.
    directed : bool
        Create a directed graph.
    weighted : bool
        Assign random weights in [1, 10].
    seed : int | None
        Random seed.
    """
    if seed is not None:
        random.seed(seed)
    g = Graph(directed=directed)
    for i in range(n):
        g.add_node(i)

    for i in range(n):
        start = 0 if directed else i + 1
        for j in range(start, n):
            if i == j:
                continue
            if random.random() < edge_probability:
                w = round(random.uniform(1, 10), 1) if weighted else 1.0
                g.add_edge(i, j, weight=w)

    return g


def complete_graph(n, directed=False):
    """
    Complete graph K_n — every node connected to every other.
    """
    g = Graph(directed=directed)
    for i in range(n):
        g.add_node(i)
    for i in range(n):
        for j in range(i + 1, n):
            g.add_edge(i, j)
            if directed:
                g.add_edge(j, i)
    return g


def grid_graph(rows, cols):
    """
    2D grid graph.
    Node IDs are (row, col) tuples.
    """
    g = Graph(directed=False)
    for r in range(rows):
        for c in range(cols):
            label = f"{r},{c}"
            g.add_node((r, c), label=label)

    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                g.add_edge((r, c), (r, c + 1))
            if r + 1 < rows:
                g.add_edge((r, c), (r + 1, c))

    return g


def cycle_graph(n, directed=False):
    """
    Cycle graph C_n — ring of n nodes.
    """
    g = Graph(directed=directed)
    for i in range(n):
        g.add_node(i)
    for i in range(n):
        g.add_edge(i, (i + 1) % n)
    return g


def star_graph(n):
    """
    Star graph S_n — one central node connected to n outer nodes.
    """
    g = Graph(directed=False)
    g.add_node(0, label="center")
    for i in range(1, n + 1):
        g.add_node(i)
        g.add_edge(0, i)
    return g


def binary_tree(depth):
    """
    Complete binary tree with given depth.
    """
    g = Graph(directed=True)
    n_nodes = 2 ** (depth + 1) - 1
    for i in range(n_nodes):
        g.add_node(i)
    for i in range(n_nodes):
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n_nodes:
            g.add_edge(i, left)
        if right < n_nodes:
            g.add_edge(i, right)
    return g
