import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pygraphviz import (
    Graph,
    average_clustering,
    average_degree,
    bfs,
    binary_tree,
    circular_layout,
    complete_graph,
    connected_components,
    cycle_graph,
    degree_distribution,
    density,
    dfs,
    dijkstra,
    floyd_warshall,
    force_directed_layout,
    from_adjacency_matrix,
    from_edge_list,
    from_json,
    greedy_coloring,
    grid_graph,
    has_cycle,
    hierarchical_layout,
    kruskal_mst,
    prim_mst,
    random_graph,
    shortest_path,
    star_graph,
    to_adjacency_matrix,
    to_edge_list,
    to_html,
    to_json,
    to_svg,
    topological_sort,
)
from pygraphviz.layout import _QuadTree


def test_add_nodes():
    g = Graph()
    g.add_node(1, label="A")
    g.add_node(2, label="B")
    assert g.node_count() == 2
    assert g.get_node(1).label == "A"


def test_add_edges_undirected():
    g = Graph(directed=False)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    assert g.edge_count() == 2
    assert g.has_edge(1, 2)
    assert 2 in g.neighbors(1)
    assert 1 in g.neighbors(2)


def test_add_edges_directed():
    g = Graph(directed=True)
    g.add_edge("a", "b")
    g.add_edge("b", "c")
    assert "b" in g.neighbors("a")
    assert "a" not in g.neighbors("b")


def test_auto_add_nodes_on_edge():
    g = Graph()
    g.add_edge(10, 20)
    assert g.has_node(10)
    assert g.has_node(20)


def test_remove_node():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.remove_node(1)
    assert not g.has_node(1)
    assert g.edge_count() == 0


def test_remove_edge():
    g = Graph(directed=False)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.remove_edge(1, 2)
    assert not g.has_edge(1, 2)
    assert g.edge_count() == 1


def test_degree():
    g = Graph(directed=False)
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(1, 4)
    assert g.degree(1) == 3
    assert g.degree(2) == 1


def test_in_out_degree_directed():
    g = Graph(directed=True)
    g.add_edge("a", "b")
    g.add_edge("a", "c")
    g.add_edge("b", "c")
    assert g.out_degree("a") == 2
    assert g.in_degree("c") == 2
    assert g.in_degree("a") == 0


def test_indexes_update_after_remove():
    g = Graph(directed=True)
    g.add_edge("a", "b")
    g.add_edge("c", "b")
    assert g.has_edge("a", "b")
    assert g.in_degree("b") == 2

    g.remove_edge("a", "b")
    assert not g.has_edge("a", "b")
    assert g.in_degree("b") == 1

    g.remove_node("c")
    assert g.in_degree("b") == 0


def test_adj_returns_neighbor_edge_pairs():
    g = Graph(directed=True)
    e = g.add_edge("a", "b", weight=2.0)
    assert g.adj("a") == [("b", e)]
    assert g.adj("b") == []


def test_weighted_edge():
    g = Graph()
    e = g.add_edge(1, 2, weight=3.5)
    assert e.weight == 3.5


def test_empty_graph():
    g = Graph()
    assert g.node_count() == 0
    assert g.edge_count() == 0


def test_barnes_hut_layout_returns_all_positions():
    g = random_graph(80, edge_probability=0.04, seed=4)
    positions = force_directed_layout(g, iterations=3, repulsion="barnes_hut", seed=5)
    assert set(positions) == {n.id for n in g.nodes()}


def test_barnes_hut_handles_coincident_points():
    tree = _QuadTree({"a": (0.0, 0.0), "b": (0.0, 0.0), "c": (0.0, 0.0)})
    fx, fy = tree.repulsion("a", (0.0, 0.0), 0.1, 0.7)
    assert isinstance(fx, float) and isinstance(fy, float)


