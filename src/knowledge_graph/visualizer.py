"""
ABOUTME: Graph visualizer — generates Mermaid diagrams and HTML reports
ABOUTME: Phase 5: produces human-readable visual representation of the knowledge graph
"""

from __future__ import annotations

import logging
import textwrap
from pathlib import Path

from .graph_engine import KnowledgeGraph

logger = logging.getLogger(__name__)

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    body {{ font-family: sans-serif; margin: 2rem; background: #f8f9fa; }}
    h1 {{ color: #333; }}
    .mermaid {{ background: white; padding: 1.5rem; border-radius: 8px;
               box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
    .meta {{ color: #666; font-size: 0.85rem; margin-top: 1rem; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p class="meta">Nodes: {node_count} | Edges: {edge_count}</p>
  <div class="mermaid">
{diagram}
  </div>
  <script>mermaid.initialize({{ startOnLoad: true, theme: 'default' }});</script>
</body>
</html>
"""


class GraphVisualizer:
    """
    Generate visual representations of a KnowledgeGraph.

    Supports:
    - Mermaid flowchart diagram (plain text, embeddable)
    - HTML report with embedded Mermaid (rendered via CDN)
    """

    def __init__(self, kg: KnowledgeGraph) -> None:
        self._kg = kg

    # ------------------------------------------------------------------
    # Mermaid diagram
    # ------------------------------------------------------------------

    def to_mermaid(self, group_by_domain: bool = False) -> str:
        """
        Render the graph as a Mermaid flowchart string.

        Args:
            group_by_domain: If True, wrap nodes in subgraph blocks per domain.

        Returns:
            Mermaid diagram source string.
        """
        lines: list[str] = ["graph TD"]

        if group_by_domain:
            lines.extend(self._mermaid_grouped())
        else:
            lines.extend(self._mermaid_flat())

        return "\n".join(lines)

    def to_html_report(self, title: str = "Domain Knowledge Graph") -> str:
        """Return an HTML string with an embedded Mermaid diagram."""
        diagram = self.to_mermaid(group_by_domain=True)
        indented = textwrap.indent(diagram, "    ")
        return _HTML_TEMPLATE.format(
            title=title,
            node_count=self._kg.node_count,
            edge_count=self._kg.edge_count,
            diagram=indented,
        )

    def write_html_report(
        self,
        path: Path | str,
        title: str = "Domain Knowledge Graph",
    ) -> None:
        """Write the HTML report to a file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        html = self.to_html_report(title=title)
        path.write_text(html, encoding="utf-8")
        logger.info("Knowledge graph HTML report written to %s", path)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _mermaid_flat(self) -> list[str]:
        lines: list[str] = []
        for node in self._kg.all_nodes():
            safe_id = self._safe_id(node.id)
            label = node.label.replace('"', "'")
            lines.append(f'    {safe_id}["{label}"]')
        for node in self._kg.all_nodes():
            for edge in self._kg.get_edges_from(node.id):
                src = self._safe_id(edge.source)
                tgt = self._safe_id(edge.target)
                rel = edge.relation.replace('"', "'")
                lines.append(f'    {src} -->|"{rel}"| {tgt}')
        return lines

    def _mermaid_grouped(self) -> list[str]:
        lines: list[str] = []
        domains: dict[str, list] = {}
        no_domain: list = []

        for node in self._kg.all_nodes():
            if node.domain:
                domains.setdefault(node.domain, []).append(node)
            else:
                no_domain.append(node)

        for domain, nodes in sorted(domains.items()):
            safe_domain = self._safe_id(domain)
            lines.append(f"    subgraph {safe_domain}[\"{domain.replace('_', ' ').title()}\"]")
            for node in nodes:
                safe_id = self._safe_id(node.id)
                label = node.label.replace('"', "'")
                lines.append(f'        {safe_id}["{label}"]')
            lines.append("    end")

        if no_domain:
            lines.append('    subgraph no_domain["Unclassified"]')
            for node in no_domain:
                safe_id = self._safe_id(node.id)
                label = node.label.replace('"', "'")
                lines.append(f'        {safe_id}["{label}"]')
            lines.append("    end")

        # Edges (outside subgraphs for cleaner rendering)
        for node in self._kg.all_nodes():
            for edge in self._kg.get_edges_from(node.id):
                src = self._safe_id(edge.source)
                tgt = self._safe_id(edge.target)
                rel = edge.relation.replace('"', "'")
                lines.append(f'    {src} -->|"{rel}"| {tgt}')

        return lines

    @staticmethod
    def _safe_id(node_id: str) -> str:
        """Convert a node ID to a Mermaid-safe identifier."""
        return node_id.replace("-", "_").replace(" ", "_")
