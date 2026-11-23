"""Tests for /mnt/ace undiscovered resource audit script.

All filesystem access is mocked so tests run in CI without /mnt/ace.
Covers: cross-reference logic, report generation, conference scanning,
standards coverage, engineering-refs scanning.

GH issue: #1579
"""

import json
import os
import subprocess
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest
import yaml


# ---------------------------------------------------------------------------
# We import the module under test lazily so the file can be created after
# the test file (TDD).  The conftest fixture below handles the import.
# ---------------------------------------------------------------------------

@pytest.fixture
def audit_module():
    """Import the audit module, skipping if not yet implemented."""
    import importlib
    import sys
    scripts_dir = Path(__file__).resolve().parents[2] / "scripts" / "data"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    # Force re-import to pick up changes
    mod_name = "ace_resource_audit"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    mod = importlib.import_module(mod_name)
    return mod


# ---------------------------------------------------------------------------
# Fixtures: sample data structures matching real /mnt/ace layout
# ---------------------------------------------------------------------------

SAMPLE_CATALOG_YAML = {
    "schema_version": "1.0.0",
    "domains": {
        "hydrodynamics": {
            "description": "Hydrodynamic solvers",
            "libraries": [
                {"name": "WEC-Sim", "url": "https://github.com/WEC-Sim/WEC-Sim"},
                {"name": "Capytaine", "url": "https://github.com/capytaine/capytaine"},
                {"name": "HAMS", "url": "https://github.com/YingyiLiu/HAMS"},
            ],
        },
        "marine_offshore": {
            "description": "Marine & offshore engineering",
            "libraries": [
                {"name": "OpenFAST", "url": "https://github.com/OpenFAST/openfast"},
                {"name": "MoorDyn", "url": "https://github.com/FloatingArrayDesign/MoorDyn"},
                {"name": "MoorPy", "url": "https://github.com/NREL/MoorPy"},
            ],
        },
        "cad_geometry": {
            "description": "CAD & geometry",
            "libraries": [
                {"name": "Gmsh", "url": "https://gitlab.onelab.info/gmsh/gmsh"},
            ],
        },
    },
}

SAMPLE_LEDGER = {
    "generated": "2026-03-12",
    "total": 5,
    "standards": [
        {"id": "5L", "org": "API", "title": "API Spec 5L", "status": "reference"},
        {"id": "X52", "org": "API", "title": "API 5L X52", "status": "gap"},
        {"id": "F101", "org": "DNV", "title": "DNV-OS-F101", "status": "done"},
        {"id": "A36", "org": "ASTM", "title": "ASTM A36", "status": "reference"},
        {"id": "ISO-13628", "org": "ISO", "title": "ISO 13628", "status": "gap"},
    ],
}


@pytest.fixture
def sample_catalog():
    return SAMPLE_CATALOG_YAML


@pytest.fixture
def sample_ledger():
    return SAMPLE_LEDGER


# ===========================================================================
# 1. Cross-reference: repos vs catalog
# ===========================================================================

class TestRepoCrossReference:
    """Check that repos are correctly identified as cataloged or not."""

    def test_all_repos_in_catalog_detected(self, audit_module, sample_catalog):
        """Repos present in catalog should be flagged as in_catalog=True."""
        result = audit_module.check_repos_in_catalog(
            repo_names=["WEC-Sim", "openfast", "gmsh", "capytaine", "HAMS", "MoorDyn", "MoorPy"],
            catalog=sample_catalog,
        )
        for r in result:
            assert r["in_catalog"] is True, f"{r['name']} should be in catalog"

    def test_missing_repo_detected(self, audit_module, sample_catalog):
        """Repos NOT in catalog should be flagged as in_catalog=False."""
        result = audit_module.check_repos_in_catalog(
            repo_names=["opm-common"],
            catalog=sample_catalog,
        )
        assert len(result) == 1
        assert result[0]["in_catalog"] is False
        assert result[0]["name"] == "opm-common"

    def test_domain_returned_for_cataloged_repo(self, audit_module, sample_catalog):
        """For cataloged repos, the domain should be returned."""
        result = audit_module.check_repos_in_catalog(
            repo_names=["WEC-Sim"],
            catalog=sample_catalog,
        )
        assert result[0]["domain"] == "hydrodynamics"

    def test_empty_repos_returns_empty(self, audit_module, sample_catalog):
        result = audit_module.check_repos_in_catalog(
            repo_names=[],
            catalog=sample_catalog,
        )
        assert result == []


# ===========================================================================
# 2. Conference scanning
# ===========================================================================

class TestConferenceScanning:
    """Conference directory scanning and index cross-referencing."""

    def test_conference_scan_counts_files(self, audit_module, tmp_path):
        """Each conference dir should report its file count."""
        conf_root = tmp_path / "conferences"
        conf_root.mkdir()
        (conf_root / "OTC").mkdir()
        for i in range(5):
            (conf_root / "OTC" / f"paper{i}.pdf").write_text("x")
        (conf_root / "OMAE").mkdir()
        for i in range(3):
            (conf_root / "OMAE" / f"paper{i}.pdf").write_text("x")

        result = audit_module.scan_conferences(str(conf_root))
        by_name = {r["name"]: r for r in result}
        assert by_name["OTC"]["file_count"] == 5
        assert by_name["OMAE"]["file_count"] == 3

    def test_conference_indexed_detection(self, audit_module):
        """Conferences found in index should be flagged as indexed."""
        index_lines = [
            json.dumps({"path": "/mnt/ace/docs/conferences/OTC/paper1.pdf"}),
            json.dumps({"path": "/mnt/ace/O&G-Standards/API/api-5l.pdf"}),
        ]
        conferences = [
            {"name": "OTC", "file_count": 100, "indexed": False},
            {"name": "OMAE", "file_count": 200, "indexed": False},
        ]
        result = audit_module.check_conferences_in_index(conferences, index_lines)
        by_name = {r["name"]: r for r in result}
        assert by_name["OTC"]["indexed"] is True
        assert by_name["OMAE"]["indexed"] is False


