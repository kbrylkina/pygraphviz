"""
Showcase — демонстрация всех возможностей библиотеки pygraphviz.
"""
import sys, os
_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_dir, ".."))
out = os.path.join(_dir, "output")
os.makedirs(out, exist_ok=True)

from pygraphviz import (
    Graph, Renderer,
    random_graph, complete_graph, cycle_graph, star_graph, binary_tree,
    bfs, dfs, dijkstra, shortest_path, connected_components, has_cycle, topological_sort,
    to_json, from_json, to_adjacency_matrix,
)


print("1/6  Random graph...")
rg = random_graph(12, edge_probability=0.25, weighted=True, seed=7)
Renderer(rg).draw(
    layout="force",
    title="Случайный граф G(12, 0.25)",
    show_weights=True,
    node_size=600,
    save_path=os.path.join(out, "04_random_force.png"),
)


print("2/6  Complete graph K6...")
kg = complete_graph(6)
Renderer(kg).draw(
    layout="circular",
    title="Полный граф K₆",
    node_color="#E67E22",
    save_path=os.path.join(out, "05_complete_circular.png"),
)


print("3/6  Binary tree...")
bt = binary_tree(3)
Renderer(bt).draw(
    layout="hierarchical",
    title="Полное бинарное дерево (глубина 3)",
    node_color="#1ABC9C",
    root=0,
    save_path=os.path.join(out, "06_binary_tree.png"),
)


print("4/6  Star graph...")
sg = star_graph(8)
Renderer(sg).draw(
    layout="force",
    title="Звёздный граф S₈",
    node_color={0: "#E74C3C"},
    node_size=700,
    save_path=os.path.join(out, "07_star.png"),
)


print("5/6  Shortest path...")
g = Graph(directed=False)
edges = [
    ("A", "B", 4), ("A", "C", 2), ("B", "D", 3), ("B", "E", 1),
    ("C", "D", 5), ("C", "F", 6), ("D", "E", 2), ("D", "F", 3),
    ("E", "F", 5),
]
for s, t, w in edges:
    g.add_edge(s, t, weight=w)

path, dist = shortest_path(g, "A", "F")
print(f"   Path A->F: {' -> '.join(path)}, distance={dist}")

colors = {}
for nid in [n.id for n in g.nodes()]:
    colors[nid] = "#E74C3C" if nid in path else "#BDC3C7"

Renderer(g).draw(
    layout="force",
    title=f"Кратчайший путь A→F (Dijkstra, d={dist})",
    node_color=colors,
    show_weights=True,
    node_size=1000,
    save_path=os.path.join(out, "08_shortest_path.png"),
)


print("6/6  Algorithms demo...")
dag = Graph(directed=True)
for s, t in [("A","B"),("A","C"),("B","D"),("C","D"),("D","E")]:
    dag.add_edge(s, t)

bfs_order, _ = bfs(dag, "A")
dfs_order, _ = dfs(dag, "A")
topo = topological_sort(dag)

print(f"   BFS from A: {bfs_order}")
print(f"   DFS from A: {dfs_order}")
print(f"   Topological sort: {topo}")
print(f"   Has cycle: {has_cycle(dag)}")

json_str = to_json(g)
g2 = from_json(json_str)
print(f"   JSON round-trip: {g.node_count()} nodes -> serialize -> deserialize -> {g2.node_count()} nodes ✓")

matrix, ids = to_adjacency_matrix(g)
print(f"   Adjacency matrix: {len(ids)}×{len(ids)}")

print(f"\nDone! Check {out}/ for images.")
