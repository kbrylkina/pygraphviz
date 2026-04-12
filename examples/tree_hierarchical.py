"""
Пример 3 — дерево
"""
import sys, os
_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_dir, ".."))
os.makedirs(os.path.join(_dir, "output"), exist_ok=True)

from pygraphviz import Graph, Renderer

g = Graph(directed=True)

edges = [
    ("/", "home"),
    ("/", "etc"),
    ("/", "var"),
    ("home", "user1"),
    ("home", "user2"),
    ("etc", "nginx"),
    ("etc", "ssh"),
    ("var", "log"),
    ("var", "tmp"),
    ("user1", "docs"),
    ("user1", "downloads"),
    ("nginx", "nginx.conf"),
]

for src, dst in edges:
    g.add_edge(src, dst)

r = Renderer(g)
r.draw(
    layout="hierarchical",
    title="Дерево файловой системы",
    node_color="#8E44AD",
    node_size=1000,
    node_gap=1.5,
    font_size=8,
    root="/",
    save_path=os.path.join(_dir, "output/03_tree_hierarchical.png"),
)
