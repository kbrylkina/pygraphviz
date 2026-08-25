"""
Import / export utilities for graphs.
Supported formats: adjacency matrix, edge list, JSON.
"""
import html
import json
from .graph import Graph
from .layout import circular_layout, force_directed_layout, hierarchical_layout


HTML_LAYOUTS = {
    "circular": circular_layout,
    "force": force_directed_layout,
    "hierarchical": hierarchical_layout,
}



def to_json(graph, pretty=True):
    """Serialize graph to a JSON string."""
    data = {
        "directed": graph.directed,
        "nodes": [
            {"id": _serialize(n.id), "label": n.label, **n.attrs}
            for n in graph.nodes()
        ],
        "edges": [
            {"source": _serialize(e.source), "target": _serialize(e.target),
             "weight": e.weight, **({"label": e.label} if e.label else {})}
            for e in graph.edges()
        ],
    }
    return json.dumps(data, indent=2 if pretty else None, ensure_ascii=False)


def from_json(json_str):
    """Deserialize graph from a JSON string."""
    data = json.loads(json_str)
    g = Graph(directed=data.get("directed", False))
    for n in data["nodes"]:
        nid = n["id"]
        label = n.get("label")
        attrs = {k: v for k, v in n.items() if k not in ("id", "label")}
        g.add_node(nid, label=label, **attrs)
    for e in data["edges"]:
        g.add_edge(e["source"], e["target"],
                   weight=e.get("weight", 1.0),
                   label=e.get("label"))
    return g


def save_json(graph, path, pretty=True):
    """Save graph to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(to_json(graph, pretty=pretty))


def load_json(path):
    """Load graph from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return from_json(f.read())


