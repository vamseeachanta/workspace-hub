"""
ABOUTME: Core graph data structure and query engine for Domain Knowledge Graph
ABOUTME: Wraps networkx DiGraph with domain-aware node/edge access and traversal queries
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """A concept node in the domain knowledge graph."""

    id: str
    label: str
    domain: str
    tags: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class GraphEdge:
    """A directed relationship between two concept nodes."""

    source: str
    target: str
    relation: str
    weight: float = 1.0


@dataclass
class SkillSuggestion:
    """A suggested skill derived from a concept node traversal."""

    skill: str
    source_node: str
    relevance: float  # 0.0 – 1.0; higher is more relevant


class KnowledgeGraph:
    """
    Directed knowledge graph over engineering concept nodes.

    Wraps a networkx DiGraph.  All public query methods operate on node IDs
    (strings) and return domain objects (GraphNode, GraphEdge, etc.) so that
    callers never need to interact with networkx directly.
    """

    def __init__(self) -> None:
        self._graph: nx.DiGraph = nx.DiGraph()
        self._nodes: dict[str, GraphNode] = {}
        self._skills_map: dict[str, list[str]] = {}

    # ------------------------------------------------------------------
    # Mutation helpers (used by TaxonomyLoader only)
    # ------------------------------------------------------------------

    def add_node(self, node: GraphNode) -> None:
        """Add a concept node to the graph."""
        self._nodes[node.id] = node
        self._graph.add_node(node.id, domain=node.domain, tags=node.tags)

    def add_edge(self, edge: GraphEdge) -> None:
        """Add a directed relationship edge."""
        self._graph.add_edge(
            edge.source,
            edge.target,
            relation=edge.relation,
            weight=edge.weight,
        )

    def set_skills_map(self, skills_map: dict[str, list[str]]) -> None:
        """Register concept → list-of-skills mapping."""
        self._skills_map = dict(skills_map)

    # ------------------------------------------------------------------
    # Size
    # ------------------------------------------------------------------

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return self._graph.number_of_edges()

    # ------------------------------------------------------------------
    # Node access
    # ------------------------------------------------------------------

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Return a node by ID, or None if not found."""
        return self._nodes.get(node_id)

    def all_nodes(self) -> list[GraphNode]:
        """Return all nodes."""
        return list(self._nodes.values())

    def get_nodes_by_domain(self, domain: str) -> list[GraphNode]:
        """Return nodes belonging to a given domain."""
        return [n for n in self._nodes.values() if n.domain == domain]

    def get_nodes_by_tag(self, tag: str) -> list[GraphNode]:
        """Return nodes that carry a given tag."""
        return [n for n in self._nodes.values() if tag in n.tags]

    # ------------------------------------------------------------------
    # Edge access
    # ------------------------------------------------------------------

    def get_edge(self, source: str, target: str) -> Optional[GraphEdge]:
        """Return an edge by (source, target), or None."""
        if not self._graph.has_edge(source, target):
            return None
        data = self._graph[source][target]
        return GraphEdge(
            source=source,
            target=target,
            relation=data.get("relation", ""),
            weight=data.get("weight", 1.0),
        )

    def get_neighbors(self, node_id: str) -> list[GraphNode]:
        """Return direct successor nodes (outgoing edges)."""
        return [
            self._nodes[nid]
            for nid in self._graph.successors(node_id)
            if nid in self._nodes
        ]

    def get_predecessors(self, node_id: str) -> list[GraphNode]:
        """Return direct predecessor nodes (incoming edges)."""
        return [
            self._nodes[nid]
            for nid in self._graph.predecessors(node_id)
            if nid in self._nodes
        ]

    def get_edges_from(self, node_id: str) -> list[GraphEdge]:
        """Return all edges originating from a node."""
        return [
            GraphEdge(
                source=node_id,
                target=target,
                relation=data.get("relation", ""),
                weight=data.get("weight", 1.0),
            )
            for target, data in self._graph[node_id].items()
            if self._graph.has_node(node_id)
        ]

    # ------------------------------------------------------------------
    # Traversal queries
    # ------------------------------------------------------------------

    def reachable_from(
        self, node_id: str, max_depth: Optional[int] = None
    ) -> list[GraphNode]:
        """
        Return all nodes reachable from node_id via directed edges.

        Args:
            node_id:   Starting concept node ID.
            max_depth: If set, limit BFS depth.  None means unlimited.

        Returns:
            List of reachable GraphNode objects (source node excluded).
        """
        if node_id not in self._nodes:
            return []
        if max_depth is None:
            reachable_ids = nx.descendants(self._graph, node_id)
        else:
            reachable_ids = set()
            frontier = {node_id}
            for _ in range(max_depth):
                next_frontier: set[str] = set()
                for nid in frontier:
                    for succ in self._graph.successors(nid):
                        if succ != node_id and succ not in reachable_ids:
                            reachable_ids.add(succ)
                            next_frontier.add(succ)
                frontier = next_frontier
                if not frontier:
                    break
        return [self._nodes[nid] for nid in reachable_ids if nid in self._nodes]

    def ancestors_of(self, node_id: str) -> list[GraphNode]:
        """Return all ancestor nodes (i.e. nodes that can reach node_id)."""
        if node_id not in self._nodes:
            return []
        anc_ids = nx.ancestors(self._graph, node_id)
        return [self._nodes[nid] for nid in anc_ids if nid in self._nodes]

    def common_ancestors(self, node_a: str, node_b: str) -> list[GraphNode]:
        """Return nodes that are ancestors of both node_a and node_b."""
        anc_a = set(n.id for n in self.ancestors_of(node_a)) | {node_a}
        anc_b = set(n.id for n in self.ancestors_of(node_b)) | {node_b}
        common_ids = anc_a & anc_b - {node_a, node_b}
        return [self._nodes[nid] for nid in common_ids if nid in self._nodes]

    def shortest_path(self, source: str, target: str) -> Optional[list[str]]:
        """
        Return the shortest directed path from source to target as a list of
        node IDs, or None if no path exists.
        """
        try:
            return nx.shortest_path(self._graph, source=source, target=target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    # ------------------------------------------------------------------
    # Skills map access
    # ------------------------------------------------------------------

    def skills_for_node(self, node_id: str) -> list[str]:
        """Return skills directly associated with a concept node."""
        return list(self._skills_map.get(node_id, []))