def test_html_export_contains_interactive_svg():
    g = Graph(directed=True)
    g.add_edge("A", "B", weight=2)
    html = to_html(g, layout="circular", show_weights=True)
    assert "<svg" in html
    assert "pointerdown" in html
    assert "A" in html
    assert "2" in html


def test_html_export_supports_edge_colors():
    g = Graph(directed=False)
    g.add_edge("A", "B", weight=2)
    html = to_html(g, layout="circular", edge_color={("B", "A"): "#ff0000"})
    assert "#ff0000" in html
    assert '"width": 3.0' in html


def test_svg_export_contains_vector_elements():
    g = Graph(directed=True)
    g.add_edge("A", "B", weight=2)
    svg = to_svg(g, layout="circular", show_weights=True)
    assert "<svg" in svg
    assert "<circle" in svg
    assert "marker-end" in svg
    assert "A" in svg
    assert "2" in svg


def test_svg_export_supports_edge_colors():
    g = Graph(directed=False)
    g.add_edge("A", "B")
    svg = to_svg(g, layout="circular", edge_color={("B", "A"): "#ff0000"})
    assert "#ff0000" in svg


def test_bfs_returns_order_and_parents():
    g = Graph()
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")

    order, parent = bfs(g, "A")
    assert order == ["A", "B", "C", "D"]
    assert parent == {"A": None, "B": "A", "C": "A", "D": "B"}


def test_dfs_reaches_all_nodes_from_start():
    g = Graph()
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")

    order, parent = dfs(g, "A")
    assert order[0] == "A"
    assert set(order) == {"A", "B", "C", "D"}
    assert parent["B"] == "A"
    assert parent["C"] == "A"


def test_dijkstra_and_shortest_path_use_weights():
    g = Graph()
    g.add_edge("A", "B", weight=5)
    g.add_edge("A", "C", weight=2)
    g.add_edge("C", "B", weight=1)

    dist, parent = dijkstra(g, "A")
    path, length = shortest_path(g, "A", "B")
    assert dist["B"] == 3
    assert parent["B"] == "C"
    assert path == ["A", "C", "B"]
    assert length == 3


def test_shortest_path_unreachable_returns_none_and_inf():
    g = Graph()
    g.add_edge("A", "B")
    g.add_node("Z")

    path, length = shortest_path(g, "A", "Z")
    assert path is None
    assert length == float("inf")


def test_connected_components_splits_disconnected_graph():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(3, 4)
    g.add_node(5)

    components = [set(c) for c in connected_components(g)]
    assert {1, 2} in components
    assert {3, 4} in components
    assert {5} in components


def test_cycle_detection_directed_and_undirected():
    directed = Graph(directed=True)
    directed.add_edge("A", "B")
    directed.add_edge("B", "C")
    directed.add_edge("C", "A")

    undirected_tree = Graph()
    undirected_tree.add_edge(1, 2)
    undirected_tree.add_edge(2, 3)

    assert has_cycle(directed)
    assert not has_cycle(undirected_tree)


def test_topological_sort_respects_dependencies_and_detects_cycle():
    g = Graph(directed=True)
    g.add_edge("parse", "compile")
    g.add_edge("compile", "link")
    g.add_edge("parse", "lint")

    order = topological_sort(g)
    assert order.index("parse") < order.index("compile")
    assert order.index("compile") < order.index("link")
    assert order.index("parse") < order.index("lint")

    g.add_edge("link", "parse")
    assert topological_sort(g) is None


def test_topological_sort_rejects_undirected_graph():
    g = Graph()
    g.add_edge(1, 2)
    try:
        topological_sort(g)
    except ValueError:
        pass
    else:
        raise AssertionError("topological_sort should reject undirected graphs")


def test_kruskal_and_prim_find_same_mst_weight():
    g = Graph()
    for source, target, weight in [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "C", 5),
        ("B", "D", 10),
        ("C", "D", 3),
    ]:
        g.add_edge(source, target, weight=weight)

    kruskal_edges, kruskal_weight = kruskal_mst(g)
    prim_edges, prim_weight = prim_mst(g)
    assert kruskal_weight == 9
    assert prim_weight == 9
    assert len(kruskal_edges) == g.node_count() - 1
    assert len(prim_edges) == g.node_count() - 1


