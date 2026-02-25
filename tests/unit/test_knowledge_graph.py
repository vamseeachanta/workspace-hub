"""
ABOUTME: TDD tests for Domain Knowledge Graph — WRK-183
ABOUTME: Tests taxonomy loading, graph construction, query engine, and skill suggestion
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

# We import from the module we are about to build
from src.knowledge_graph.graph_engine import (
    KnowledgeGraph,
    GraphNode,
    GraphEdge,
    SkillSuggestion,
)
from src.knowledge_graph.taxonomy_loader import TaxonomyLoader
from src.knowledge_graph.session_advisor import SessionAdvisor
from src.knowledge_graph.visualizer import GraphVisualizer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TAXONOMY_YAML = """
version: "1.0"
domains:
  - id: naval_architecture
    label: Naval Architecture
  - id: structural_engineering
    label: Structural Engineering
  - id: metocean
    label: Metocean

nodes:
  - id: hull_form
    label: Hull Form
    domain: naval_architecture
    tags: [geometry, design]
  - id: displacement
    label: Displacement
    domain: naval_architecture
    tags: [hydrostatics, design]
  - id: stability
    label: Stability
    domain: naval_architecture
    tags: [hydrostatics, safety]
  - id: mooring_loads
    label: Mooring Loads
    domain: structural_engineering
    tags: [loads, design]
  - id: fatigue
    label: Fatigue
    domain: structural_engineering
    tags: [integrity, assessment]
  - id: wave_environment
    label: Wave Environment
    domain: metocean
    tags: [environmental, loading]
  - id: wind_environment
    label: Wind Environment
    domain: metocean
    tags: [environmental, loading]
  - id: current_environment
    label: Current Environment
    domain: metocean
    tags: [environmental, loading]
  - id: structural_response
    label: Structural Response
    domain: structural_engineering
    tags: [analysis, loads]

edges:
  - source: hull_form
    target: displacement
    relation: determines
    weight: 1.0
  - source: displacement
    target: stability
    relation: influences
    weight: 0.9
  - source: stability
    target: mooring_loads
    relation: affects
    weight: 0.7
  - source: mooring_loads
    target: fatigue
    relation: drives
    weight: 0.8
  - source: wave_environment
    target: mooring_loads
    relation: contributes_to
    weight: 0.9
  - source: wind_environment
    target: mooring_loads
    relation: contributes_to
    weight: 0.7
  - source: current_environment
    target: mooring_loads
    relation: contributes_to
    weight: 0.6
  - source: wave_environment
    target: structural_response
    relation: excites
    weight: 1.0
  - source: structural_response
    target: fatigue
    relation: causes
    weight: 0.95

skills_map:
  hull_form:
    - vessel-hull-design
    - hydrostatics-analysis
  displacement:
    - hydrostatics-analysis
  stability:
    - stability-analysis
    - intact-stability
  mooring_loads:
    - mooring-analysis
    - orca3d-skill
  fatigue:
    - fatigue-assessment
    - rainflow-counting
  wave_environment:
    - metocean-analysis
    - wave-scatter
  wind_environment:
    - metocean-analysis
    - wind-loading
  current_environment:
    - metocean-analysis
    - current-loading
  structural_response:
    - fem-analysis
    - structural-assessment
