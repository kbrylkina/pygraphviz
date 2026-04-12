"""
Graph traversal, pathfinding, and combinatorial algorithms.
"""
import heapq
from collections import deque
from itertools import count as _count


def bfs(graph, start):
    """
    Breadth-first search.

    Returns
    -------
    order : list
        Node IDs in BFS visit order.
    parent : dict
        parent[node_id] = predecessor node_id (None for start).
    """
    visited = {start}
    queue = deque([start])
    order = []
    parent = {start: None}

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                queue.append(neighbor)

    return order, parent


def dfs(graph, start):
    """
    Depth-first search (iterative).

    Returns
    -------
    order : list
        Node IDs in DFS visit order.
    parent : dict
        parent[node_id] = predecessor node_id (None for start).
    """
    visited = set()
    stack = [start]
    order = []
    parent = {start: None}

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in reversed(graph.neighbors(node)):
            if neighbor not in visited:
                parent.setdefault(neighbor, node)
                stack.append(neighbor)

    return order, parent


def dijkstra(graph, start):
    """
    Dijkstra's shortest-path algorithm (uses edge weights).

    Returns
    -------
    dist : dict
        dist[node_id] = shortest distance from start.
    parent : dict
        parent[node_id] = predecessor on the shortest path.
    """
    dist = {start: 0.0}
    parent = {start: None}
    heap = [(0.0, start)]
    visited = set()

    while heap:
        d, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)

        for neighbor, edge in graph._adj.get(node, []):
            weight = edge.weight
            new_dist = d + weight
            if neighbor not in dist or new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                parent[neighbor] = node
                heapq.heappush(heap, (new_dist, neighbor))

    return dist, parent


def shortest_path(graph, start, end):
    """
    Find the shortest path between two nodes.

    Returns
    -------
    path : list | None
        List of node IDs from start to end, or None if unreachable.
    distance : float
        Total path distance (inf if unreachable).
    """
    dist, parent = dijkstra(graph, start)
    if end not in parent:
        return None, float("inf")

    path = []
    current = end
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path, dist[end]


def connected_components(graph):
    """
    Find connected components of an undirected graph.

    Returns
    -------
    components : list of list
        Each sublist is a connected component (list of node IDs).
    """
    visited = set()
    components = []

    for node in graph.nodes():
        if node.id not in visited:
            order, _ = bfs(graph, node.id)
            visited.update(order)
            components.append(order)

    return components


def has_cycle(graph):
    """
    Detect whether the graph contains a cycle.

    For directed graphs uses DFS coloring.
    For undirected graphs uses union-find logic in DFS.
    """
    if graph.directed:
        return _has_cycle_directed(graph)
    else:
        return _has_cycle_undirected(graph)


def _has_cycle_directed(graph):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node.id: WHITE for node in graph.nodes()}

    def _dfs(u):
        color[u] = GRAY
        for v in graph.neighbors(u):
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and _dfs(v):
                return True
        color[u] = BLACK
        return False

    for node in graph.nodes():
        if color[node.id] == WHITE:
            if _dfs(node.id):
                return True
    return False


def _has_cycle_undirected(graph):
    visited = set()

    def _dfs(node, parent):
        visited.add(node)
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                if _dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                return True
        return False

    for node in graph.nodes():
        if node.id not in visited:
            if _dfs(node.id, None):
                return True
    return False


def topological_sort(graph):
    """
    Topological ordering of a directed acyclic graph.

    Returns
    -------
    order : list | None
        Node IDs in topological order, or None if graph has a cycle.
    """
    if not graph.directed:
        raise ValueError("Topological sort requires a directed graph")

    in_degree = {node.id: 0 for node in graph.nodes()}
    for edge in graph.edges():
        in_degree[edge.target] += 1

    queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.neighbors(node):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != graph.node_count():
        return None
    return order



def kruskal_mst(graph):
    """
    Kruskal's minimum spanning tree (for undirected weighted graphs).
    Uses Union-Find (disjoint set).

    Returns
    -------
    mst_edges : list of Edge
        Edges forming the MST.
    total_weight : float
        Sum of MST edge weights.
    """
    parent = {}
    rank = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True

    for node in graph.nodes():
        parent[node.id] = node.id
        rank[node.id] = 0

    sorted_edges = sorted(graph.edges(), key=lambda e: e.weight)
    mst_edges = []
    total_weight = 0.0

    for edge in sorted_edges:
        if union(edge.source, edge.target):
            mst_edges.append(edge)
            total_weight += edge.weight
            if len(mst_edges) == graph.node_count() - 1:
                break

    return mst_edges, total_weight


