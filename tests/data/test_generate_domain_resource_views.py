"""
ABOUTME: Tests for scripts/data/generate-domain-resource-views.py
Tests reading from multiple YAML sources, domain filtering, markdown generation,
and gap analysis.
"""

import importlib.util
from pathlib import Path

import pytest
import yaml

HUB_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = HUB_ROOT / "scripts" / "data" / "generate-domain-resource-views.py"


def load_module():
    """Load the generator script as a module."""
    spec = importlib.util.spec_from_file_location("gen_views", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures — minimal YAML data for each source
# ---------------------------------------------------------------------------

SAMPLE_REGISTRY = {
    "generated": "2026-04-02T00:00:00",
    "total_entries": 5,
    "summary": {"by_type": {}, "by_domain": {}, "by_download_status": {}},
    "entries": [
        {
            "id": "entry1", "url": "https://github.com/capytaine/capytaine",
            "name": "Capytaine", "type": "github_repo", "domain": "hydrodynamics",
            "local_backup_path": "", "download_status": "not_started",
            "last_checked": "2026-04-01", "relevance_score": 5,
            "source_catalog": "test", "notes": "BEM solver",
        },
        {
            "id": "entry2", "url": "https://standards.dnv.com/explorer/",
            "name": "DNV Standards", "type": "standard_portal", "domain": "structural",
            "local_backup_path": "", "download_status": "not_started",
            "last_checked": "2026-04-01", "relevance_score": 5,
            "source_catalog": "test", "notes": "DNV rules",
        },
        {
            "id": "entry3", "url": "https://www.orcina.com/webhelp/",
            "name": "OrcaFlex Docs", "type": "tutorial", "domain": "orcaflex",
            "local_backup_path": "", "download_status": "reference_only",
            "last_checked": "2026-04-01", "relevance_score": 4,
            "source_catalog": "test", "notes": "Official docs",
        },
        {
            "id": "entry4", "url": "https://github.com/OpenSees/OpenSees",
            "name": "OpenSees", "type": "github_repo", "domain": "structural",
            "local_backup_path": "", "download_status": "not_started",
            "last_checked": "2026-04-01", "relevance_score": 4,
            "source_catalog": "test", "notes": "FEA framework",
        },
        {
            "id": "entry5", "url": "https://arxiv.org/abs/1234",
            "name": "Wave paper", "type": "paper", "domain": "hydrodynamics",
            "local_backup_path": "", "download_status": "downloaded",
            "last_checked": "2026-04-01", "relevance_score": 3,
            "source_catalog": "test", "notes": "Wave mechanics paper",
        },
    ],
}

SAMPLE_LEDGER = {
    "generated": "2026-03-12",
    "total": 5,
    "standards": [
        {"id": "DNV-OS-F101", "title": "Submarine Pipeline Systems", "org": "DNV",
         "domain": "pipeline", "status": "gap", "doc_path": ""},
        {"id": "API-RP-2A", "title": "Planning, Designing and Constructing Fixed Offshore Platforms",
         "org": "API", "domain": "structural", "status": "done", "doc_path": "/mnt/ace/..."},
        {"id": "DNV-RP-C205", "title": "Environmental Conditions and Environmental Loads",
         "org": "DNV", "domain": "hydrodynamics", "status": "reference", "doc_path": ""},
        {"id": "ISO-19901-7", "title": "Stationkeeping systems for floating structures",
         "org": "ISO", "domain": "marine", "status": "gap", "doc_path": ""},
        {"id": "DNV-RP-C203", "title": "Fatigue Design of Offshore Steel Structures",
         "org": "DNV", "domain": "fatigue", "status": "gap", "doc_path": ""},
    ],
}

SAMPLE_DOC_REGISTRY = {
    "generated": "2026-04-01",
    "total_docs": 100000,
    "by_domain": {
        "marine": 28345,
        "structural": 5000,
        "hydrodynamics": 1500,
        "pipeline": 18800,
        "cad": 27500,
        "orcaflex": 0,
        "fatigue": 0,
    },
}


@pytest.fixture
def data_dir(tmp_path):
    """Create temp directory with all YAML data files."""
    d = tmp_path / "data"
    d.mkdir()

    (d / "online-resource-registry.yaml").write_text(
        yaml.dump(SAMPLE_REGISTRY, default_flow_style=False)
    )
    (d / "standards-transfer-ledger.yaml").write_text(
        yaml.dump(SAMPLE_LEDGER, default_flow_style=False)
    )
    (d / "registry.yaml").write_text(
        yaml.dump(SAMPLE_DOC_REGISTRY, default_flow_style=False)
    )

    return d


@pytest.fixture
def output_dir(tmp_path):
    """Create output directory for generated views."""
    d = tmp_path / "docs" / "resources"
    d.mkdir(parents=True)
    return d


# ---------------------------------------------------------------------------
# Test domain filtering
# ---------------------------------------------------------------------------


class TestDomainFiltering:
    """Test that entries are correctly filtered by domain."""

    def test_filter_entries_by_domain(self, data_dir):
        mod = load_module()
        entries = SAMPLE_REGISTRY["entries"]
        filtered = mod.filter_by_domain(entries, "hydrodynamics")
        assert len(filtered) == 2
        assert all(e["domain"] == "hydrodynamics" for e in filtered)

    def test_filter_entries_empty_domain(self, data_dir):
        mod = load_module()
        entries = SAMPLE_REGISTRY["entries"]
        filtered = mod.filter_by_domain(entries, "geotechnical")
        assert len(filtered) == 0

    def test_filter_standards_by_domain(self, data_dir):
        mod = load_module()
        standards = SAMPLE_LEDGER["standards"]
        filtered = mod.filter_by_domain(standards, "structural")
        assert len(filtered) == 1
        assert filtered[0]["id"] == "API-RP-2A"


# ---------------------------------------------------------------------------
# Test markdown generation
# ---------------------------------------------------------------------------


class TestMarkdownGeneration:
    """Test that domain view markdown is correctly generated."""

    def test_generates_markdown_string(self, data_dir, output_dir):
        mod = load_module()
        md = mod.generate_domain_view(
            domain="hydrodynamics",
            resource_entries=SAMPLE_REGISTRY["entries"],
            standards=SAMPLE_LEDGER["standards"],
            doc_counts=SAMPLE_DOC_REGISTRY["by_domain"],
        )
        assert isinstance(md, str)
        assert len(md) > 0

    def test_markdown_has_sections(self, data_dir, output_dir):
        mod = load_module()
        md = mod.generate_domain_view(
            domain="hydrodynamics",
            resource_entries=SAMPLE_REGISTRY["entries"],
            standards=SAMPLE_LEDGER["standards"],
            doc_counts=SAMPLE_DOC_REGISTRY["by_domain"],
        )
        assert "# hydrodynamics" in md.lower() or "# Hydrodynamics" in md
        assert "Online Resources" in md
        assert "Standards" in md
        assert "Gap Analysis" in md

    def test_markdown_includes_github_repos(self, data_dir, output_dir):
        mod = load_module()
        md = mod.generate_domain_view(
            domain="hydrodynamics",
            resource_entries=SAMPLE_REGISTRY["entries"],
            standards=SAMPLE_LEDGER["standards"],
            doc_counts=SAMPLE_DOC_REGISTRY["by_domain"],
        )
        assert "GitHub Repositories" in md
        assert "Capytaine" in md

    def test_markdown_gap_analysis_lists_undownloaded(self, data_dir, output_dir):
        mod = load_module()
        md = mod.generate_domain_view(
            domain="hydrodynamics",
            resource_entries=SAMPLE_REGISTRY["entries"],
            standards=SAMPLE_LEDGER["standards"],
            doc_counts=SAMPLE_DOC_REGISTRY["by_domain"],
        )
        assert "not_started" in md or "Not Downloaded" in md or "Capytaine" in md


# ---------------------------------------------------------------------------
# Test file writing
# ---------------------------------------------------------------------------


class TestFileWriting:
    """Test that domain view files are written correctly."""

    def test_writes_markdown_file(self, data_dir, output_dir):
        mod = load_module()
        md = mod.generate_domain_view(
            domain="structural",
            resource_entries=SAMPLE_REGISTRY["entries"],
            standards=SAMPLE_LEDGER["standards"],
            doc_counts=SAMPLE_DOC_REGISTRY["by_domain"],
        )
        out_path = output_dir / "structural-resources.md"
        out_path.write_text(md)
        assert out_path.exists()
        content = out_path.read_text()
        assert "structural" in content.lower()

    def test_multiple_domains_generate(self, data_dir, output_dir):
        mod = load_module()
        domains = ["hydrodynamics", "structural", "orcaflex"]
        for domain in domains:
            md = mod.generate_domain_view(
                domain=domain,
                resource_entries=SAMPLE_REGISTRY["entries"],
                standards=SAMPLE_LEDGER["standards"],
                doc_counts=SAMPLE_DOC_REGISTRY["by_domain"],
            )
            assert len(md) > 50  # Non-trivial content


# ---------------------------------------------------------------------------
# Test gap analysis
# ---------------------------------------------------------------------------


class TestGapAnalysis:
    """Test that gap analysis correctly identifies missing resources."""

    def test_gap_finds_undownloaded(self, data_dir):
        mod = load_module()
        gaps = mod.compute_gaps(
            domain="hydrodynamics",
            resource_entries=SAMPLE_REGISTRY["entries"],
            standards=SAMPLE_LEDGER["standards"],
        )
        assert "undownloaded_resources" in gaps
        assert len(gaps["undownloaded_resources"]) >= 1

    def test_gap_finds_standard_gaps(self, data_dir):
        mod = load_module()
        gaps = mod.compute_gaps(
            domain="fatigue",
            resource_entries=SAMPLE_REGISTRY["entries"],
            standards=SAMPLE_LEDGER["standards"],
        )
        assert "standard_gaps" in gaps
        assert len(gaps["standard_gaps"]) >= 1  # DNV-RP-C203 is a gap