def test_prim_empty_graph_returns_empty_result():
    assert prim_mst(Graph()) == ([], 0.0)


def test_greedy_coloring_assigns_different_colors_to_neighbors():
    g = cycle_graph(5)
    coloring, num_colors = greedy_coloring(g)

    assert num_colors >= 3
    for edge in g.edges():
        assert coloring[edge.source] != coloring[edge.target]


def test_floyd_warshall_all_pairs_shortest_paths():
    g = Graph(directed=True)
    g.add_edge("A", "B", weight=4)
    g.add_edge("A", "C", weight=1)
    g.add_edge("C", "B", weight=2)

    dist, next_node = floyd_warshall(g)
    assert dist["A"]["B"] == 3
    assert next_node["A"]["B"] == "C"
    assert dist["B"]["A"] == float("inf")


def test_graph_metrics_on_complete_graph():
    g = complete_graph(4)

    assert density(g) == 1.0
    assert average_degree(g) == 3
    assert degree_distribution(g) == {3: 4}
    assert average_clustering(g) == 1.0


def test_generators_create_expected_sizes():
    assert complete_graph(5).edge_count() == 10
    assert complete_graph(4, directed=True).edge_count() == 12
    assert cycle_graph(6).edge_count() == 6
    assert star_graph(4).node_count() == 5
    assert grid_graph(2, 3).edge_count() == 7
    assert binary_tree(2).edge_count() == 6


def test_random_graph_is_reproducible_with_seed():
    g1 = random_graph(8, edge_probability=0.4, weighted=True, seed=11)
    g2 = random_graph(8, edge_probability=0.4, weighted=True, seed=11)

    edges1 = [(e.source, e.target, e.weight) for e in g1.edges()]
    edges2 = [(e.source, e.target, e.weight) for e in g2.edges()]
    assert edges1 == edges2


def test_json_round_trip_preserves_graph_data():
    g = Graph(directed=True)
    g.add_node("A", label="Alpha", role="source")
    g.add_edge("A", "B", weight=2.5, label="ab")

    restored = from_json(to_json(g))
    assert restored.directed
    assert restored.get_node("A").label == "Alpha"
    assert restored.get_node("A").attrs["role"] == "source"
    assert restored.edge_count() == 1
    assert restored.edges()[0].weight == 2.5
    assert restored.edges()[0].label == "ab"


def test_edge_list_round_trip_weighted():
    g = from_edge_list("A B 2.5\nB C 1", directed=True, weighted=True)
    text = to_edge_list(g)

    assert g.directed
    assert g.has_edge("A", "B")
    assert g.edges()[0].weight == 2.5
    assert "A\tB\t2.5" in text


def test_adjacency_matrix_round_trip_undirected():
    original = Graph()
    original.add_edge("A", "B", weight=3)
    original.add_edge("B", "C", weight=4)

    matrix, ids = to_adjacency_matrix(original)
    restored = from_adjacency_matrix(matrix, ids=ids)
    assert matrix[ids.index("A")][ids.index("B")] == 3
    assert restored.has_edge("A", "B")
    assert restored.has_edge("B", "C")
    assert restored.edge_count() == 2


def test_layouts_return_position_for_every_node():
    g = binary_tree(2)
    circular = circular_layout(g)
    force = force_directed_layout(g, iterations=2, seed=9, repulsion="exact")
    hierarchical = hierarchical_layout(g, root=0)
    ids = {node.id for node in g.nodes()}

    assert set(circular) == ids
    assert set(force) == ids
    assert set(hierarchical) == ids
    assert hierarchical[0][1] == 0


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {fn.__name__}: {exc}")
    print(f"\n{passed}/{len(tests)} tests passed")
