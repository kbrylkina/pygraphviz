"""
Пример 2 — ориентированный граф зависимостей
"""
import sys, os
_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_dir, ".."))
os.makedirs(os.path.join(_dir, "output"), exist_ok=True)

from pygraphviz import Graph, Renderer

g = Graph(directed=True)

deps = [
    ("main", "config"),
    ("main", "database"),
    ("main", "api"),
    ("api", "auth"),
    ("api", "database"),
    ("auth", "config"),
    ("database", "config"),
    ("api", "cache"),
    ("cache", "config"),
]

for src, dst in deps:
    g.add_edge(src, dst)

colors = {
    "main": "#E74C3C",
    "config": "#2ECC71",
}

r = Renderer(g)
r.draw(
    layout="force",
    title="Граф зависимостей модулей",
    node_color=colors,
    node_size=1200,
    iterations=300,
    save_path=os.path.join(_dir, "output/02_deps_force.png"),
)
