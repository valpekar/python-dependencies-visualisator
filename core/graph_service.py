"""
core/graph_service.py - Service layer for dependency graph logic
"""
import re
from typing import List
from packaging.requirements import Requirement
import networkx as nx

class DependencyGraphService:
    @staticmethod
    def parse_requirements(filename: str) -> List[str]:
        """
        Parse a requirements.txt file and return a list of package names (no versions/extras).
        Handles all pip requirement formats using packaging.Requirement.
        """
        packages = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                try:
                    req = Requirement(line)
                    packages.append(req.name)
                except Exception:
                    continue  # skip lines that aren't valid requirements
        return packages

    @staticmethod
    def filter_to_top_n_levels(G, roots, n):
        """
        Return a subgraph containing only nodes up to n levels deep from the given roots.
        Uses BFS to collect nodes up to depth n.
        For n==1, returns only the root nodes (no edges).
        """
        if n == 1:
            return G.subgraph(roots).copy()
        from collections import deque
        visited = set()
        queue = deque((root, 0) for root in roots)
        while queue:
            node, depth = queue.popleft()
            if node in visited or depth > n:
                continue
            visited.add(node)
            if depth < n:
                for child in G.successors(node):
                    queue.append((child, depth + 1))
        return G.subgraph(visited).copy()

    @staticmethod
    def filter_to_top_n_levels_unique_colored(G, roots, n):
        """
        BFS from each root, tracking node levels and which root(s) each node is reachable from.
        For each level > 1, only include nodes unique to a single root at that level.
        Returns: (subgraph, node_levels, node_roots)
        """
        from collections import deque, defaultdict
        node_levels = {}
        node_roots = {}
        visited = set()
        all_nodes = set()
        for root in roots:
            queue = deque([(root, 1)])
            local_visited = set()
            while queue:
                node, level = queue.popleft()
                if level > n or (node, level) in local_visited:
                    continue
                local_visited.add((node, level))
                all_nodes.add(node)
                # Track the lowest level at which this node is seen
                if node not in node_levels or level < node_levels[node]:
                    node_levels[node] = level
                # Track which root(s) this node is reachable from
                node_roots.setdefault(node, set()).add(root)
                if level < n:
                    for child in G.successors(node):
                        queue.append((child, level + 1))
        # For each level > 1, only keep nodes unique to a single root at that level
        filtered_nodes = set()
        for node, level in node_levels.items():
            if level == 1:
                filtered_nodes.add(node)
            elif len(node_roots[node]) == 1:
                filtered_nodes.add(node)
        subgraph = G.subgraph(filtered_nodes).copy()
        return subgraph, node_levels, {k: list(v)[0] if len(v) == 1 else None for k, v in node_roots.items()}

    @staticmethod
    def filter_to_top_n_levels_with_shared_clusters(G, roots, n):
        """
        For each root, at each level, cluster shared dependencies into a synthetic node per root.
        Returns: (subgraph, node_levels, node_roots, shared_clusters)
        shared_clusters: dict of synthetic node -> list of shared dependencies for tooltip.
        """
        from collections import deque, defaultdict
        node_levels = {}
        node_roots = {}
        visited = set()
        all_nodes = set()
        # For each root, track nodes at each level
        root_level_nodes = defaultdict(lambda: defaultdict(set))  # root -> level -> set(nodes)
        for root in roots:
            queue = deque([(root, 1)])
            local_visited = set()
            while queue:
                node, level = queue.popleft()
                if level > n or (node, level) in local_visited:
                    continue
                local_visited.add((node, level))
                all_nodes.add(node)
                node_levels[node] = min(level, node_levels.get(node, level))
                node_roots.setdefault(node, set()).add(root)
                root_level_nodes[root][level].add(node)
                if level < n:
                    for child in G.successors(node):
                        queue.append((child, level + 1))
        # For each level > 1, cluster shared dependencies
        filtered_nodes = set()
        edges = set()
        shared_clusters = {}
        for root in roots:
            filtered_nodes.add(root)
            for level in range(2, n+1):
                nodes = root_level_nodes[root][level]
                unique = set()
                shared = set()
                for node in nodes:
                    if len(node_roots[node]) == 1:
                        unique.add(node)
                    else:
                        shared.add(node)
                # Add unique nodes and edges
                for node in unique:
                    filtered_nodes.add(node)
                    edges.add((root, node))
                # Cluster shared nodes
                if shared:
                    cluster_name = f"Shared for {root} (level {level})"
                    filtered_nodes.add(cluster_name)
                    edges.add((root, cluster_name))
                    shared_clusters[cluster_name] = sorted(shared)
        # Build subgraph
        subgraph = nx.DiGraph()
        subgraph.add_nodes_from(filtered_nodes)
        subgraph.add_edges_from(edges)
        # Assign levels for synthetic nodes
        for cluster in shared_clusters:
            node_levels[cluster] = int(cluster.split('level ')[-1].rstrip(')'))
        return subgraph, node_levels, node_roots, shared_clusters 

    @staticmethod
    def filter_to_top_n_levels_with_shared_nodes(G, roots, n):
        """
        For each root, at each level, show unique and shared dependencies as real nodes.
        Shared dependencies are colored purple and have edges from all relevant roots.
        Returns: (subgraph, node_levels, node_roots, shared_nodes)
        shared_nodes: set of shared dependency node names.
        """
        from collections import deque, defaultdict
        node_levels = {}
        node_roots = {}
        visited = set()
        all_nodes = set()
        root_level_nodes = defaultdict(lambda: defaultdict(set))  # root -> level -> set(nodes)
        for root in roots:
            queue = deque([(root, 1)])
            local_visited = set()
            while queue:
                node, level = queue.popleft()
                if level > n or (node, level) in local_visited:
                    continue
                local_visited.add((node, level))
                all_nodes.add(node)
                node_levels[node] = min(level, node_levels.get(node, level))
                node_roots.setdefault(node, set()).add(root)
                root_level_nodes[root][level].add(node)
                if level < n:
                    for child in G.successors(node):
                        queue.append((child, level + 1))
        # For each level > 1, add unique and shared nodes
        filtered_nodes = set()
        edges = set()
        shared_nodes = set()
        for root in roots:
            filtered_nodes.add(root)
            for level in range(2, n+1):
                nodes = root_level_nodes[root][level]
                for node in nodes:
                    filtered_nodes.add(node)
                    edges.add((root, node))
                    if len(node_roots[node]) > 1:
                        shared_nodes.add(node)
        # Build subgraph
        subgraph = nx.DiGraph()
        subgraph.add_nodes_from(filtered_nodes)
        subgraph.add_edges_from(edges)
        return subgraph, node_levels, node_roots, shared_nodes 