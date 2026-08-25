"""
PyGraphViz — библиотека для визуализации графов.
Главный исполняемый файл: запускает все демонстрации.

Запуск:
    python3 main.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pygraphviz import (
    Graph, Renderer,
    random_graph, complete_graph, cycle_graph, star_graph, binary_tree,
    bfs, dfs, dijkstra, shortest_path,
    connected_components, has_cycle, topological_sort,
    kruskal_mst, prim_mst,
    greedy_coloring, density, average_degree,
    to_json, from_json, to_adjacency_matrix,
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)


def demo_cities():
    """1. Взвешенный граф городов — круговая укладка."""
    print("=" * 60)
    print("1. Граф городов России (circular layout)")
    print("=" * 60)

    g = Graph(directed=False)
    g.add_edge("Москва", "Казань", weight=815)
    g.add_edge("Москва", "Самара", weight=1065)
    g.add_edge("Москва", "Пермь", weight=1440)
    g.add_edge("Казань", "Уфа", weight=525)
    g.add_edge("Казань", "Пермь", weight=500)
    g.add_edge("Уфа", "Пермь", weight=490)
    g.add_edge("Самара", "Уфа", weight=465)
    g.add_edge("Самара", "Казань", weight=350)

    print(f"   Узлов: {g.node_count()}, Рёбер: {g.edge_count()}")
    print(f"   Плотность графа: {density(g):.2f}")
    print(f"   Средняя степень: {average_degree(g):.1f}")

    Renderer(g).draw(
        layout="circular",
        title="Расстояния между городами России (км)",
        show_weights=True,
        node_size=1800,
        font_size=10,
        save_path=os.path.join(OUT, "01_cities_circular.png"),
    )


def demo_dependencies():
    """2. Ориентированный граф зависимостей — force-directed."""
    print("\n" + "=" * 60)
    print("2. Граф зависимостей модулей (force-directed layout)")
    print("=" * 60)

    g = Graph(directed=True)
    deps = [
        ("main", "config"), ("main", "database"), ("main", "api"),
        ("api", "auth"), ("api", "database"), ("auth", "config"),
        ("database", "config"), ("api", "cache"), ("cache", "config"),
    ]
    for src, dst in deps:
        g.add_edge(src, dst)

    print(f"   Узлов: {g.node_count()}, Рёбер: {g.edge_count()}")
    print(f"   Содержит цикл: {has_cycle(g)}")

    topo = topological_sort(g)
    print(f"   Топологический порядок: {topo}")

    colors = {"main": "#E74C3C", "config": "#2ECC71"}
    Renderer(g).draw(
        layout="force",
        title="Граф зависимостей модулей",
        node_color=colors,
        node_size=1200,
        iterations=300,
        save_path=os.path.join(OUT, "02_deps_force.png"),
    )


def demo_tree():
    """3. Дерево файловой системы — иерархическая укладка."""
    print("\n" + "=" * 60)
    print("3. Дерево файловой системы (hierarchical layout)")
    print("=" * 60)

    g = Graph(directed=True)
    edges = [
        ("/", "home"), ("/", "etc"), ("/", "var"),
        ("home", "user1"), ("home", "user2"),
        ("etc", "nginx"), ("etc", "ssh"),
        ("var", "log"), ("var", "tmp"),
        ("user1", "docs"), ("user1", "downloads"),
        ("nginx", "nginx.conf"),
    ]
    for src, dst in edges:
        g.add_edge(src, dst)

    print(f"   Узлов: {g.node_count()}, Рёбер: {g.edge_count()}")

    bfs_order, _ = bfs(g, "/")
    dfs_order, _ = dfs(g, "/")
    print(f"   BFS от корня: {bfs_order}")
    print(f"   DFS от корня: {dfs_order}")

    Renderer(g).draw(
        layout="hierarchical",
        title="Дерево файловой системы",
        node_color="#8E44AD",
        node_size=1000,
        node_gap=1.5,
        font_size=8,
        root="/",
        save_path=os.path.join(OUT, "03_tree_hierarchical.png"),
    )


def demo_random():
    """4. Случайный граф — генератор Эрдёша-Реньи."""
    print("\n" + "=" * 60)
    print("4. Случайный граф G(12, 0.25) (force-directed layout)")
    print("=" * 60)

    g = random_graph(12, edge_probability=0.25, weighted=True, seed=7)
    print(f"   Узлов: {g.node_count()}, Рёбер: {g.edge_count()}")
    print(f"   Плотность: {density(g):.2f}")
    print(f"   Компонент связности: {len(connected_components(g))}")

    Renderer(g).draw(
        layout="force",
        title="Случайный граф G(12, 0.25)",
        show_weights=True,
        node_size=600,
        save_path=os.path.join(OUT, "04_random_force.png"),
    )


def demo_complete():
    """5. Полный граф K6."""
    print("\n" + "=" * 60)
    print("5. Полный граф K6 (circular layout)")
    print("=" * 60)

    g = complete_graph(6)
    print(f"   Узлов: {g.node_count()}, Рёбер: {g.edge_count()}")
    print(f"   Плотность: {density(g):.2f} (должна быть 1.0 для полного графа)")

    Renderer(g).draw(
        layout="circular",
        title="Полный граф K6",
        node_color="#E67E22",
        save_path=os.path.join(OUT, "05_complete_circular.png"),
    )


def demo_binary_tree():
    """6. Бинарное дерево."""
    print("\n" + "=" * 60)
    print("6. Полное бинарное дерево глубины 3 (hierarchical layout)")
    print("=" * 60)

    g = binary_tree(3)
    print(f"   Узлов: {g.node_count()}, Рёбер: {g.edge_count()}")

    Renderer(g).draw(
        layout="hierarchical",
        title="Полное бинарное дерево (глубина 3)",
        node_color="#1ABC9C",
        root=0,
        save_path=os.path.join(OUT, "06_binary_tree.png"),
    )


def demo_shortest_path():
    """7. Кратчайший путь — алгоритм Дейкстры."""
    print("\n" + "=" * 60)
    print("7. Кратчайший путь A -> F (Dijkstra)")
    print("=" * 60)

    g = Graph(directed=False)
    edges = [
        ("A", "B", 4), ("A", "C", 2), ("B", "D", 3), ("B", "E", 1),
        ("C", "D", 5), ("C", "F", 6), ("D", "E", 2), ("D", "F", 3),
        ("E", "F", 5),
    ]
    for s, t, w in edges:
        g.add_edge(s, t, weight=w)

    path, dist = shortest_path(g, "A", "F")
    print(f"   Путь: {' -> '.join(path)}")
    print(f"   Расстояние: {dist}")

    # Все расстояния от A
    all_dist, _ = dijkstra(g, "A")
    for node_id, d in sorted(all_dist.items()):
        print(f"   A -> {node_id}: {d}")

    colors = {nid: "#E74C3C" if nid in path else "#BDC3C7"
              for nid in [n.id for n in g.nodes()]}
    path_edges = {(path[i], path[i + 1]): "#E74C3C" for i in range(len(path) - 1)}

    Renderer(g).draw(
        layout="force",
        title=f"Кратчайший путь A -> F (Dijkstra, d={dist})",
        node_color=colors,
        edge_color=path_edges,
        show_weights=True,
        node_size=1000,
        save_path=os.path.join(OUT, "07_shortest_path.png"),
    )


def demo_mst():
    """8. Минимальное остовное дерево — Kruskal и Prim."""
    print("\n" + "=" * 60)
    print("8. Минимальное остовное дерево (Kruskal & Prim)")
    print("=" * 60)

    g = Graph(directed=False)
    edges = [
        ("A", "B", 4), ("A", "C", 2), ("A", "F", 9), ("B", "C", 5),
        ("B", "D", 10), ("C", "D", 3), ("C", "F", 8), ("D", "E", 5),
        ("D", "F", 6), ("E", "F", 2),
    ]
    for s, t, w in edges:
        g.add_edge(s, t, weight=w)

    mst_k, total_k = kruskal_mst(g)
    mst_p, total_p = prim_mst(g)

    print(f"   Kruskal MST: вес = {total_k}")
    for e in mst_k:
        print(f"      {e.source} -- {e.target}  (w={e.weight})")
    print(f"   Prim MST:    вес = {total_p}")
    print(f"   Результаты совпадают: {total_k == total_p}")

    mst_nodes = set()
    for e in mst_k:
        mst_nodes.add(e.source)
        mst_nodes.add(e.target)
    colors = {nid: "#27AE60" for nid in mst_nodes}
    mst_edge_colors = {(e.source, e.target): "#27AE60" for e in mst_k}

    Renderer(g).draw(
        layout="force",
        title=f"Минимальное остовное дерево (Kruskal, вес={total_k})",
        node_color=colors,
        edge_color=mst_edge_colors,
        show_weights=True,
        node_size=1200,
        seed=15,
        save_path=os.path.join(OUT, "08_mst.png"),
    )

    Renderer(g).draw_html(
        os.path.join(OUT, "08_mst_interactive.html"),
        layout="force",
        title=f"Интерактивное MST (Kruskal, вес={total_k})",
        node_color=colors,
        edge_color=mst_edge_colors,
        show_weights=True,
        seed=15,
    )

    Renderer(g).draw_svg(
        os.path.join(OUT, "08_mst.svg"),
        layout="force",
        title=f"MST (Kruskal, вес={total_k})",
        node_color=colors,
        edge_color=mst_edge_colors,
        show_weights=True,
        seed=15,
    )


def demo_coloring():
    """9. Раскраска графа."""
    print("\n" + "=" * 60)
    print("9. Жадная раскраска графа")
    print("=" * 60)

    g = Graph(directed=False)
    edges = [
        ("A","B"), ("A","C"), ("A","D"),
        ("B","C"), ("B","E"),
        ("C","D"), ("C","E"), ("C","F"),
        ("D","F"),
        ("E","F"),
    ]
    for s, t in edges:
        g.add_edge(s, t)

    coloring, num_colors = greedy_coloring(g)
    print(f"   Использовано цветов: {num_colors}")
    for nid, c in sorted(coloring.items()):
        print(f"      {nid}: цвет {c}")

    palette = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6", "#1ABC9C"]
    node_colors = {nid: palette[c % len(palette)] for nid, c in coloring.items()}

    Renderer(g).draw(
        layout="force",
        title=f"Раскраска графа ({num_colors} цвета)",
        node_color=node_colors,
        node_size=1200,
        save_path=os.path.join(OUT, "09_coloring.png"),
    )


def demo_io():
    """10. Импорт/экспорт."""
    print("\n" + "=" * 60)
    print("10. Импорт / экспорт")
    print("=" * 60)

    g = Graph(directed=False)
    g.add_edge("A", "B", weight=3)
    g.add_edge("B", "C", weight=5)
    g.add_edge("A", "C", weight=1)

    json_str = to_json(g)
    print(f"   JSON:\n{json_str[:200]}...")
    g2 = from_json(json_str)
    print(f"   Восстановлено из JSON: {g2.node_count()} узлов, {g2.edge_count()} рёбер")

    matrix, ids = to_adjacency_matrix(g)
    print(f"   Матрица смежности ({len(ids)}x{len(ids)}):")
    header = "     " + "  ".join(f"{nid:>5}" for nid in ids)
    print(header)
    for i, row in enumerate(matrix):
        vals = "  ".join(f"{v:5.1f}" for v in row)
        print(f"   {ids[i]:>3}  {vals}")



if __name__ == "__main__":
    print()
    print("  PyGraphViz v0.1.0 — библиотека для визуализации графов")
    print()

    demo_cities()
    demo_dependencies()
    demo_tree()
    demo_random()
    demo_complete()
    demo_binary_tree()
    demo_shortest_path()
    demo_mst()
    demo_coloring()
    demo_io()

    print(f"Визуализации сохранены в папку: {OUT}")