def prim_mst(graph, start=None):
    """
    Prim's minimum spanning tree (for undirected weighted graphs).

    Returns
    -------
    mst_edges : list of Edge
        Edges forming the MST.
    total_weight : float
        Sum of MST edge weights.
    """
    if graph.node_count() == 0:
        return [], 0.0

    if start is None:
        start = graph.nodes()[0].id

    visited = {start}
    heap = []
    counter = _count()

    for neighbor, edge in graph._adj.get(start, []):
        heapq.heappush(heap, (edge.weight, next(counter), edge))

    mst_edges = []
    total_weight = 0.0

    while heap and len(visited) < graph.node_count():
        w, _, edge = heapq.heappop(heap)
        if edge.source in visited and edge.target in visited:
            continue
        new_node = edge.target if edge.source in visited else edge.source
        visited.add(new_node)
        mst_edges.append(edge)
        total_weight += edge.weight

        for neighbor, e in graph._adj.get(new_node, []):
            if neighbor not in visited:
                heapq.heappush(heap, (e.weight, next(counter), e))

    return mst_edges, total_weight



def greedy_coloring(graph, strategy="largest_first"):
    """
    Greedy vertex coloring.

    Parameters
    ----------
    strategy : str
        'largest_first' — color highest-degree nodes first.
        'smallest_last' — remove smallest-degree node repeatedly, color in reverse.
        'random' — arbitrary order.

    Returns
    -------
    coloring : dict
        node_id -> color (int starting from 0).
    num_colors : int
        Number of colors used.
    """
    nodes = graph.nodes()

    if strategy == "largest_first":
        order = sorted(nodes, key=lambda n: graph.degree(n.id), reverse=True)
    elif strategy == "smallest_last":
        remaining = {n.id for n in nodes}
        order_ids = []
        adj_copy = {n.id: set(graph.neighbors(n.id)) for n in nodes}
        while remaining:
            min_node = min(remaining, key=lambda x: len(adj_copy[x] & remaining))
            remaining.remove(min_node)
            order_ids.append(min_node)
        order_ids.reverse()
        id_to_node = {n.id: n for n in nodes}
        order = [id_to_node[nid] for nid in order_ids]
    else:
        order = list(nodes)

    coloring = {}
    for node in order:
        neighbor_colors = {coloring[nb] for nb in graph.neighbors(node.id) if nb in coloring}
        color = 0
        while color in neighbor_colors:
            color += 1
        coloring[node.id] = color

    num_colors = max(coloring.values()) + 1 if coloring else 0
    return coloring, num_colors



def floyd_warshall(graph):
    """
    All-pairs shortest paths (Floyd-Warshall).

    Returns
    -------
    dist : dict of dict
        dist[u][v] = shortest distance from u to v.
    next_node : dict of dict
        next_node[u][v] = next hop on shortest path from u to v.
    """
    ids = [n.id for n in graph.nodes()]
    INF = float("inf")

    dist = {u: {v: INF for v in ids} for u in ids}
    next_node = {u: {v: None for v in ids} for u in ids}

    for u in ids:
        dist[u][u] = 0

    for edge in graph.edges():
        u, v, w = edge.source, edge.target, edge.weight
        if w < dist[u][v]:
            dist[u][v] = w
            next_node[u][v] = v
        if not graph.directed and w < dist[v][u]:
            dist[v][u] = w
            next_node[v][u] = u

    for k in ids:
        for i in ids:
            for j in ids:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_node[i][j] = next_node[i][k]

    return dist, next_node



def density(graph):
    """Graph density: ratio of actual edges to possible edges."""
    n = graph.node_count()
    if n <= 1:
        return 0.0
    max_edges = n * (n - 1) if graph.directed else n * (n - 1) / 2
    return graph.edge_count() / max_edges


def degree_distribution(graph):
    """
    Returns dict mapping degree -> count of nodes with that degree.
    """
    dist = {}
    for node in graph.nodes():
        d = graph.degree(node.id)
        dist[d] = dist.get(d, 0) + 1
    return dist


def average_degree(graph):
    """Average node degree."""
    if graph.node_count() == 0:
        return 0.0
    return sum(graph.degree(n.id) for n in graph.nodes()) / graph.node_count()


def clustering_coefficient(graph, node_id):
    """
    Local clustering coefficient for a node.
    Measures how connected its neighbors are to each other.
    """
    neighbors = graph.neighbors(node_id)
    k = len(neighbors)
    if k < 2:
        return 0.0
    nb_set = set(neighbors)
    links = 0
    for i, u in enumerate(neighbors):
        for v in neighbors[i + 1:]:
            if v in set(graph.neighbors(u)):
                links += 1
    return 2 * links / (k * (k - 1))


def average_clustering(graph):
    """Average clustering coefficient across all nodes."""
    nodes = graph.nodes()
    if not nodes:
        return 0.0
    return sum(clustering_coefficient(graph, n.id) for n in nodes) / len(nodes)
