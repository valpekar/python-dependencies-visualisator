import os
import re
import sys
import logging
import argparse
from typing import List, Dict, Set, Optional
import requests
import networkx as nx
from pyvis.network import Network
from assets import PYVIS_OPTIONS, HTML_CSS, HTML_LOADING_JS, HTML_ZOOM_JS
from exporter.html_exporter import visualize_graph
from exporter.pdf_exporter import export_pdf_with_playwright
from core.graph_service import DependencyGraphService
from config import DEFAULT_MAX_DEPTH
from packaging.requirements import Requirement

# --- Configuration Constants ---
REQUIREMENTS_FILE = 'requirements.txt'
DEFAULT_OUTPUT_HTML = 'dependency_graph.html'
GRAPH_WIDTH_PX = 2400
GRAPH_HEIGHT_PX = 1600

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# --- PyPI Dependency Fetching ---
def fetch_dependencies(
    package: str,
    seen: Optional[Set[str]] = None,
    depth: int = 0,
    max_depth: int = 2
) -> Dict[str, List[str]]:
    """Recursively fetch dependencies for a package from PyPI."""
    if seen is None:
        seen = set()
    if package in seen or depth > max_depth:
        return {}
    seen.add(package)
    url = f'https://pypi.org/pypi/{package}/json'
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            logger.warning(f"PyPI returned status {resp.status_code} for {package}")
            return {}
        info = resp.json()
        requires_dist = info['info'].get('requires_dist') or []
        deps = []
        for dep in requires_dist:
            try:
                dep_req = Requirement(dep)
                dep_name = dep_req.name
            except Exception:
                dep_name = re.split(r'[ ;\(\)]', dep)[0]
            if dep_name and dep_name.lower() != package.lower():
                deps.append(dep_name)
        result = {package: deps}
        for dep in deps:
            result.update(fetch_dependencies(dep, seen, depth+1, max_depth))
        return result
    except Exception as e:
        logger.warning(f"Failed to fetch dependencies for {package}: {e}")
        return {package: []}

# --- Graph Construction ---
def build_dependency_graph(packages: List[str], max_depth: int = 2) -> nx.DiGraph:
    """Build a directed dependency graph from a list of packages."""
    G = nx.DiGraph()
    for pkg in packages:
        dep_tree = fetch_dependencies(pkg, max_depth=max_depth)
        for parent, children in dep_tree.items():
            for child in children:
                G.add_edge(parent, child)
            if not children:
                G.add_node(parent)
    return G

# --- Graph Layout ---
def optimize_graph_layout(G: nx.DiGraph) -> None:
    """Optimize node positions for better PDF rendering (in-place)."""
    if len(G.nodes) == 0:
        return
    pos = nx.spring_layout(G, k=3, iterations=50)
    x_coords = [pos[node][0] for node in G.nodes]
    y_coords = [pos[node][1] for node in G.nodes]
    if x_coords and y_coords:
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        scale_factor = min(GRAPH_WIDTH_PX / max(x_range, 1), GRAPH_HEIGHT_PX / max(y_range, 1))
        for node in G.nodes:
            pos[node] = (pos[node][0] * scale_factor, pos[node][1] * scale_factor)
    # PyVis will use its own layout, but this helps for future extensibility

# --- Main Entrypoint ---
def main():
    parser = argparse.ArgumentParser(description='Python Dependency Visualizer')
    parser.add_argument('--file', type=str, default=REQUIREMENTS_FILE, help='Path to requirements.txt')
    parser.add_argument('--output', type=str, default=DEFAULT_OUTPUT_HTML, help='Output HTML file')
    parser.add_argument('--depth', type=int, default=DEFAULT_MAX_DEPTH, help='Max dependency depth')
    parser.add_argument('--pdf', type=str, default=None, help='Export graph to PDF (requires Playwright)')
    parser.add_argument('--levels', type=int, default=None, help='Only visualize the top N levels of dependencies (default: all)')
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        logger.error(f"Input file '{args.file}' does not exist.")
        sys.exit(1)

    pkgs = DependencyGraphService.parse_requirements(args.file)
    if not pkgs:
        logger.error("No packages found in requirements file.")
        sys.exit(1)

    logger.info(f"Building dependency graph for {len(pkgs)} package(s)...")
    G = build_dependency_graph(pkgs, max_depth=args.depth)
    optimize_graph_layout(G)
    if args.levels is not None:
        G, node_levels, node_roots, shared_nodes = DependencyGraphService.filter_to_top_n_levels_with_shared_nodes(G, pkgs, args.levels)
        visualize_graph(G, args.output, node_levels=node_levels, node_size=16, shared_nodes=shared_nodes)
    else:
        visualize_graph(G, args.output)
    if args.pdf:
        export_pdf_with_playwright(args.output, args.pdf)

if __name__ == '__main__':
    main()