def to_html(
    graph,
    layout="force",
    title="Interactive graph",
    node_color="#4A90D9",
    edge_color="#888888",
    width=960,
    height=640,
    show_weights=False,
    show_edge_labels=False,
    **layout_kwargs,
):
    """
    Export graph as a standalone interactive HTML document.

    The generated page supports panning, zooming, dragging nodes and toggling labels.
    """
    layout_fn = HTML_LAYOUTS.get(layout)
    if layout_fn is None:
        raise ValueError(f"Unknown layout {layout!r}. Choose from: {list(HTML_LAYOUTS)}")

    positions = layout_fn(graph, **layout_kwargs) if graph.node_count() else {}
    nodes = []
    for node in graph.nodes():
        x, y = positions.get(node.id, (0.0, 0.0))
        color = node_color.get(node.id, "#4A90D9") if isinstance(node_color, dict) else node_color
        nodes.append({
            "id": _html_id(node.id),
            "label": node.label,
            "x": x,
            "y": y,
            "color": color,
        })

    edges = []
    for edge in graph.edges():
        color = _edge_color(graph, edge_color, edge)
        label = None
        if show_weights and edge.weight != 1.0:
            label = f"{edge.weight:g}"
        elif show_edge_labels and edge.label:
            label = edge.label
        edges.append({
            "source": _html_id(edge.source),
            "target": _html_id(edge.target),
            "weight": edge.weight,
            "label": label,
            "color": color,
            "width": 3.0 if color != "#888888" else 1.8,
        })

    data = {
        "directed": graph.directed,
        "nodes": nodes,
        "edges": edges,
        "edgeColor": "#888888" if isinstance(edge_color, dict) else edge_color,
        "title": title,
    }

    payload = json.dumps(data, ensure_ascii=False)
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      color: #24313a;
      background: #f6f8fa;
    }}
    .toolbar {{
      display: flex;
      gap: 8px;
      align-items: center;
      padding: 10px 12px;
      border-bottom: 1px solid #d8e0e4;
      background: #ffffff;
    }}
    .toolbar strong {{ margin-right: auto; }}
    button {{
      border: 1px solid #c8d1d7;
      background: #ffffff;
      padding: 6px 10px;
      border-radius: 6px;
      cursor: pointer;
    }}
    svg {{
      display: block;
      width: 100vw;
      height: calc(100vh - 48px);
      background: #ffffff;
      cursor: grab;
    }}
    svg.dragging {{ cursor: grabbing; }}
    .edge {{ stroke: var(--edge-color); stroke-width: 1.8; }}
    .node {{ stroke: #ffffff; stroke-width: 2.5; cursor: move; }}
    .node-label {{
      fill: #ffffff;
      font-size: 12px;
      font-weight: 700;
      pointer-events: none;
      text-anchor: middle;
      dominant-baseline: central;
    }}
    .edge-label {{
      fill: #24313a;
      font-size: 12px;
      paint-order: stroke;
      stroke: #ffffff;
      stroke-width: 4px;
      stroke-linejoin: round;
      text-anchor: middle;
      dominant-baseline: central;
    }}
    .hidden {{ display: none; }}
  </style>
</head>
<body>
  <div class="toolbar">
    <strong>{safe_title}</strong>
    <button id="fit">Fit</button>
    <button id="labels">Labels</button>
    <button id="edgeLabels">Edge labels</button>
  </div>
  <svg id="graph" viewBox="0 0 {int(width)} {int(height)}" role="img" aria-label="{safe_title}">
    <defs>
      <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="{html.escape(data["edgeColor"])}"></path>
      </marker>
    </defs>
    <g id="viewport"></g>
  </svg>
  <script>
    const data = {payload};
    const svg = document.getElementById("graph");
    const viewport = document.getElementById("viewport");
    const state = {{ scale: 1, tx: 0, ty: 0, labels: true, edgeLabels: true }};
    const nodeMap = new Map(data.nodes.map(n => [n.id, n]));

    normalizePositions();
    render();
    fit();

    document.getElementById("fit").onclick = fit;
    document.getElementById("labels").onclick = () => {{
      state.labels = !state.labels;
      viewport.querySelectorAll(".node-label").forEach(el => el.classList.toggle("hidden", !state.labels));
    }};
    document.getElementById("edgeLabels").onclick = () => {{
      state.edgeLabels = !state.edgeLabels;
      viewport.querySelectorAll(".edge-label").forEach(el => el.classList.toggle("hidden", !state.edgeLabels));
    }};

    let pan = null;
    svg.addEventListener("pointerdown", event => {{
      if (event.target.classList.contains("node")) return;
      pan = {{ x: event.clientX, y: event.clientY, tx: state.tx, ty: state.ty }};
      svg.classList.add("dragging");
      svg.setPointerCapture(event.pointerId);
    }});
    svg.addEventListener("pointermove", event => {{
      if (!pan) return;
      state.tx = pan.tx + event.clientX - pan.x;
      state.ty = pan.ty + event.clientY - pan.y;
      applyTransform();
    }});
    svg.addEventListener("pointerup", event => {{
      pan = null;
      svg.classList.remove("dragging");
      svg.releasePointerCapture(event.pointerId);
    }});
    svg.addEventListener("wheel", event => {{
      event.preventDefault();
      const factor = event.deltaY < 0 ? 1.12 : 0.89;
      const before = screenToWorld(event.clientX, event.clientY);
      state.scale *= factor;
      const after = worldToScreen(before.x, before.y);
      state.tx += event.clientX - after.x;
      state.ty += event.clientY - after.y;
      applyTransform();
    }}, {{ passive: false }});

    function normalizePositions() {{
      if (!data.nodes.length) return;
      const xs = data.nodes.map(n => n.x);
      const ys = data.nodes.map(n => n.y);
      const minX = Math.min(...xs), maxX = Math.max(...xs);
      const minY = Math.min(...ys), maxY = Math.max(...ys);
      const spanX = Math.max(maxX - minX, 1e-6);
      const spanY = Math.max(maxY - minY, 1e-6);
      const pad = 64;
      const box = svg.viewBox.baseVal;
      for (const n of data.nodes) {{
        n.x = pad + (n.x - minX) / spanX * Math.max(box.width - pad * 2, 1);
        n.y = pad + (n.y - minY) / spanY * Math.max(box.height - pad * 2, 1);
      }}
    }}

    function render() {{
      viewport.style.setProperty("--edge-color", data.edgeColor);
      for (const edge of data.edges) {{
        const s = nodeMap.get(edge.source), t = nodeMap.get(edge.target);
        if (!s || !t) continue;
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.classList.add("edge");
        line.dataset.source = edge.source;
        line.dataset.target = edge.target;
        line.setAttribute("stroke", edge.color);
        line.setAttribute("stroke-width", edge.width);
        if (data.directed) line.setAttribute("marker-end", "url(#arrow)");
        viewport.appendChild(line);
        if (edge.label) {{
          const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
          label.classList.add("edge-label");
          label.textContent = edge.label;
          label.dataset.source = edge.source;
          label.dataset.target = edge.target;
          viewport.appendChild(label);
        }}
      }}
      for (const node of data.nodes) {{
        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        group.dataset.id = node.id;
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.classList.add("node");
        circle.setAttribute("r", Math.max(20, Math.min(38, 12 + String(node.label).length * 3)));
        circle.setAttribute("fill", node.color);
        const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        label.classList.add("node-label");
        label.textContent = node.label;
        group.append(circle, label);
        viewport.appendChild(group);
        enableNodeDrag(group, node);
      }}
      updateGraph();
    }}

    function enableNodeDrag(group, node) {{
      group.addEventListener("pointerdown", event => {{
        event.stopPropagation();
        const start = screenToWorld(event.clientX, event.clientY);
        const drag = {{ x: start.x, y: start.y, nx: node.x, ny: node.y }};
        group.setPointerCapture(event.pointerId);
        const move = e => {{
          const p = screenToWorld(e.clientX, e.clientY);
          node.x = drag.nx + p.x - drag.x;
          node.y = drag.ny + p.y - drag.y;
          updateGraph();
        }};
        const up = () => {{
          group.removeEventListener("pointermove", move);
          group.removeEventListener("pointerup", up);
        }};
        group.addEventListener("pointermove", move);
        group.addEventListener("pointerup", up);
      }});
    }}

    function updateGraph() {{
      viewport.querySelectorAll(".edge").forEach(line => {{
        const s = nodeMap.get(line.dataset.source), t = nodeMap.get(line.dataset.target);
        line.setAttribute("x1", s.x);
        line.setAttribute("y1", s.y);
        line.setAttribute("x2", t.x);
        line.setAttribute("y2", t.y);
      }});
      viewport.querySelectorAll(".edge-label").forEach(label => {{
        const s = nodeMap.get(label.dataset.source), t = nodeMap.get(label.dataset.target);
        label.setAttribute("x", (s.x + t.x) / 2);
        label.setAttribute("y", (s.y + t.y) / 2);
      }});
      viewport.querySelectorAll("g[data-id]").forEach(group => {{
        const n = nodeMap.get(group.dataset.id);
        group.setAttribute("transform", `translate(${{n.x}},${{n.y}})`);
      }});
    }}

    function fit() {{
      state.scale = 1;
      state.tx = 0;
      state.ty = 0;
      applyTransform();
    }}
    function applyTransform() {{
      viewport.setAttribute("transform", `translate(${{state.tx}},${{state.ty}}) scale(${{state.scale}})`);
    }}
    function screenToWorld(x, y) {{
      const pt = svg.createSVGPoint();
      pt.x = x; pt.y = y;
      const p = pt.matrixTransform(svg.getScreenCTM().inverse());
      return {{ x: (p.x - state.tx) / state.scale, y: (p.y - state.ty) / state.scale }};
    }}
    function worldToScreen(x, y) {{
      const pt = svg.createSVGPoint();
      pt.x = x * state.scale + state.tx;
      pt.y = y * state.scale + state.ty;
      return pt.matrixTransform(svg.getScreenCTM());
    }}
  </script>
</body>
</html>
"""


def save_html(graph, path, **kwargs):
    """Save graph as a standalone interactive HTML file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(to_html(graph, **kwargs))


def to_svg(
    graph,
    layout="force",
    title="Graph",
    node_color="#4A90D9",
    edge_color="#888888",
    width=960,
    height=640,
    show_weights=False,
    show_edge_labels=False,
    **layout_kwargs,
):
    """
    Export graph as a standalone static SVG document.

    SVG output is vector-based and, unlike PNG rendering, does not depend on
    matplotlib, so it can be produced in a headless environment.
    """
    layout_fn = HTML_LAYOUTS.get(layout)
    if layout_fn is None:
        raise ValueError(f"Unknown layout {layout!r}. Choose from: {list(HTML_LAYOUTS)}")

    positions = layout_fn(graph, **layout_kwargs) if graph.node_count() else {}
    coords = _fit_positions(positions, width, height)

    arrow_fill = "#888888" if isinstance(edge_color, dict) else edge_color
    parts = [
        f'<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L0,6 L9,3 z" fill="{html.escape(arrow_fill)}"></path></marker></defs>'
    ]

    for edge in graph.edges():
        if edge.source not in coords or edge.target not in coords:
            continue
        x1, y1 = coords[edge.source]
        x2, y2 = coords[edge.target]
        color = _edge_color(graph, edge_color, edge)
        w = 3.0 if color != "#888888" else 1.8
        marker = ' marker-end="url(#arrow)"' if graph.directed else ""
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{html.escape(color)}" stroke-width="{w}"{marker}></line>'
        )
        label = None
        if show_weights and edge.weight != 1.0:
            label = f"{edge.weight:g}"
        elif show_edge_labels and edge.label:
            label = edge.label
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            parts.append(
                f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" dominant-baseline="central" '
                f'font-size="12" fill="#24313a" paint-order="stroke" stroke="#ffffff" '
                f'stroke-width="4" stroke-linejoin="round">{html.escape(str(label))}</text>'
            )

    for node in graph.nodes():
        if node.id not in coords:
            continue
        x, y = coords[node.id]
        color = node_color.get(node.id, "#4A90D9") if isinstance(node_color, dict) else node_color
        r = max(20, min(38, 12 + len(str(node.label)) * 3))
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{html.escape(color)}" '
            f'stroke="#ffffff" stroke-width="2.5"></circle>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="central" '
            f'font-size="12" font-weight="700" fill="#ffffff">{html.escape(str(node.label))}</text>'
        )

    body = "\n  ".join(parts)
    safe_title = html.escape(title)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(width)} {int(height)}" width="{int(width)}" height="{int(height)}" role="img" aria-label="{safe_title}">
  <title>{safe_title}</title>
  <rect width="100%" height="100%" fill="#ffffff"></rect>
  {body}
