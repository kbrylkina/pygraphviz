"""
Пример — минимальное остовное дерево (Kruskal / Prim).
"""
import sys, os
_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_dir, ".."))
os.makedirs(os.path.join(_dir, "output"), exist_ok=True)

from pygraphviz import Graph, Renderer, kruskal_mst, prim_mst

g = Graph(directed=False)
edges = [
    ("A", "B", 4), ("A", "C", 2), ("B", "C", 5), ("B", "D", 10),
    ("C", "D", 3), ("C", "E", 8), ("D", "E", 7), ("D", "F", 6),
    ("E", "F", 1),
]
for s, t, w in edges:
    g.add_edge(s, t, weight=w)

# Kruskal
mst_edges, total = kruskal_mst(g)
mst_pairs = {(e.source, e.target) for e in mst_edges}
mst_pairs |= {(e.target, e.source) for e in mst_edges}

print(f"MST edges: {[(e.source, e.target, e.weight) for e in mst_edges]}")
print(f"Total weight: {total}")

# Prim
mst_edges_p, total_p = prim_mst(g)
print(f"Prim total weight: {total_p}")

mst_nodes = set()
for e in mst_edges:
    mst_nodes.add(e.source)
    mst_nodes.add(e.target)

colors = {nid: "#27AE60" for nid in mst_nodes}

r = Renderer(g)
r.draw(
    layout="force",
    title=f"Минимальное остовное дерево (Kruskal, вес={total})",
    node_color=colors,
    show_weights=True,
    node_size=1200,
    save_path=os.path.join(_dir, "output/09_mst.png"),
)
