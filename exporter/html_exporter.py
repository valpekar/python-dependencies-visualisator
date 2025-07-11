"""
html_exporter.py - HTML generation and post-processing for Python Dependency Visualizer CLI
"""
from typing import Optional
import networkx as nx
from pyvis.network import Network
from assets import PYVIS_OPTIONS, HTML_CSS, HTML_LOADING_JS, HTML_ZOOM_JS

# These should be imported from a config or main module in a larger project
GRAPH_WIDTH_PX = 2400
GRAPH_HEIGHT_PX = 1600
DEFAULT_OUTPUT_HTML = 'dependency_graph.html'


def postprocess_html(output_html: str) -> None:
    """Inject custom CSS/JS and minimalist loading overlay into the generated HTML."""
    with open(output_html, 'r', encoding='utf-8') as f:
        html = f.read()
    # Insert CSS after </head>
    html = html.replace('</head>', HTML_CSS.format(width=GRAPH_WIDTH_PX, height=GRAPH_HEIGHT_PX) + '</head>')
    # Insert minimalist loading text as a new element after <body>
    html = html.replace('<body>', '<body>\n<div id="minimalLoading">0%</div>')
    # Inject loading JS and zoom JS before </body>
    html = html.replace('</body>', HTML_LOADING_JS + HTML_ZOOM_JS + '</body>')
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)


def visualize_graph(
    G: nx.DiGraph,
    output_html: str = DEFAULT_OUTPUT_HTML,
    node_levels: dict = {},
    node_size: int = 16,
    shared_nodes: set = None
) -> None:
    """Render the dependency graph to HTML and post-process for UI/print quality. Optionally color nodes by level and show shared nodes in purple."""
    from pyvis.network import Network
    palette = ['#1976d2', '#388e3c', '#fbc02d', '#e64a19', '#7b1fa2', '#00838f', '#c2185b']
    shared_color = '#8e24aa'
    net = Network(
        height=f'{GRAPH_HEIGHT_PX}px',
        width=f'{GRAPH_WIDTH_PX}px',
        directed=True,
        notebook=False
    )
    if node_levels:
        # Find root nodes (level 1)
        roots = [node for node, lvl in node_levels.items() if lvl == 1]
        n_roots = len(roots)
        radius = 800
        import math
        root_positions = {}
        for i, node in enumerate(roots):
            angle = 2 * math.pi * i / n_roots
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            root_positions[node] = (x, y)
        for node in G.nodes:
            level = node_levels.get(node, 0)
            color = palette[(level-1) % len(palette)] if level > 0 else '#888'
            if shared_nodes and node in shared_nodes:
                size = node_size * 1.2
                net.add_node(
                    node,
                    label=node,
                    color=color,
                    size=size,
                    font={"size": node_size, "face": "Arial", "color": "#111", "bold": True}
                )
            elif node in root_positions:
                x, y = root_positions[node]
                net.add_node(
                    node,
                    label=node,
                    color=color,
                    size=node_size,
                    x=x,
                    y=y,
                    fixed=True,
                    font={"size": node_size, "face": "Arial", "color": "#111", "bold": True}
                )
            else:
                net.add_node(
                    node,
                    label=node,
                    color=color,
                    size=node_size,
                    font={"size": node_size, "face": "Arial", "color": "#111", "bold": True}
                )
        for source, target in G.edges:
            net.add_edge(source, target)
    else:
        net.from_nx(G)
    net.set_options(PYVIS_OPTIONS)
    net.write_html(output_html)
    postprocess_html(output_html) 