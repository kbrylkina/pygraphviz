"""
Graph layout algorithms: circular, force-directed (Fruchterman-Reingold), hierarchical.
"""
import math
import random
from collections import deque

_MAX_DEPTH = 24


def circular_layout(graph, radius=1.0, **kwargs):
    """Place nodes evenly on a circle."""
    nodes = graph.nodes()
    n = len(nodes)
    if n == 0:
        return {}
    positions = {}
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n - math.pi / 2
        positions[node.id] = (radius * math.cos(angle), radius * math.sin(angle))
    return positions


def force_directed_layout(
    graph,
    iterations=200,
    k=None,
    seed=42,
    repulsion="auto",
    theta=0.7,
    barnes_hut_threshold=60,
    **kwargs,
):
    """
    Fruchterman-Reingold force-directed layout.
    Nodes repel each other; edges act as springs pulling connected nodes together.
    """
    random.seed(seed)
    nodes = graph.nodes()
    n = len(nodes)
    if n == 0:
        return {}
    if n == 1:
        return {nodes[0].id: (0.0, 0.0)}

    positions = {}
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n
        positions[node.id] = (
            math.cos(angle) + random.uniform(-0.1, 0.1),
            math.sin(angle) + random.uniform(-0.1, 0.1),
        )

    area = 1.0
    if k is None:
        k = math.sqrt(area / n)

    t = 0.3  # max displacement
    cooling = t / (iterations + 1)

    node_ids = [node.id for node in nodes]

    use_barnes_hut = repulsion == "barnes_hut" or (
        repulsion == "auto" and n >= barnes_hut_threshold
    )

    for iteration in range(iterations):
        disp = {nid: [0.0, 0.0] for nid in node_ids}

        if use_barnes_hut:
            tree = _QuadTree(positions)
            for nid in node_ids:
                fx, fy = tree.repulsion(nid, positions[nid], k, theta)
                disp[nid][0] += fx
                disp[nid][1] += fy
        else:
            _exact_repulsion(node_ids, positions, disp, k)

        # Attractive forces along edges
        for edge in graph.edges():
            u, v = edge.source, edge.target
            dx = positions[u][0] - positions[v][0]
            dy = positions[u][1] - positions[v][1]
            dist = math.sqrt(dx * dx + dy * dy) or 0.001
            force = dist * dist / k
            disp[u][0] -= dx / dist * force
            disp[u][1] -= dy / dist * force
            disp[v][0] += dx / dist * force
            disp[v][1] += dy / dist * force

        # Apply displacement capped by temperature
        for nid in node_ids:
            d = math.sqrt(disp[nid][0] ** 2 + disp[nid][1] ** 2) or 0.001
            scale = min(d, t) / d
            positions[nid] = (
                positions[nid][0] + disp[nid][0] * scale,
                positions[nid][1] + disp[nid][1] * scale,
            )

        t -= cooling

    return positions


def _exact_repulsion(node_ids, positions, disp, k):
    for i in range(len(node_ids)):
        for j in range(i + 1, len(node_ids)):
            u, v = node_ids[i], node_ids[j]
            dx = positions[u][0] - positions[v][0]
            dy = positions[u][1] - positions[v][1]
            dist = math.sqrt(dx * dx + dy * dy) or 0.001
            force = k * k / dist
            disp[u][0] += dx / dist * force
            disp[u][1] += dy / dist * force
            disp[v][0] -= dx / dist * force
            disp[v][1] -= dy / dist * force