</svg>
"""


def save_svg(graph, path, **kwargs):
    """Save graph as a standalone static SVG file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(to_svg(graph, **kwargs))


def _fit_positions(positions, width, height, pad=64):
    """Scale layout coordinates into the SVG viewport with a margin."""
    if not positions:
        return {}
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1e-6)
    span_y = max(max_y - min_y, 1e-6)
    inner_w = max(width - pad * 2, 1)
    inner_h = max(height - pad * 2, 1)
    return {
        nid: (pad + (x - min_x) / span_x * inner_w, pad + (y - min_y) / span_y * inner_h)
        for nid, (x, y) in positions.items()
    }


def to_edge_list(graph):
    """
    Export as edge list string.
    Format: one edge per line: ``source target [weight]``
    """
    lines = []
    for e in graph.edges():
        if e.weight != 1.0:
            lines.append(f"{e.source}\t{e.target}\t{e.weight}")
        else:
            lines.append(f"{e.source}\t{e.target}")
    return "\n".join(lines)


def from_edge_list(text, directed=False, weighted=False):
    """
    Import from edge list string.
    Each line: ``source target [weight]``
    """
    g = Graph(directed=directed)
    for line in text.strip().splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        src, dst = parts[0], parts[1]
        w = float(parts[2]) if len(parts) > 2 and weighted else 1.0
        g.add_edge(src, dst, weight=w)
    return g



