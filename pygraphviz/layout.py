import math
import random


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


def force_directed_layout(graph, iterations=200, k=None, seed=42, **kwargs):
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

    for iteration in range(iterations):
        disp = {nid: [0.0, 0.0] for nid in node_ids}

        # Repulsive forces between every pair of nodes
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
    queue = [root]
    visited = {root}
    while queue:
        current = queue.pop(0)
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