class _QuadNode:
    def __init__(self, cx, cy, half_size):
        self.cx = cx
        self.cy = cy
        self.half_size = half_size
        self.point = None
        self.children = None
        self.mass = 0
        self.mass_x = 0.0
        self.mass_y = 0.0

    def insert(self, node_id, x, y, depth=0):
        self.mass += 1
        self.mass_x += (x - self.mass_x) / self.mass
        self.mass_y += (y - self.mass_y) / self.mass

        if self.children is None and self.point is None and self.mass == 1:
            self.point = (node_id, x, y)
            return

        # coincident points: stop subdividing, keep as one aggregate leaf
        if depth >= _MAX_DEPTH:
            self.point = None
            return

        if self.children is None:
            old_id, old_x, old_y = self.point
            self.point = None
            self._split()
            self._child_for(old_x, old_y).insert(old_id, old_x, old_y, depth + 1)

        self._child_for(x, y).insert(node_id, x, y, depth + 1)

    def repulsion(self, node_id, x, y, k, theta):
        if self.mass == 0:
            return 0.0, 0.0
        if self.children is None:
            if self.point is None:
                return _repulsion_from_mass(x, y, self.mass_x, self.mass_y, self.mass, k)
            if self.point[0] == node_id:
                return 0.0, 0.0
            return _repulsion_from_mass(x, y, self.point[1], self.point[2], 1, k)

        dx = x - self.mass_x
        dy = y - self.mass_y
        dist = math.sqrt(dx * dx + dy * dy) or 0.001
        width = self.half_size * 2
        if width / dist < theta:
            return _repulsion_from_mass(x, y, self.mass_x, self.mass_y, self.mass, k)

        fx = fy = 0.0
        for child in self.children:
            cfx, cfy = child.repulsion(node_id, x, y, k, theta)
            fx += cfx
            fy += cfy
        return fx, fy

    def _split(self):
        q = self.half_size / 2
        self.children = [
            _QuadNode(self.cx - q, self.cy - q, q),
            _QuadNode(self.cx + q, self.cy - q, q),
            _QuadNode(self.cx - q, self.cy + q, q),
            _QuadNode(self.cx + q, self.cy + q, q),
        ]

    def _child_for(self, x, y):
        east = x >= self.cx
        north = y >= self.cy
        return self.children[(1 if east else 0) + (2 if north else 0)]


class _QuadTree:
    def __init__(self, positions):
        xs = [p[0] for p in positions.values()]
        ys = [p[1] for p in positions.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        half_size = max(max_x - min_x, max_y - min_y, 1e-6) / 2 + 1e-6
        self.root = _QuadNode(cx, cy, half_size)
        for node_id, (x, y) in positions.items():
            self.root.insert(node_id, x, y)

    def repulsion(self, node_id, position, k, theta):
        return self.root.repulsion(node_id, position[0], position[1], k, theta)


def _repulsion_from_mass(x, y, mass_x, mass_y, mass, k):
    dx = x - mass_x
    dy = y - mass_y
    dist = math.sqrt(dx * dx + dy * dy) or 0.001
    force = mass * k * k / dist
    return dx / dist * force, dy / dist * force


def hierarchical_layout(graph, root=None, level_gap=1.2, node_gap=1.0, **kwargs):
    """
    BFS-based top-down hierarchical layout.
    """
    nodes = graph.nodes()
    if not nodes:
        return {}

    if root is None:
        in_deg = {node.id: graph.in_degree(node.id) for node in nodes}
        root = min(in_deg, key=in_deg.get)

    levels = {root: 0}
    queue = deque([root])
    visited = {root}
    while queue:
        current = queue.popleft()
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                levels[neighbor] = levels[current] + 1
                queue.append(neighbor)

    # Nodes not reachable from root get appended at bottom
    max_level = max(levels.values(), default=0)
    for node in nodes:
        if node.id not in levels:
            max_level += 1
            levels[node.id] = max_level

    level_groups = {}
    for nid, lvl in levels.items():
        level_groups.setdefault(lvl, []).append(nid)

    positions = {}
    for lvl, group in level_groups.items():
        total_width = (len(group) - 1) * node_gap
        for i, nid in enumerate(group):
            x = i * node_gap - total_width / 2
            y = -lvl * level_gap
            positions[nid] = (x, y)

    return positions
