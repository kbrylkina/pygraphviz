import math
import matplotlib.pyplot as plt
import numpy as np

from .layout import circular_layout, force_directed_layout, hierarchical_layout

LAYOUTS = {
    "circular": circular_layout,
    "force": force_directed_layout,
    "hierarchical": hierarchical_layout,
}

DEFAULT_NODE_COLOR = "#4A90D9"
DEFAULT_EDGE_COLOR = "#888888"


class Renderer:
    def __init__(self, graph):
        self.graph = graph

    def draw(
        self,
        layout="force",
        figsize=(10, 8),
        node_color=DEFAULT_NODE_COLOR,
        node_size=800,
        edge_color=DEFAULT_EDGE_COLOR,
        font_size=9,
        show_weights=False,
        show_edge_labels=False,
        title=None,
        save_path=None,
        **layout_kwargs,
    ):
        """
        Render the graph.

        Parameters
        ----------
        layout : str
            One of 'force', 'circular', 'hierarchical'.
        figsize : tuple
            Matplotlib figure size.
        node_color : str | dict
            Single hex color or dict mapping node_id -> color.
        node_size : int
            Size of node markers.
        edge_color : str
            Color for edges.
        font_size : int
            Font size for node labels.
        show_weights : bool
            Display edge weights (skips weight=1.0 by default).
        show_edge_labels : bool
            Display edge labels if present.
        title : str | None
            Figure title.
        save_path : str | None
            If given, save figure to this path instead of showing it.
        **layout_kwargs
            Extra arguments forwarded to the layout function.
        """
        if self.graph.node_count() == 0:
            print("Graph is empty, nothing to draw.")
            return None, None

        layout_fn = LAYOUTS.get(layout)
        if layout_fn is None:
            raise ValueError(f"Unknown layout {layout!r}. Choose from: {list(LAYOUTS)}")

        positions = layout_fn(self.graph, **layout_kwargs)

        # Auto-scale figure size based on graph extent
        xs_raw = [p[0] for p in positions.values()]
        ys_raw = [p[1] for p in positions.values()]
        x_span = max(xs_raw) - min(xs_raw) or 1
        y_span = max(ys_raw) - min(ys_raw) or 1
        aspect = x_span / y_span
        fig_w = max(figsize[0], figsize[0] * aspect) if aspect > 1.2 else figsize[0]
        fig_h = max(figsize[1], figsize[1] / aspect) if aspect < 0.8 else figsize[1]

        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        ax.set_aspect("equal")
        ax.axis("off")

        if title:
            title_fs = 14 * max(1.0, fig_h / figsize[1])
            ax.set_title(title, fontsize=title_fs, fontweight="bold", pad=20)

        self._draw_edges(ax, positions, edge_color, show_weights, show_edge_labels)
        self._draw_nodes(ax, positions, node_color, node_size, font_size)

        margin = 0.3
        ax.set_xlim(min(xs_raw) - margin, max(xs_raw) + margin)
        ax.set_ylim(min(ys_raw) - margin, max(ys_raw) + margin)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Saved to {save_path}")
        else:
            plt.show()

        return fig, ax


    def _draw_edges(self, ax, positions, edge_color, show_weights, show_edge_labels):
        node_radius = 0.12  # approximate visual radius to shorten arrow endpoints

        for edge in self.graph.edges():
            x1, y1 = positions[edge.source]
            x2, y2 = positions[edge.target]

            if self.graph.directed:
                dx, dy = x2 - x1, y2 - y1
                dist = math.sqrt(dx * dx + dy * dy) or 1e-6
                tx = x2 - dx / dist * node_radius
                ty = y2 - dy / dist * node_radius

                ax.annotate(
                    "",
                    xy=(tx, ty),
                    xytext=(x1, y1),
                    arrowprops=dict(
                        arrowstyle="-|>",
                        color=edge_color,
                        lw=1.5,
                        mutation_scale=16,
                    ),
                    zorder=2,
                )
            else:
                ax.plot(
                    [x1, x2], [y1, y2],
                    color=edge_color,
                    linewidth=1.5,
                    zorder=1,
                )

            text = None
            if show_weights and edge.weight != 1.0:
                text = f"{edge.weight:g}"
            elif show_edge_labels and edge.label:
                text = edge.label

            if text:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(
                    mx, my, text,
                    fontsize=8,
                    ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white", alpha=0.75),
                    zorder=3,
                )

    def _draw_nodes(self, ax, positions, node_color, node_size, font_size):
        nodes = self.graph.nodes()

        if isinstance(node_color, dict):
            colors = [node_color.get(node.id, DEFAULT_NODE_COLOR) for node in nodes]
        else:
            colors = [node_color] * len(nodes)

        xs = [positions[node.id][0] for node in nodes]
        ys = [positions[node.id][1] for node in nodes]

        # Scale each node size based on label length so text fits
        sizes = []
        for node in nodes:
            label_len = len(node.label)
            if label_len <= 4:
                s = node_size
            else:
                s = node_size * max(1.0, (label_len / 4.0) ** 1.6)
            sizes.append(s)

        ax.scatter(
            xs, ys,
            s=sizes,
            c=colors,
            zorder=4,
            edgecolors="white",
            linewidths=2,
        )

        for node, x, y, s in zip(nodes, xs, ys, sizes):
            label = node.label
            # Scale font to fit inside node; longer labels get smaller font
            if len(label) <= 4:
                fs = font_size
            elif len(label) <= 7:
                fs = font_size * 0.85
            else:
                fs = max(6.5, font_size * 6.5 / len(label))

            ax.text(
                x, y, label,
                fontsize=fs,
                ha="center", va="center",
                fontweight="bold",
                color="white",
                zorder=5,
            )
