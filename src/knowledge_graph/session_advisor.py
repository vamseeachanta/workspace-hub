"""
ABOUTME: Session Advisor — suggests relevant skills based on concept graph traversal
ABOUTME: Phase 3 integration: given entry-point concepts, traverse graph and rank skills
"""

from __future__ import annotations

import logging
from collections import defaultdict

from .graph_engine import KnowledgeGraph, SkillSuggestion

logger = logging.getLogger(__name__)

# Weight decay applied per hop when propagating relevance through the graph
_HOP_DECAY = 0.7


class SessionAdvisor:
    """
    Suggest engineering skills relevant to a set of entry-point concept nodes.

    Traverses the knowledge graph up to a configurable depth and scores each
    skill by a relevance measure derived from edge weights and hop distance.
    Skills for directly-provided nodes receive relevance = 1.0 (before edge
    weighting).  Skills reached transitively are discounted by _HOP_DECAY per
    hop.
    """

    def __init__(self, kg: KnowledgeGraph) -> None:
        self._kg = kg

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def suggest_skills(
        self,
        entry_nodes: list[str],
        depth: int = 2,
    ) -> list[SkillSuggestion]:
        """
        Return skills suggested by the provided concept entry-point nodes.

        Args:
            entry_nodes: Concept node IDs that represent the current domain.
            depth:       Traversal depth. 0 = direct skills only.

        Returns:
            Sorted list of SkillSuggestion (highest relevance first).
            Returns [] for unknown node IDs.
        """
        # Filter to known nodes
        valid_nodes = [n for n in entry_nodes if self._kg.get_node(n) is not None]
        if not valid_nodes:
            return []

        # Map skill → best relevance score across all entry paths
        skill_relevance: dict[str, float] = defaultdict(float)
        skill_source: dict[str, str] = {}

        for node_id in valid_nodes:
            self._collect_skills(
                node_id=node_id,
                current_relevance=1.0,
                remaining_depth=depth,
                skill_relevance=skill_relevance,
                skill_source=skill_source,
                visited=set(),
            )

        suggestions = [
            SkillSuggestion(
                skill=skill,
                source_node=skill_source[skill],
                relevance=round(score, 4),
            )
            for skill, score in skill_relevance.items()
        ]
        suggestions.sort(key=lambda s: s.relevance, reverse=True)
        return suggestions

    def suggest_skills_for_domain(self, domain: str) -> list[SkillSuggestion]:
        """
        Suggest skills for all concept nodes belonging to a domain.

        Equivalent to suggest_skills with all domain node IDs as entry_nodes.
        """
        domain_nodes = [n.id for n in self._kg.get_nodes_by_domain(domain)]
        return self.suggest_skills(domain_nodes, depth=1)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _collect_skills(
        self,
        node_id: str,
        current_relevance: float,
        remaining_depth: int,
        skill_relevance: dict[str, float],
        skill_source: dict[str, str],
        visited: set[str],
    ) -> None:
        if node_id in visited:
            return
        visited.add(node_id)

        # Register direct skills for this node
        for skill in self._kg.skills_for_node(node_id):
            if skill_relevance[skill] < current_relevance:
                skill_relevance[skill] = current_relevance
                skill_source[skill] = node_id

        if remaining_depth <= 0:
            return

        # Recurse into successors with decayed relevance
        for edge in self._kg.get_edges_from(node_id):
            child_relevance = current_relevance * edge.weight * _HOP_DECAY
            self._collect_skills(
                node_id=edge.target,
                current_relevance=child_relevance,
                remaining_depth=remaining_depth - 1,
                skill_relevance=skill_relevance,
                skill_source=skill_source,
                visited=visited,
            )
