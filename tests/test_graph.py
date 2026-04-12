import sys
sys.path.insert(0, "..")

from pygraphviz import Graph


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


def test_weighted_edge():
    g = Graph()
    e = g.add_edge(1, 2, weight=3.5)
    assert e.weight == 3.5


def test_empty_graph():
    g = Graph()
    assert g.node_count() == 0
    assert g.edge_count() == 0


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
