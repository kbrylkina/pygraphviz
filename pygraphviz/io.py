"""
Import / export utilities for graphs.
Supported formats: adjacency matrix, edge list, JSON.
"""
import json
from .graph import Graph



def to_json(graph, pretty=True):
    """Serialize graph to a JSON string."""
    data = {
        "directed": graph.directed,
        "nodes": [
            {"id": _serialize(n.id), "label": n.label, **n.attrs}
            for n in graph.nodes()
        ],
        "edges": [
            {"source": _serialize(e.source), "target": _serialize(e.target),
             "weight": e.weight, **({"label": e.label} if e.label else {})}
            for e in graph.edges()
        ],
    }
    return json.dumps(data, indent=2 if pretty else None, ensure_ascii=False)


def from_json(json_str):
    """Deserialize graph from a JSON string."""
    data = json.loads(json_str)
    g = Graph(directed=data.get("directed", False))
    for n in data["nodes"]:
        nid = n["id"]
        label = n.get("label")
        attrs = {k: v for k, v in n.items() if k not in ("id", "label")}
        g.add_node(nid, label=label, **attrs)
    for e in data["edges"]:
        g.add_edge(e["source"], e["target"],
                   weight=e.get("weight", 1.0),
                   label=e.get("label"))
    return g


def save_json(graph, path, pretty=True):
    """Save graph to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(to_json(graph, pretty=pretty))


def load_json(path):
    """Load graph from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return from_json(f.read())



def to_edge_list(graph):
    """
    Export as edge list string.
    Format: one edge per line: ``source target [weight]``
    """
    lines = []
    for e in graph.edges():
        if e.weight != 1.0:
            lines.append(f"{e.source}\t{e.target}\t{e.weight}")
        else:
            lines.append(f"{e.source}\t{e.target}")
    return "\n".join(lines)


def from_edge_list(text, directed=False, weighted=False):
    """
    Import from edge list string.
    Each line: ``source target [weight]``
    """
    g = Graph(directed=directed)
    for line in text.strip().splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        src, dst = parts[0], parts[1]
        w = float(parts[2]) if len(parts) > 2 and weighted else 1.0
        g.add_edge(src, dst, weight=w)
    return g



def to_adjacency_matrix(graph):
    """
    Export as adjacency matrix.

    Returns
    -------
    matrix : list of list of float
        matrix[i][j] = edge weight (0 if no edge).
    ids : list
        Node IDs corresponding to rows/columns.
    """
    ids = [n.id for n in graph.nodes()]
    idx = {nid: i for i, nid in enumerate(ids)}
    n = len(ids)
    matrix = [[0.0] * n for _ in range(n)]

    for e in graph.edges():
        i, j = idx[e.source], idx[e.target]
        matrix[i][j] = e.weight
        if not graph.directed:
            matrix[j][i] = e.weight

    return matrix, ids


def from_adjacency_matrix(matrix, ids=None, directed=False):
    """
    Import from adjacency matrix.

    Parameters
    ----------
    matrix : list of list of float
        Adjacency matrix (non-zero = edge weight).
    ids : list | None
        Node IDs. Defaults to 0..n-1.
    directed : bool
    """
    n = len(matrix)
    if ids is None:
        ids = list(range(n))
    g = Graph(directed=directed)
    for nid in ids:
        g.add_node(nid)
    for i in range(n):
        start = 0 if directed else i + 1
        for j in range(start, n):
            if matrix[i][j] != 0:
                g.add_edge(ids[i], ids[j], weight=matrix[i][j])
    return g



def _serialize(val):
    """Make value JSON-serializable (tuples -> lists, etc.)."""
    if isinstance(val, tuple):
        return list(val)
    return val