"""


@pytest.fixture
def taxonomy_data() -> dict:
    return yaml.safe_load(TAXONOMY_YAML)


@pytest.fixture
def taxonomy_file(tmp_path, taxonomy_data) -> Path:
    p = tmp_path / "taxonomy.yaml"
    p.write_text(yaml.dump(taxonomy_data))
    return p


@pytest.fixture
def kg(taxonomy_data) -> KnowledgeGraph:
    """Fully populated KnowledgeGraph from fixture data."""
    loader = TaxonomyLoader()
    return loader.load_from_dict(taxonomy_data)


# ---------------------------------------------------------------------------
# Phase 1 — Taxonomy YAML loading
# ---------------------------------------------------------------------------

class TestTaxonomyLoader:
    """Tests for TaxonomyLoader — Phase 1."""

    def test_load_from_dict_returns_knowledge_graph(self, taxonomy_data):
        loader = TaxonomyLoader()
        result = loader.load_from_dict(taxonomy_data)
        assert isinstance(result, KnowledgeGraph)

    def test_load_from_file_returns_knowledge_graph(self, taxonomy_file):
        loader = TaxonomyLoader()
        result = loader.load_from_file(taxonomy_file)
        assert isinstance(result, KnowledgeGraph)

    def test_node_count_matches_taxonomy(self, taxonomy_data):
        loader = TaxonomyLoader()
        kg = loader.load_from_dict(taxonomy_data)
        expected = len(taxonomy_data["nodes"])
        assert kg.node_count == expected

    def test_edge_count_matches_taxonomy(self, taxonomy_data):
        loader = TaxonomyLoader()
        kg = loader.load_from_dict(taxonomy_data)
        expected = len(taxonomy_data["edges"])
        assert kg.edge_count == expected

    def test_missing_version_raises_value_error(self):
        loader = TaxonomyLoader()
        bad = {"nodes": [], "edges": []}
        with pytest.raises(ValueError, match="version"):
            loader.load_from_dict(bad)

    def test_nonexistent_file_raises_file_not_found(self):
        loader = TaxonomyLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_from_file(Path("/nonexistent/taxonomy.yaml"))

    def test_node_has_correct_domain(self, taxonomy_data):
        loader = TaxonomyLoader()
        kg = loader.load_from_dict(taxonomy_data)
        node = kg.get_node("hull_form")
        assert node.domain == "naval_architecture"

    def test_node_has_tags(self, taxonomy_data):
        loader = TaxonomyLoader()
        kg = loader.load_from_dict(taxonomy_data)
        node = kg.get_node("hull_form")
        assert "geometry" in node.tags
        assert "design" in node.tags


# ---------------------------------------------------------------------------
# Phase 2 — Graph data structure and query engine
# ---------------------------------------------------------------------------

class TestKnowledgeGraphNodes:
    """Tests for node access and metadata."""

    def test_get_node_by_id_returns_graph_node(self, kg):
        node = kg.get_node("hull_form")
        assert isinstance(node, GraphNode)
        assert node.id == "hull_form"
        assert node.label == "Hull Form"

    def test_get_nonexistent_node_returns_none(self, kg):
        assert kg.get_node("does_not_exist") is None

    def test_get_nodes_by_domain_naval_architecture(self, kg):
        nodes = kg.get_nodes_by_domain("naval_architecture")
        ids = {n.id for n in nodes}
        assert "hull_form" in ids
        assert "displacement" in ids
        assert "stability" in ids

    def test_get_nodes_by_domain_metocean(self, kg):
        nodes = kg.get_nodes_by_domain("metocean")
        ids = {n.id for n in nodes}
        assert "wave_environment" in ids
        assert "wind_environment" in ids

    def test_get_nodes_by_tag_returns_matching(self, kg):
        nodes = kg.get_nodes_by_tag("hydrostatics")
        ids = {n.id for n in nodes}
        assert "displacement" in ids
        assert "stability" in ids

    def test_all_nodes_returns_all(self, kg):
        nodes = kg.all_nodes()
        assert len(nodes) == 9


class TestKnowledgeGraphEdges:
    """Tests for edge access and relations."""

    def test_get_neighbors_hull_form(self, kg):
        neighbors = kg.get_neighbors("hull_form")
        ids = {n.id for n in neighbors}
        assert "displacement" in ids

    def test_get_predecessors_stability(self, kg):
        preds = kg.get_predecessors("stability")
        ids = {n.id for n in preds}
        assert "displacement" in ids

    def test_get_edge_returns_graph_edge(self, kg):
        edge = kg.get_edge("hull_form", "displacement")
        assert isinstance(edge, GraphEdge)
        assert edge.relation == "determines"
        assert edge.weight == pytest.approx(1.0)

    def test_get_nonexistent_edge_returns_none(self, kg):
        assert kg.get_edge("hull_form", "fatigue") is None

    def test_edges_from_node_count(self, kg):
        edges = kg.get_edges_from("wave_environment")
        assert len(edges) == 2  # mooring_loads and structural_response


class TestKnowledgeGraphTraversal:
    """Tests for transitive discovery — the core value of the graph."""

    def test_reachable_from_hull_form_includes_fatigue(self, kg):
        """Transitive: hull_form -> displacement -> stability -> mooring_loads -> fatigue."""
        reachable = kg.reachable_from("hull_form")
        ids = {n.id for n in reachable}
        assert "fatigue" in ids

    def test_reachable_from_hull_form_excludes_self(self, kg):
        reachable = kg.reachable_from("hull_form")
        ids = {n.id for n in reachable}
        assert "hull_form" not in ids

    def test_shortest_path_hull_form_to_fatigue(self, kg):
        path = kg.shortest_path("hull_form", "fatigue")
        assert path is not None
        assert path[0] == "hull_form"
        assert path[-1] == "fatigue"
        # Path must pass through the chain
        assert "displacement" in path
        assert "stability" in path
        assert "mooring_loads" in path

    def test_shortest_path_no_path_returns_none(self, kg):
        # fatigue has no outgoing edges in our test taxonomy
        path = kg.shortest_path("fatigue", "hull_form")
        assert path is None

    def test_reachable_from_nonexistent_node_returns_empty(self, kg):
        reachable = kg.reachable_from("does_not_exist")
        assert reachable == []

    def test_ancestors_of_fatigue_includes_hull_form(self, kg):
        ancs = kg.ancestors_of("fatigue")
        ids = {n.id for n in ancs}
        assert "hull_form" in ids
        assert "mooring_loads" in ids
        assert "stability" in ids

    def test_common_ancestors_mooring_and_fatigue(self, kg):
        common = kg.common_ancestors("mooring_loads", "fatigue")
        ids = {n.id for n in common}
        assert "hull_form" in ids
        assert "wave_environment" in ids

    def test_depth_limited_reachable_respects_limit(self, kg):
        reachable = kg.reachable_from("hull_form", max_depth=1)
        ids = {n.id for n in reachable}
        assert "displacement" in ids
        # stability is 2 hops away — should not appear at depth=1
        assert "stability" not in ids


# ---------------------------------------------------------------------------
# Phase 3 — Session Advisor (skill suggestion)
# ---------------------------------------------------------------------------

class TestSessionAdvisor:
    """Tests for skill suggestion when entering a domain area."""

    def test_suggest_skills_for_hull_form_includes_hydrostatics(self, kg):
        advisor = SessionAdvisor(kg)
        suggestions = advisor.suggest_skills(["hull_form"])
        skill_names = {s.skill for s in suggestions}
        assert "hydrostatics-analysis" in skill_names

    def test_suggest_skills_transitive_from_hull_form_includes_mooring(self, kg):
        """hull_form -> ... -> mooring_loads should surface mooring skills."""
        advisor = SessionAdvisor(kg)
        suggestions = advisor.suggest_skills(["hull_form"], depth=4)
        skill_names = {s.skill for s in suggestions}
        assert "mooring-analysis" in skill_names

    def test_suggest_skills_direct_nodes_only_at_depth_zero(self, kg):
        advisor = SessionAdvisor(kg)
        suggestions = advisor.suggest_skills(["hull_form"], depth=0)
        skill_names = {s.skill for s in suggestions}
        # Direct skills for hull_form only
        assert "vessel-hull-design" in skill_names
        assert "hydrostatics-analysis" in skill_names
        # Mooring skills should NOT appear at depth 0
        assert "mooring-analysis" not in skill_names

    def test_suggest_skills_multiple_entry_nodes(self, kg):
        advisor = SessionAdvisor(kg)
        suggestions = advisor.suggest_skills(["stability", "wave_environment"])
        skill_names = {s.skill for s in suggestions}
        assert "stability-analysis" in skill_names
        assert "metocean-analysis" in skill_names

    def test_suggestion_has_relevance_score(self, kg):
        advisor = SessionAdvisor(kg)
        suggestions = advisor.suggest_skills(["hull_form"])
        for s in suggestions:
            assert isinstance(s, SkillSuggestion)
            assert 0.0 <= s.relevance <= 1.0

    def test_suggestions_ordered_by_relevance_descending(self, kg):
        advisor = SessionAdvisor(kg)
        suggestions = advisor.suggest_skills(["hull_form"], depth=3)
        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                assert suggestions[i].relevance >= suggestions[i + 1].relevance

    def test_unknown_entry_node_returns_empty(self, kg):
        advisor = SessionAdvisor(kg)
        suggestions = advisor.suggest_skills(["nonexistent_concept"])
        assert suggestions == []

    def test_suggest_skills_from_domain_name(self, kg):
        advisor = SessionAdvisor(kg)
        suggestions = advisor.suggest_skills_for_domain("metocean")
        skill_names = {s.skill for s in suggestions}
        assert "metocean-analysis" in skill_names
        assert "wave-scatter" in skill_names


# ---------------------------------------------------------------------------
# Phase 5 — Visualizer (Mermaid)
# ---------------------------------------------------------------------------

class TestGraphVisualizer:
    """Tests for Mermaid diagram generation."""

    def test_to_mermaid_returns_string(self, kg):
        viz = GraphVisualizer(kg)
        output = viz.to_mermaid()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_mermaid_contains_graph_td_header(self, kg):
        viz = GraphVisualizer(kg)
        output = viz.to_mermaid()
        assert "graph TD" in output

    def test_mermaid_contains_node_ids(self, kg):
        viz = GraphVisualizer(kg)
        output = viz.to_mermaid()
        assert "hull_form" in output
        assert "fatigue" in output

    def test_mermaid_contains_edges(self, kg):
        viz = GraphVisualizer(kg)
        output = viz.to_mermaid()
        # At least one arrow should appear
        assert "-->" in output

    def test_to_html_report_returns_string_with_mermaid_block(self, kg):
        viz = GraphVisualizer(kg)
        html = viz.to_html_report(title="Domain Knowledge Graph")
        assert "<html" in html.lower() or "<!DOCTYPE" in html.lower()
        assert "mermaid" in html.lower()

    def test_mermaid_subgraph_per_domain(self, kg):
        viz = GraphVisualizer(kg)
        output = viz.to_mermaid(group_by_domain=True)
        assert "subgraph" in output

    def test_write_html_report_creates_file(self, kg, tmp_path):
        viz = GraphVisualizer(kg)
        out_path = tmp_path / "knowledge-graph.html"
        viz.write_html_report(out_path, title="Test Graph")
        assert out_path.exists()
        content = out_path.read_text()
        assert "mermaid" in content.lower()


# ---------------------------------------------------------------------------
# Integration — load real taxonomy file
# ---------------------------------------------------------------------------

class TestRealTaxonomyIntegration:
    """Integration tests against the real taxonomy YAML shipped with the repo."""

    TAXONOMY_PATH = Path(__file__).parent.parent.parent / (
        "src/knowledge_graph/data/engineering-taxonomy.yaml"
    )

    def test_real_taxonomy_file_exists(self):
        assert self.TAXONOMY_PATH.exists(), (
            f"Real taxonomy not found at {self.TAXONOMY_PATH}"
        )

    def test_real_taxonomy_loads_without_error(self):
        loader = TaxonomyLoader()
        kg = loader.load_from_file(self.TAXONOMY_PATH)
        assert kg.node_count >= 50

    def test_real_taxonomy_has_minimum_edges(self):
        loader = TaxonomyLoader()
        kg = loader.load_from_file(self.TAXONOMY_PATH)
        assert kg.edge_count >= 100

    def test_real_taxonomy_hull_form_connects_to_fatigue(self):
        loader = TaxonomyLoader()
        kg = loader.load_from_file(self.TAXONOMY_PATH)
        reachable = kg.reachable_from("hull_form")
        ids = {n.id for n in reachable}
        assert "fatigue" in ids
