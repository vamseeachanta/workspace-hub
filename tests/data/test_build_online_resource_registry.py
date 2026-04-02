"""
ABOUTME: Tests for scripts/data/build-online-resource-registry.py
Tests catalog parsing for each of the 7 source formats, deduplication logic,
schema normalization, and YAML output format.
"""

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

HUB_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = HUB_ROOT / "scripts" / "data" / "build-online-resource-registry.py"


def load_module():
    """Load the build script as a module."""
    spec = importlib.util.spec_from_file_location("build_registry", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures — minimal YAML samples for each catalog format
# ---------------------------------------------------------------------------

CATALOG_YAML = """
resources:
  - id: dnv_standards
    name: DNV Standards Explorer
    category: engineering_standards
    subcategory: classification_society
    url: https://standards.dnv.com/explorer/
    auth_required: false
    cost_model: free
    relevance_score: 5
    related_module: digitalmodel/structural
    maturity: live
    notes: Full-text search across 650+ DNV rules
    discovery_status: known
  - id: openfoam
    name: OpenFOAM
    category: open_source_tools
    subcategory: cfd
    url: https://www.openfoam.com/
    auth_required: false
    cost_model: free
    relevance_score: 4
    related_module: digitalmodel/hydrodynamics
    maturity: live
    notes: Open-source CFD toolkit
    discovery_status: known
"""

ENGINEERING_CATALOG_YAML = """
schema_version: "1.0"
generated_at: "2026-03-01"
catalog_purpose: "Open-source engineering libraries"
domains:
  hydrodynamics:
    description: BEM solvers
    libraries:
      - name: Capytaine
        url: https://github.com/capytaine/capytaine
        project_url: https://capytaine.github.io/stable/
        license: GPL-3.0
        maturity: stable
        python_api: native
        community: medium
        capabilities: [BEM solver, wave diffraction]
        relevance_to_ace: Primary BEM solver
        integration_notes: pip-installable
  marine_offshore:
    description: Marine tools
    libraries:
      - name: MoorDyn
        url: https://github.com/FloatingArrayDesign/MoorDyn
        project_url: https://moordyn.readthedocs.io/
        license: BSD-3
        maturity: stable
        python_api: bindings
        community: medium
        capabilities: [mooring dynamics]
        relevance_to_ace: Mooring simulation
        integration_notes: C++ with Python bindings
"""

PUBLIC_OG_YAML = """
generated: "2026-03-01"
total_sources: 3
categories:
  already_ingested:
    - name: BSEE
      module: worldenergydata.bsee
      coverage: GOM offshore wells
      freshness: monthly
  known_not_ingested:
    - name: BOEM
      url: https://www.data.boem.gov/
      api: true
      data_format: CSV/Excel/API
      priority: high
      rationale: Offshore lease data
  newly_discovered:
    - name: Energy Institute Stats
      url: https://www.energyinst.org/statistical-review
      api: false
      data_format: Excel
      priority: medium
      rationale: Annual statistical review
"""

WEB_RESOURCES_YAML = """
cache_settings:
  max_age_days: 30
  max_size_mb: 100
enabled: true
search_history: []
sources: []
user_added_links:
  - added_by: user
    date_added: '2025-08-10T18:00:46.817617'
    notes: OrcaFlex official documentation
    title: OrcaFlex WebHelp
    type: user_added
    url: https://www.orcina.com/webhelp/OrcaFlex/
  - added_by: user
    date_added: '2025-08-10T18:01:00.000000'
    notes: DNV rules and standards
    title: DNV Rules
    type: user_added
    url: https://www.dnv.com/rules-standards/
"""

NAVAL_ARCH_YAML = """
category: naval-architecture
subcategory: reference-library
created_at: '2025-10-01'
textbooks:
  - title: "Principles of Naval Architecture, Volume I"
    author: SNAME
    year: 1988
    local_path: /mnt/ace/docs/_standards/SNAME/textbooks/PNA-Vol1.pdf
    source_url: https://navalifpe.wordpress.com/pna-vol1.pdf
    size_mb: 29
    topics: [stability, strength]
    notes: Classic SNAME set
online_portals:
  - title: Maritime Plans Index
    url: https://maritime.org/doc/plans/index.php
    notes: Historical ship plans
classification_portals:
  - title: ClassNK Rules
    url: https://www.classnk.com/hp/en/rules/tech_rules.aspx
    notes: ClassNK technical rules
pending_manual:
  - title: USNA Course Notes EN400
    url: https://www.usna.edu/NAOE/_files/documents/Courses/EN400/EN400.pdf
    notes: Naval engineering course notes
hydrostatics_stability: []
additional_resources: []
regulatory: []
"""


@pytest.fixture
def tmpdir_with_catalogs(tmp_path):
    """Create a temp directory with all catalog format samples."""
    catalog_dir = tmp_path / "catalogs"
    catalog_dir.mkdir()

    (catalog_dir / "catalog.yaml").write_text(CATALOG_YAML)
    (catalog_dir / "engineering-catalog.yaml").write_text(ENGINEERING_CATALOG_YAML)
    (catalog_dir / "public-og.yaml").write_text(PUBLIC_OG_YAML)
    (catalog_dir / "orcaflex-web.yaml").write_text(WEB_RESOURCES_YAML)
    (catalog_dir / "naval-arch.yaml").write_text(NAVAL_ARCH_YAML)

    return catalog_dir


# ---------------------------------------------------------------------------
# Test catalog parsing for each source format
# ---------------------------------------------------------------------------


class TestCatalogParsing:
    """Test that each catalog format is correctly parsed."""

    def test_parse_online_resources_catalog(self, tmpdir_with_catalogs):
        mod = load_module()
        path = tmpdir_with_catalogs / "catalog.yaml"
        entries = mod.parse_online_resources_catalog(path)
        assert len(entries) == 2
        assert entries[0]["url"] == "https://standards.dnv.com/explorer/"
        assert entries[0]["name"] == "DNV Standards Explorer"
        assert entries[0]["source_catalog"] == str(path)

    def test_parse_engineering_catalog(self, tmpdir_with_catalogs):
        mod = load_module()
        path = tmpdir_with_catalogs / "engineering-catalog.yaml"
        entries = mod.parse_engineering_catalog(path)
        # 2 libraries x 2 URLs each (primary + project_url) = 4
        assert len(entries) == 4
        urls = {e["url"] for e in entries}
        assert "https://github.com/capytaine/capytaine" in urls
        assert "https://capytaine.github.io/stable/" in urls

    def test_parse_public_og_sources(self, tmpdir_with_catalogs):
        mod = load_module()
        path = tmpdir_with_catalogs / "public-og.yaml"
        entries = mod.parse_public_og_sources(path)
        # Should get entries from known_not_ingested and newly_discovered (have URLs)
        assert len(entries) >= 2
        urls = {e["url"] for e in entries}
        assert "https://www.data.boem.gov/" in urls

    def test_parse_web_resources(self, tmpdir_with_catalogs):
        mod = load_module()
        path = tmpdir_with_catalogs / "orcaflex-web.yaml"
        entries = mod.parse_web_resources(path)
        assert len(entries) == 2
        assert entries[0]["url"] == "https://www.orcina.com/webhelp/OrcaFlex/"

    def test_parse_naval_architecture(self, tmpdir_with_catalogs):
        mod = load_module()
        path = tmpdir_with_catalogs / "naval-arch.yaml"
        entries = mod.parse_naval_architecture(path)
        # textbooks(1) + online_portals(1) + classification_portals(1) + pending_manual(1)
        assert len(entries) >= 3
        urls = {e["url"] for e in entries}
        assert "https://navalifpe.wordpress.com/pna-vol1.pdf" in urls


# ---------------------------------------------------------------------------
# Test deduplication logic
# ---------------------------------------------------------------------------


class TestDeduplication:
    """Test URL-based deduplication."""

    def test_dedup_removes_exact_duplicates(self):
        mod = load_module()
        entries = [
            {"url": "https://example.com/a", "name": "Entry A", "relevance_score": 3},
            {"url": "https://example.com/a", "name": "Entry A dup", "relevance_score": 5},
            {"url": "https://example.com/b", "name": "Entry B", "relevance_score": 4},
        ]
        deduped = mod.deduplicate_by_url(entries)
        assert len(deduped) == 2
        urls = {e["url"] for e in deduped}
        assert urls == {"https://example.com/a", "https://example.com/b"}

    def test_dedup_keeps_higher_relevance(self):
        mod = load_module()
        entries = [
            {"url": "https://example.com/a", "name": "Low", "relevance_score": 2},
            {"url": "https://example.com/a", "name": "High", "relevance_score": 5},
        ]
        deduped = mod.deduplicate_by_url(entries)
        assert len(deduped) == 1
        assert deduped[0]["relevance_score"] == 5

    def test_dedup_normalizes_trailing_slash(self):
        mod = load_module()
        entries = [
            {"url": "https://example.com/a/", "name": "With slash", "relevance_score": 3},
            {"url": "https://example.com/a", "name": "Without slash", "relevance_score": 4},
        ]
        deduped = mod.deduplicate_by_url(entries)
        assert len(deduped) == 1


# ---------------------------------------------------------------------------
# Test schema normalization
# ---------------------------------------------------------------------------


class TestSchemaNormalization:
    """Test that entries are normalized to the unified schema."""

    def test_normalize_has_all_fields(self):
        mod = load_module()
        raw = {
            "url": "https://example.com",
            "name": "Test",
            "source_catalog": "test.yaml",
        }
        normalized = mod.normalize_entry(raw)
        required_fields = [
            "id", "url", "name", "type", "domain",
            "local_backup_path", "download_status",
            "last_checked", "relevance_score",
            "source_catalog", "notes",
        ]
        for field in required_fields:
            assert field in normalized, f"Missing field: {field}"

    def test_normalize_preserves_url(self):
        mod = load_module()
        raw = {"url": "https://github.com/capytaine/capytaine", "name": "Cap"}
        normalized = mod.normalize_entry(raw)
        assert normalized["url"] == "https://github.com/capytaine/capytaine"

    def test_normalize_infers_github_type(self):
        mod = load_module()
        raw = {"url": "https://github.com/capytaine/capytaine", "name": "Cap"}
        normalized = mod.normalize_entry(raw)
        assert normalized["type"] == "github_repo"

    def test_normalize_infers_paper_type(self):
        mod = load_module()
        raw = {"url": "https://arxiv.org/abs/2412.00568", "name": "Paper"}
        normalized = mod.normalize_entry(raw)
        assert normalized["type"] == "paper"

    def test_normalize_generates_id(self):
        mod = load_module()
        raw = {"url": "https://example.com/test", "name": "Test Entry"}
        normalized = mod.normalize_entry(raw)
        assert normalized["id"]
        assert isinstance(normalized["id"], str)
        assert len(normalized["id"]) > 0

    def test_normalize_default_download_status(self):
        mod = load_module()
        raw = {"url": "https://example.com", "name": "Test"}
        normalized = mod.normalize_entry(raw)
        assert normalized["download_status"] == "not_started"


# ---------------------------------------------------------------------------
# Test YAML output format
# ---------------------------------------------------------------------------


class TestYAMLOutput:
    """Test the YAML output format of the registry."""

    def test_output_has_metadata_header(self, tmp_path):
        mod = load_module()
        entries = [
            mod.normalize_entry({"url": "https://example.com/a", "name": "A"}),
            mod.normalize_entry({"url": "https://example.com/b", "name": "B"}),
        ]
        output_path = tmp_path / "registry.yaml"
        mod.write_registry(entries, output_path)
        with open(output_path) as f:
            data = yaml.safe_load(f)
        assert "generated" in data
        assert "total_entries" in data
        assert data["total_entries"] == 2
        assert "entries" in data
        assert len(data["entries"]) == 2

    def test_output_has_summary(self, tmp_path):
        mod = load_module()
        entries = [
            mod.normalize_entry({
                "url": "https://github.com/org/repo",
                "name": "Repo",
                "domain": "hydrodynamics",
            }),
        ]
        output_path = tmp_path / "registry.yaml"
        mod.write_registry(entries, output_path)
        with open(output_path) as f:
            data = yaml.safe_load(f)
        assert "summary" in data
        assert "by_type" in data["summary"]
        assert "by_domain" in data["summary"]
        assert "by_download_status" in data["summary"]

    def test_output_is_valid_yaml(self, tmp_path):
        mod = load_module()
        entries = [
            mod.normalize_entry({"url": "https://example.com", "name": "Test"}),
        ]
        output_path = tmp_path / "registry.yaml"
        mod.write_registry(entries, output_path)
        # Should not raise
        with open(output_path) as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# Test report generation
# ---------------------------------------------------------------------------


class TestReportGeneration:
    """Test the summary report output."""

    def test_generate_report_string(self):
        mod = load_module()
        entries = [
            mod.normalize_entry({
                "url": "https://github.com/org/repo",
                "name": "Repo",
                "domain": "hydrodynamics",
            }),
            mod.normalize_entry({
                "url": "https://arxiv.org/abs/1234",
                "name": "Paper",
                "domain": "structural",
            }),
        ]
        report = mod.generate_report(entries)
        assert "Total entries:" in report or "total" in report.lower()
        assert "2" in report
