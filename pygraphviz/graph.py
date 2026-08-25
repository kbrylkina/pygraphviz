"""
Graph data structures: Node, Edge, Graph.
"""

class Node:
    def __init__(self, node_id, label=None, **attrs):
        self.id = node_id
        self.label = label if label is not None else str(node_id)
        self.attrs = attrs

    def __repr__(self):
        return f"Node(id={self.id!r}, label={self.label!r})"


class Edge:
    def __init__(self, source, target, weight=1.0, label=None, **attrs):
        self.source = source
        self.target = target
        self.weight = weight
        self.label = label
        self.attrs = attrs

    def __repr__(self):
        return f"Edge({self.source!r} -> {self.target!r}, weight={self.weight})"


class Graph:
    def __init__(self, directed=False):
        self.directed = directed
        self._nodes = {}       # id -> Node
        self._edges = []       # list of Edge
        self._adj = {}         # id -> list of (neighbor_id, Edge)
        self._edge_lookup = set()
        self._in_degree = {}

    def add_node(self, node_id, label=None, **attrs):
        if node_id not in self._nodes:
            self._nodes[node_id] = Node(node_id, label, **attrs)
            self._adj[node_id] = []
            self._in_degree[node_id] = 0
        return self._nodes[node_id]

    def remove_node(self, node_id):
        if node_id not in self._nodes:
            raise KeyError(f"Node {node_id!r} not found")
        del self._nodes[node_id]
        del self._adj[node_id]
        self._edges = [e for e in self._edges if e.source != node_id and e.target != node_id]
        for nid in self._adj:
            self._adj[nid] = [(t, e) for t, e in self._adj[nid] if t != node_id]
        self._rebuild_edge_indexes()

    def get_node(self, node_id):
        return self._nodes.get(node_id)

    def has_node(self, node_id):
        return node_id in self._nodes

    def nodes(self):
        return list(self._nodes.values())

    def node_count(self):
        return len(self._nodes)

    def add_edge(self, source, target, weight=1.0, label=None, **attrs):
        if source not in self._nodes:
            self.add_node(source)
        if target not in self._nodes:
            self.add_node(target)
        edge = Edge(source, target, weight, label, **attrs)
        self._edges.append(edge)
        self._adj[source].append((target, edge))
        self._edge_lookup.add(self._edge_key(source, target))
        self._in_degree[target] += 1
        if not self.directed:
            self._adj[target].append((source, edge))
        return edge

    def remove_edge(self, source, target):
        self._edges = [e for e in self._edges if not self._matches_edge(e, source, target)]
        if source in self._adj:
            self._adj[source] = [(t, e) for t, e in self._adj[source] if t != target]
        if not self.directed and target in self._adj:
            self._adj[target] = [(t, e) for t, e in self._adj[target] if t != source]
        self._rebuild_edge_indexes()

    def has_edge(self, source, target):
        return self._edge_key(source, target) in self._edge_lookup

    def edges(self):
        return self._edges

    def edge_count(self):
        return len(self._edges)

    def neighbors(self, node_id):
        return [nid for nid, _ in self._adj.get(node_id, [])]

    def adj(self, node_id):
        return list(self._adj.get(node_id, []))

    def degree(self, node_id):
        return len(self._adj.get(node_id, []))

    def in_degree(self, node_id):
        if not self.directed:
            return self.degree(node_id)
        return self._in_degree.get(node_id, 0)

    def out_degree(self, node_id):
        if not self.directed:
            return self.degree(node_id)
        return len(self._adj.get(node_id, []))

    def __repr__(self):
        kind = "Directed" if self.directed else "Undirected"
        return f"{kind}Graph(nodes={self.node_count()}, edges={self.edge_count()})"

    def _edge_key(self, source, target):
        if self.directed:
            return (source, target)
        return frozenset((source, target))

    def _matches_edge(self, edge, source, target):
        if self.directed:
            return edge.source == source and edge.target == target
        return self._edge_key(edge.source, edge.target) == self._edge_key(source, target)

    def _rebuild_edge_indexes(self):
        self._edge_lookup = set()
        self._in_degree = {node_id: 0 for node_id in self._nodes}
        for edge in self._edges:
            self._edge_lookup.add(self._edge_key(edge.source, edge.target))
            if edge.target in self._in_degree:
                self._in_degree[edge.target] += 1
