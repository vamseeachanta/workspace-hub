"""
ABOUTME: Taxonomy YAML loader for Domain Knowledge Graph
ABOUTME: Parses versioned YAML taxonomy files into KnowledgeGraph instances
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from .graph_engine import GraphEdge, GraphNode, KnowledgeGraph

logger = logging.getLogger(__name__)

_REQUIRED_TOP_LEVEL_KEYS = {"version", "nodes", "edges"}


class TaxonomyLoader:
    """
    Load a knowledge-graph taxonomy from a YAML file or a pre-parsed dict.

    YAML schema:
        version: "1.0"
        domains:         # optional list of domain metadata
          - id: <str>
            label: <str>
        nodes:
          - id: <str>         # unique concept identifier
            label: <str>      # human-readable name
            domain: <str>     # owning domain id
            tags: [<str>, …]  # optional
            description: <str>  # optional
        edges:
          - source: <str>     # source node id
            target: <str>     # target node id
            relation: <str>   # named relationship type
            weight: <float>   # 0.0–1.0 (default 1.0)
        skills_map:           # optional concept → skills mapping
          <node_id>: [<skill>, …]
    """

    def load_from_file(self, path: Path | str) -> KnowledgeGraph:
        """Parse a YAML file and return a KnowledgeGraph."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Taxonomy file not found: {path}")
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        logger.debug("Loaded taxonomy YAML from %s", path)
        return self.load_from_dict(data)

    def load_from_dict(self, data: dict[str, Any]) -> KnowledgeGraph:
        """Build a KnowledgeGraph from a pre-parsed taxonomy dict."""
        self._validate_structure(data)
        kg = KnowledgeGraph()

        for node_data in data.get("nodes", []):
            node = GraphNode(
                id=node_data["id"],
                label=node_data.get("label", node_data["id"]),
                domain=node_data.get("domain", ""),
                tags=list(node_data.get("tags", [])),
                description=node_data.get("description", ""),
            )
            kg.add_node(node)

        for edge_data in data.get("edges", []):
            edge = GraphEdge(
                source=edge_data["source"],
                target=edge_data["target"],
                relation=edge_data.get("relation", "relates_to"),
                weight=float(edge_data.get("weight", 1.0)),
            )
            kg.add_edge(edge)

        skills_map = data.get("skills_map", {})
        if skills_map:
            kg.set_skills_map(skills_map)

        logger.info(
            "Built KnowledgeGraph: %d nodes, %d edges",
            kg.node_count,
            kg.edge_count,
        )
        return kg

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_structure(self, data: dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise ValueError("Taxonomy must be a YAML mapping at the top level")
        if "version" not in data:
            raise ValueError(
                "Taxonomy YAML must contain a 'version' key — found none"
            )
        for key in ("nodes", "edges"):
            if key not in data:
                raise ValueError(f"Taxonomy YAML missing required key: '{key}'")
