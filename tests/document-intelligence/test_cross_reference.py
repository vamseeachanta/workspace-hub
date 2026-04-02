"""Tests for cross-reference registries tool.

Tests the cross-referencing between online-resource-registry.yaml and
the local standards-transfer-ledger, including fuzzy matching, gap
detection, and report generation.

Issue: #1613
"""

import copy
from pathlib import Path

import pytest
import yaml


def _import_cross_ref():
    """Import the cross-reference module."""
    import importlib.util
    script_path = Path(__file__).resolve().parents[2] / (
        "scripts/document-intelligence/cross-reference-registries.py"
    )
    spec = importlib.util.spec_from_file_location("cross_reference_registries", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_ONLINE = {
    "generated": "2026-04-02",
    "total_entries": 5,
    "summary": {"by_domain": {"marine": 2, "structural": 1, "general": 2}},
    "entries": [
        {
            "id": "dnv_rp_c205",
            "url": "https://rules.dnv.com/docs/pdf/DNV/RP/C205",
            "name": "DNV RP C205 Environmental Conditions and Environmental Loads",
            "type": "standard_portal",
            "domain": "marine",
            "download_status": "not_started",
            "relevance_score": 9,
            "notes": "Wave loads, wind loads",
        },
        {
            "id": "api_rp_2sk",
            "url": "https://www.api.org/rp2sk",
            "name": "API RP 2SK Design and Analysis of Stationkeeping Systems",
            "type": "standard_portal",
            "domain": "marine",
            "download_status": "downloaded",
            "relevance_score": 8,
            "notes": "Mooring design",
        },
        {
            "id": "eurocode3_fatigue",
            "url": "https://eurocodes.jrc.ec.europa.eu/EN1993-1-9",
            "name": "Eurocode 3 Part 1-9 Fatigue",
            "type": "standard_portal",
            "domain": "structural",
            "download_status": "not_started",
            "relevance_score": 5,
            "notes": "Fatigue design of steel",
        },
        {
            "id": "awesome_naval_arch",
            "url": "https://github.com/awesome-naval-arch",
            "name": "Awesome Naval Architecture Collection",
            "type": "github_repo",
            "domain": "general",
            "download_status": "not_started",
            "relevance_score": 3,
            "notes": "",
        },
        {
            "id": "python_openfoam",
            "url": "https://github.com/pyfoam",
            "name": "PyFoam OpenFOAM Python Interface",
            "type": "github_repo",
            "domain": "general",
            "download_status": "not_started",
            "relevance_score": 4,
            "notes": "",
        },
    ],
}

SAMPLE_LEDGER = {
    "generated": "2026-03-12",
    "total": 5,
    "summary": {"reference": 3, "done": 2},
    "standards": [
        {
            "id": "DNV-RP-C205",
            "title": "Environmental Conditions and Environmental Loads",
            "domain": "marine",
            "status": "reference",
            "doc_path": "/mnt/ace/standards/DNV-RP-C205.pdf",
        },
        {
            "id": "API-RP-2SK",
            "title": "Design and Analysis of Stationkeeping Systems",
            "domain": "marine",
            "status": "done",
            "doc_path": "/mnt/ace/standards/API-RP-2SK.pdf",
        },
        {
            "id": "API-5L",
            "title": "Specification for Line Pipe",
            "domain": "pipeline",
            "status": "reference",
            "doc_path": "/mnt/ace/standards/API-5L.pdf",
        },
        {
            "id": "DNV-OS-F101",
            "title": "Submarine Pipeline Systems",
            "domain": "pipeline",
            "status": "done",
            "doc_path": "",
        },
        {
            "id": "NORSOK-M501",
            "title": "Surface Preparation and Protective Coating",
            "domain": "materials",
            "status": "reference",
            "doc_path": "",
        },
    ],
}

SAMPLE_REGISTRY = {
    "generated": "2026-04-01",
    "total_docs": 100,
    "by_domain": {"marine": 50, "pipeline": 30, "structural": 10, "other": 10},
}


@pytest.fixture
def sample_online():
    return copy.deepcopy(SAMPLE_ONLINE)


@pytest.fixture
def sample_ledger():
    return copy.deepcopy(SAMPLE_LEDGER)


@pytest.fixture
def sample_registry():
    return copy.deepcopy(SAMPLE_REGISTRY)


@pytest.fixture
def data_files(tmp_path, sample_online, sample_ledger, sample_registry):
    """Write all sample data files and return their paths."""
    online_path = tmp_path / "online-resource-registry.yaml"
    ledger_path = tmp_path / "standards-transfer-ledger.yaml"
    registry_path = tmp_path / "registry.yaml"
    with open(online_path, "w") as f:
        yaml.dump(sample_online, f, default_flow_style=False)
    with open(ledger_path, "w") as f:
        yaml.dump(sample_ledger, f, default_flow_style=False)
    with open(registry_path, "w") as f:
        yaml.dump(sample_registry, f, default_flow_style=False)
    return {
        "online": str(online_path),
        "ledger": str(ledger_path),
        "registry": str(registry_path),
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMatchingAlgorithm:
    """Test title similarity and fuzzy matching."""

    def test_exact_title_match(self):
        mod = _import_cross_ref()
        score = mod.title_similarity(
            "Environmental Conditions and Environmental Loads",
            "Environmental Conditions and Environmental Loads",
        )
        assert score >= 0.95

    def test_partial_title_match(self):
        mod = _import_cross_ref()
        score = mod.title_similarity(
            "DNV RP C205 Environmental Conditions and Environmental Loads",
            "Environmental Conditions and Environmental Loads",
        )
        assert score > 0.5

    def test_unrelated_titles_low_score(self):
        mod = _import_cross_ref()
        score = mod.title_similarity(
            "PyFoam OpenFOAM Python Interface",
            "Specification for Line Pipe",
        )
        assert score < 0.45

    def test_find_matches_returns_pairs(self, sample_online, sample_ledger):
        mod = _import_cross_ref()
        matches = mod.find_matches(
            sample_online["entries"], sample_ledger["standards"],
            threshold=0.5,
        )
        # Should find DNV-RP-C205 and API-RP-2SK matches
        assert len(matches) >= 2
        matched_online_ids = {m["online_id"] for m in matches}
        assert "dnv_rp_c205" in matched_online_ids
        assert "api_rp_2sk" in matched_online_ids


class TestGapDetection:
    """Test finding online-only and local-only entries."""

    def test_online_only_entries(self, sample_online, sample_ledger):
        mod = _import_cross_ref()
        matches = mod.find_matches(
            sample_online["entries"], sample_ledger["standards"],
            threshold=0.5,
        )
        online_only = mod.find_online_only(sample_online["entries"], matches)
        online_only_ids = {e["id"] for e in online_only}
        # Eurocode, awesome_naval_arch, python_openfoam should be online-only
        assert "eurocode3_fatigue" in online_only_ids
        assert "awesome_naval_arch" in online_only_ids

    def test_local_only_entries(self, sample_online, sample_ledger):
        mod = _import_cross_ref()
        matches = mod.find_matches(
            sample_online["entries"], sample_ledger["standards"],
            threshold=0.5,
        )
        local_only = mod.find_local_only(sample_ledger["standards"], matches)
        local_only_ids = {e["id"] for e in local_only}
        # API-5L, DNV-OS-F101, NORSOK-M501 should be local-only
        assert "API-5L" in local_only_ids
        assert "NORSOK-M501" in local_only_ids


class TestReportGeneration:
    """Test markdown report generation."""

    def test_report_contains_match_count(self, data_files, tmp_path):
        mod = _import_cross_ref()
        report_path = tmp_path / "report.md"
        result = mod.run_cross_reference(
            online_path=data_files["online"],
            ledger_path=data_files["ledger"],
            registry_path=data_files["registry"],
            report_output=str(report_path),
        )
        report_text = report_path.read_text()
        assert "match" in report_text.lower()
        assert isinstance(result["match_count"], int)
        assert result["match_count"] >= 2

    def test_report_contains_domain_comparison(self, data_files, tmp_path):
        mod = _import_cross_ref()
        report_path = tmp_path / "report.md"
        mod.run_cross_reference(
            online_path=data_files["online"],
            ledger_path=data_files["ledger"],
            registry_path=data_files["registry"],
            report_output=str(report_path),
        )
        report_text = report_path.read_text()
        # Should have domain coverage section
        assert "domain" in report_text.lower()
        assert "marine" in report_text.lower()