def to_adjacency_matrix(graph):
    """
    Export as adjacency matrix.

    Returns
    -------
    matrix : list of list of float
        matrix[i][j] = edge weight (0 if no edge).
    ids : list
        Node IDs corresponding to rows/columns.
    """
    ids = [n.id for n in graph.nodes()]
    idx = {nid: i for i, nid in enumerate(ids)}
    n = len(ids)
    matrix = [[0.0] * n for _ in range(n)]

    for e in graph.edges():
        i, j = idx[e.source], idx[e.target]
        matrix[i][j] = e.weight
        if not graph.directed:
            matrix[j][i] = e.weight

    return matrix, ids


def from_adjacency_matrix(matrix, ids=None, directed=False):
    """
    Import from adjacency matrix.

    Parameters
    ----------
    matrix : list of list of float
        Adjacency matrix (non-zero = edge weight).
    ids : list | None
        Node IDs. Defaults to 0..n-1.
    directed : bool
    """
    n = len(matrix)
    if ids is None:
        ids = list(range(n))
    g = Graph(directed=directed)
    for nid in ids:
        g.add_node(nid)
    for i in range(n):
        start = 0 if directed else i + 1
        for j in range(start, n):
            if matrix[i][j] != 0:
                g.add_edge(ids[i], ids[j], weight=matrix[i][j])
    return g



def _serialize(val):
    """Make value JSON-serializable (tuples -> lists, etc.)."""
    if isinstance(val, tuple):
        return list(val)
    return val


def _html_id(val):
    return json.dumps(_serialize(val), ensure_ascii=False)


def _edge_color(graph, edge_color, edge):
    if not isinstance(edge_color, dict):
        return edge_color
    key = (edge.source, edge.target)
    if key in edge_color:
        return edge_color[key]
    reverse_key = (edge.target, edge.source)
    if not graph.directed and reverse_key in edge_color:
        return edge_color[reverse_key]
    return "#888888"
