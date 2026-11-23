"""Tests for quality-gap-report.py (WRK-1060).

TDD tests written before implementation:
  1. test_classify_covered_dir — src/ maps to ruff+mypy+pytest+bandit → "covered"
  2. test_classify_uncovered_dir — scripts/ maps to no checks → "uncovered"
  3. test_classify_partial_dir — notebooks/ in non-digitalmodel repo → "uncovered"
  4. test_all_repos_walked — scanner finds all 5 repos given REPO_MAP
  5. test_yaml_output_schema — output YAML has required keys
  6. test_gap_count_matches — total gap count matches
"""

import json
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent
SCRIPTS_QUALITY = TESTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_QUALITY))

import quality_gap_report as qgr  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Classify a covered directory
# ---------------------------------------------------------------------------


def test_classify_covered_dir():
    """src/ directory maps to at least one quality check → 'covered'."""
    checks = qgr.classify_dir("src/", repo="assetutilities")
    assert checks["coverage"] == "covered"
    assert len(checks["tools"]) >= 1


# ---------------------------------------------------------------------------
# 2. Classify an uncovered directory
# ---------------------------------------------------------------------------


def test_classify_uncovered_dir():
    """scripts/ directory has no quality checks → 'uncovered'."""
    checks = qgr.classify_dir("scripts/", repo="assetutilities")
    assert checks["coverage"] == "uncovered"
    assert checks["tools"] == []


# ---------------------------------------------------------------------------
# 3. Partial coverage for notebooks/ in non-digitalmodel repo
# ---------------------------------------------------------------------------


def test_classify_partial_dir_notebooks():
    """notebooks/ in assethold has no checks (no nbqa) → 'uncovered'."""
    checks = qgr.classify_dir("notebooks/", repo="assethold")
    assert checks["coverage"] == "uncovered"


def test_classify_partial_dir_notebooks_digitalmodel():
    """notebooks/ in digitalmodel has nbqa → 'partial' or 'covered'."""
    checks = qgr.classify_dir("notebooks/", repo="digitalmodel")
    assert checks["coverage"] in ("partial", "covered")


# ---------------------------------------------------------------------------
# 4. All 5 repos walked
# ---------------------------------------------------------------------------


def test_all_repos_walked():
    """REPO_MAP contains all 5 tier-1 repos."""
    expected = {"assetutilities", "digitalmodel", "worldenergydata", "assethold", "ogmanufacturing"}
    assert set(qgr.REPO_MAP.keys()) == expected


# ---------------------------------------------------------------------------
# 5. YAML output schema
# ---------------------------------------------------------------------------


def test_yaml_output_schema(tmp_path):
    """build_gap_report returns dict with required top-level keys."""
    # Use a minimal fake repo root with known structure
    fake_root = tmp_path
    fake_repo = fake_root / "assetutilities"
    (fake_repo / "src").mkdir(parents=True)
    (fake_repo / "scripts").mkdir(parents=True)

    report = qgr.build_gap_report({"assetutilities": "assetutilities"}, repo_root=fake_root)

    assert "schema_version" in report
    assert "generated_at" in report
    assert "repos" in report
    assert "summary" in report
    assert "assetutilities" in report["repos"]


# ---------------------------------------------------------------------------
# 6. Gap count matches
# ---------------------------------------------------------------------------


def test_classify_unknown_dir():
    """Unknown directory pattern returns coverage='unknown' with empty tools."""
    checks = qgr.classify_dir("vendor/", repo="assetutilities")
    assert checks["coverage"] == "unknown"
    assert checks["tools"] == []


def test_gap_count_matches(tmp_path):
    """summary.total_gaps == number of gap entries across all repos."""
    fake_root = tmp_path
    fake_repo = fake_root / "assetutilities"
    (fake_repo / "src").mkdir(parents=True)
    (fake_repo / "scripts").mkdir(parents=True)
    (fake_repo / "examples").mkdir(parents=True)

    report = qgr.build_gap_report({"assetutilities": "assetutilities"}, repo_root=fake_root)

    total_in_summary = report["summary"]["total_gaps"]
    counted = sum(
        len(repo_data.get("dir_gaps", {}))
        for repo_data in report["repos"].values()
    )
    assert total_in_summary == counted
