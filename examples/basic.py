"""
Пример 1 — расстояния между городами России (км по автодорогам)
"""
import sys, os
_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_dir, ".."))
os.makedirs(os.path.join(_dir, "output"), exist_ok=True)

from pygraphviz import Graph, Renderer

g = Graph(directed=False)

# Реальные расстояния по автодорогам (км, Яндекс.Карты)
g.add_edge("Москва", "Казань", weight=815)
g.add_edge("Москва", "Самара", weight=1065)
g.add_edge("Москва", "Пермь", weight=1440)
g.add_edge("Казань", "Уфа", weight=525)
g.add_edge("Казань", "Пермь", weight=500)
g.add_edge("Уфа", "Пермь", weight=490)
g.add_edge("Самара", "Уфа", weight=465)
g.add_edge("Самара", "Казань", weight=350)

r = Renderer(g)
r.draw(
    layout="circular",
    title="Расстояния между городами России (км)",
    show_weights=True,
    node_size=1800,
    font_size=10,
    save_path=os.path.join(_dir, "output/01_cities_circular.png"),
)