# ===========================================================================
# 3. Standards coverage
# ===========================================================================

class TestStandardsCoverage:
    """Standards directory vs transfer-ledger coverage."""

    def test_coverage_calculation(self, audit_module, sample_ledger):
        """Coverage % = ledger entries for org / files on disk."""
        disk_counts = {"API": 574, "DNV": 100, "ASTM": 25537, "ISO": 308}
        result = audit_module.calculate_standards_coverage(
            disk_counts=disk_counts,
            ledger=sample_ledger,
        )
        by_org = {r["org"]: r for r in result}
        # API has 2 entries in sample_ledger
        assert by_org["API"]["ledger_count"] == 2
        assert by_org["API"]["disk_count"] == 574
        assert 0 < by_org["API"]["coverage_pct"] < 100

    def test_zero_disk_files_no_division_error(self, audit_module, sample_ledger):
        """Org with 0 files on disk should not crash."""
        disk_counts = {"SNAME": 0}
        result = audit_module.calculate_standards_coverage(
            disk_counts=disk_counts,
            ledger=sample_ledger,
        )
        assert result[0]["coverage_pct"] == 0.0

    def test_org_not_in_ledger(self, audit_module, sample_ledger):
        """Org not in ledger should show 0 ledger entries."""
        disk_counts = {"NEMA": 4}
        result = audit_module.calculate_standards_coverage(
            disk_counts=disk_counts,
            ledger=sample_ledger,
        )
        assert result[0]["ledger_count"] == 0
        assert result[0]["coverage_pct"] == 0.0


# ===========================================================================
# 4. Engineering refs scanning
# ===========================================================================

class TestEngineeringRefs:
    """Engineering references directory scanning."""

    def test_scan_engineering_refs(self, audit_module, tmp_path):
        """Should list subdirs with file counts and top-level file count."""
        refs_root = tmp_path / "engineering-refs"
        refs_root.mkdir()
        (refs_root / "api").mkdir()
        (refs_root / "api" / "doc1.pdf").write_text("x")
        (refs_root / "dnv").mkdir()
        for i in range(4):
            (refs_root / "dnv" / f"doc{i}.pdf").write_text("x")
        # Top-level file
        (refs_root / "loose-file.pdf").write_text("x")

        result = audit_module.scan_engineering_refs(str(refs_root))
        assert result["top_level_files"] == 1
        by_name = {d["name"]: d for d in result["subdirs"]}
        assert by_name["api"]["file_count"] == 1
        assert by_name["dnv"]["file_count"] == 4


# ===========================================================================
# 5. Report generation
# ===========================================================================

class TestReportGeneration:
    """Markdown report generation."""

    def test_report_contains_summary_table(self, audit_module):
        """Generated report must contain a summary table."""
        audit_data = {
            "repos": [
                {"name": "WEC-Sim", "last_updated": "2026-01-21", "in_catalog": True, "domain": "hydrodynamics"},
                {"name": "opm-common", "last_updated": "2026-03-24", "in_catalog": False, "domain": None},
            ],
            "conferences": [
                {"name": "OTC", "file_count": 8500, "indexed": False},
            ],
            "standards": [
                {"org": "API", "disk_count": 574, "ledger_count": 2, "coverage_pct": 0.35},
            ],
            "engineering_refs": {
                "top_level_files": 31,
                "subdirs": [{"name": "api", "file_count": 3}],
            },
        }
        report = audit_module.generate_report(audit_data)
        assert "# /mnt/ace Undiscovered Resource Audit" in report
        assert "WEC-Sim" in report
        assert "opm-common" in report
        assert "OTC" in report
        assert "Top 20" in report or "Recommendations" in report

    def test_report_has_recommendations(self, audit_module):
        """Report must include recommendations section."""
        audit_data = {
            "repos": [],
            "conferences": [
                {"name": "OTC", "file_count": 8500, "indexed": False},
                {"name": "OMAE", "file_count": 13126, "indexed": False},
            ],
            "standards": [],
            "engineering_refs": {"top_level_files": 0, "subdirs": []},
        }
        report = audit_module.generate_report(audit_data)
        assert "Recommendation" in report or "recommendation" in report

    def test_report_top20_undiscovered(self, audit_module):
        """Report should list top 20 undiscovered resources by estimated value."""
        audit_data = {
            "repos": [
                {"name": "opm-common", "last_updated": "2026-03-24", "in_catalog": False, "domain": None},
            ],
            "conferences": [
                {"name": f"Conf{i}", "file_count": (30 - i) * 100, "indexed": False}
                for i in range(25)
            ],
            "standards": [
                {"org": "ASTM", "disk_count": 25537, "ledger_count": 97, "coverage_pct": 0.38},
            ],
            "engineering_refs": {"top_level_files": 31, "subdirs": []},
        }
        report = audit_module.generate_report(audit_data)
        assert "Top 20" in report or "top 20" in report
