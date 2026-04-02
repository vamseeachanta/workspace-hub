# ABOUTME: TDD tests for test-health-dashboard.py — #1573.
# ABOUTME: Tests cover pytest output parsing, markdown report generation,
# ABOUTME: pass/fail counting, package-level aggregation, and gap detection.
"""
Tests for scripts/quality/test-health-dashboard.py

Tests cover:
  1. Pytest output line parsing (pass/fail/skip/error extraction)
  2. Package-level aggregation
  3. Pass rate calculation
  4. Markdown report generation (summary table, badges, timestamp, gap list)
  5. Gap detection (packages with zero tests)
  6. Edge cases (empty results, all failures, all passes)
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture(autouse=True)
def _add_scripts_to_path():
    """Ensure scripts.quality is importable."""
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    yield
    sys.path.pop(0)


def _import_dashboard():
    """Import the dashboard module dynamically (handles hyphenated filename)."""
    mod_path = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "quality"
        / "test-health-dashboard.py"
    )
    spec = importlib.util.spec_from_file_location("test_health_dashboard", mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# 1. parse_pytest_output — single-line summary parsing
# ---------------------------------------------------------------------------

class TestParsePytestOutput:
    """Test parsing of pytest short summary output."""

    def test_parse_typical_summary(self):
        """Parse a typical pytest summary line like '10 passed, 2 failed, 1 skipped'."""
        dashboard = _import_dashboard()
        raw = "10 passed, 2 failed, 1 skipped in 3.45s"
        result = dashboard.parse_pytest_summary(raw)
        assert result["passed"] == 10
        assert result["failed"] == 2
        assert result["skipped"] == 1
        assert result["errors"] == 0

    def test_parse_all_passed(self):
        """Parse output where all tests pass."""
        dashboard = _import_dashboard()
        raw = "25 passed in 1.20s"
        result = dashboard.parse_pytest_summary(raw)
        assert result["passed"] == 25
        assert result["failed"] == 0
        assert result["skipped"] == 0

    def test_parse_with_errors(self):
        """Parse output with errors."""
        dashboard = _import_dashboard()
        raw = "5 passed, 3 failed, 2 errors in 10.00s"
        result = dashboard.parse_pytest_summary(raw)
        assert result["passed"] == 5
        assert result["failed"] == 3
        assert result["errors"] == 2

    def test_parse_empty_output_returns_zeros(self):
        """Empty or missing summary returns all zeros."""
        dashboard = _import_dashboard()
        result = dashboard.parse_pytest_summary("")
        assert result["passed"] == 0
        assert result["failed"] == 0
        assert result["skipped"] == 0
        assert result["errors"] == 0


# ---------------------------------------------------------------------------
# 2. Package-level aggregation
# ---------------------------------------------------------------------------

class TestPackageAggregation:
    """Test per-package result aggregation from pytest output."""

    def test_aggregate_per_package(self):
        """Given multi-package pytest output, aggregate by top-level test dir."""
        dashboard = _import_dashboard()
        lines = [
            "digitalmodel/tests/reservoir/test_reservoir.py::TestPackageImport::test_import PASSED",
            "digitalmodel/tests/reservoir/test_reservoir.py::TestModuleExistence::test_init PASSED",
            "digitalmodel/tests/fatigue/test_spectral.py::test_rain PASSED",
            "digitalmodel/tests/fatigue/test_spectral.py::test_sn FAILED",
            "digitalmodel/tests/fatigue/test_spectral.py::test_skip SKIPPED",
        ]
        packages = dashboard.aggregate_by_package(lines)
        assert "reservoir" in packages
        assert "fatigue" in packages
        assert packages["reservoir"]["passed"] == 2
        assert packages["reservoir"]["failed"] == 0
        assert packages["fatigue"]["passed"] == 1
        assert packages["fatigue"]["failed"] == 1
        assert packages["fatigue"]["skipped"] == 1

    def test_aggregate_error_lines(self):
        """Parse ERROR summary lines from pytest collection failures."""
        dashboard = _import_dashboard()
        lines = [
            "ERROR digitalmodel/tests/fatigue/test_crack_growth.py",
            "ERROR digitalmodel/tests/fatigue/test_damage.py",
            "ERROR digitalmodel/tests/gis/test_coordinates.py",
        ]
        packages = dashboard.aggregate_by_package(lines)
        assert "fatigue" in packages
        assert "gis" in packages
        assert packages["fatigue"]["errors"] == 2
        assert packages["gis"]["errors"] == 1

    def test_aggregate_empty_lines(self):
        """Empty input yields empty dict."""
        dashboard = _import_dashboard()
        packages = dashboard.aggregate_by_package([])
        assert packages == {}


# ---------------------------------------------------------------------------
# 3. Pass rate calculation
# ---------------------------------------------------------------------------

class TestPassRate:
    """Test pass rate computation."""

    def test_pass_rate_normal(self):
        dashboard = _import_dashboard()
        rate = dashboard.compute_pass_rate(8, 10)
        assert rate == 80.0

    def test_pass_rate_zero_total(self):
        """Zero total tests yields 0.0 rate (no division by zero)."""
        dashboard = _import_dashboard()
        rate = dashboard.compute_pass_rate(0, 0)
        assert rate == 0.0

    def test_pass_rate_all_pass(self):
        dashboard = _import_dashboard()
        rate = dashboard.compute_pass_rate(50, 50)
        assert rate == 100.0


# ---------------------------------------------------------------------------
# 4. Markdown report generation
# ---------------------------------------------------------------------------

class TestMarkdownReport:
    """Test dashboard markdown content generation."""

    def test_report_contains_summary_table(self):
        dashboard = _import_dashboard()
        packages = {
            "reservoir": {"passed": 5, "failed": 0, "skipped": 0, "errors": 0, "total": 5},
            "fatigue": {"passed": 3, "failed": 2, "skipped": 1, "errors": 0, "total": 6},
        }
        now = datetime(2026, 4, 2, 6, 0, 0, tzinfo=timezone.utc)
        md = dashboard.generate_markdown_report(packages, now)
        # Must contain table header
        assert "Package" in md
        assert "Pass" in md
        assert "Fail" in md
        # Must contain package names
        assert "reservoir" in md
        assert "fatigue" in md

    def test_report_contains_timestamp(self):
        dashboard = _import_dashboard()
        now = datetime(2026, 4, 2, 6, 0, 0, tzinfo=timezone.utc)
        md = dashboard.generate_markdown_report({}, now)
        assert "2026-04-02" in md

    def test_report_contains_status_emoji(self):
        """Pass/fail status should use emoji badges."""
        dashboard = _import_dashboard()
        packages = {
            "reservoir": {"passed": 5, "failed": 0, "skipped": 0, "errors": 0, "total": 5},
            "fatigue": {"passed": 0, "failed": 3, "skipped": 0, "errors": 0, "total": 3},
        }
        now = datetime(2026, 4, 2, 6, 0, 0, tzinfo=timezone.utc)
        md = dashboard.generate_markdown_report(packages, now)
        # Green check for all-pass, red X for failures
        assert "\u2705" in md or ":white_check_mark:" in md
        assert "\u274c" in md or ":x:" in md


# ---------------------------------------------------------------------------
# 5. Gap detection — packages with zero tests
# ---------------------------------------------------------------------------

class TestGapDetection:
    """Test detection of source packages with no tests."""

    def test_detect_zero_test_packages(self):
        dashboard = _import_dashboard()
        source_packages = ["reservoir", "fatigue", "gis", "power"]
        tested_packages = {"reservoir": {"total": 5}, "fatigue": {"total": 3}}
        gaps = dashboard.find_test_gaps(source_packages, tested_packages)
        assert "gis" in gaps
        assert "power" in gaps
        assert "reservoir" not in gaps

    def test_no_gaps_when_all_tested(self):
        dashboard = _import_dashboard()
        source_packages = ["reservoir", "fatigue"]
        tested_packages = {
            "reservoir": {"total": 5},
            "fatigue": {"total": 3},
        }
        gaps = dashboard.find_test_gaps(source_packages, tested_packages)
        assert gaps == []


# ---------------------------------------------------------------------------
# 6. report_includes_gap_list
# ---------------------------------------------------------------------------

class TestReportGapList:
    """Test that the generated markdown includes the gap list section."""

    def test_gap_list_in_report(self):
        dashboard = _import_dashboard()
        packages = {
            "reservoir": {"passed": 2, "failed": 0, "skipped": 0, "errors": 0, "total": 2},
        }
        now = datetime(2026, 4, 2, 6, 0, 0, tzinfo=timezone.utc)
        gaps = ["gis", "power"]
        md = dashboard.generate_markdown_report(packages, now, gaps=gaps)
        assert "gis" in md
        assert "power" in md
        assert "gap" in md.lower() or "Gap" in md or "zero test" in md.lower() or "0 tests" in md.lower()
