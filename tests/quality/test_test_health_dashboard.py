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
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

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
        now = datetime(2026, 4, 2, 6, 0, 0, tzinfo=UTC)
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
        now = datetime(2026, 4, 2, 6, 0, 0, tzinfo=UTC)
        md = dashboard.generate_markdown_report({}, now)
        assert "2026-04-02" in md

    def test_report_contains_status_emoji(self):
        """Pass/fail status should use emoji badges."""
        dashboard = _import_dashboard()
        packages = {
            "reservoir": {"passed": 5, "failed": 0, "skipped": 0, "errors": 0, "total": 5},
            "fatigue": {"passed": 0, "failed": 3, "skipped": 0, "errors": 0, "total": 3},
        }
        now = datetime(2026, 4, 2, 6, 0, 0, tzinfo=UTC)
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
        now = datetime(2026, 4, 2, 6, 0, 0, tzinfo=UTC)
        gaps = ["gis", "power"]
        md = dashboard.generate_markdown_report(packages, now, gaps=gaps)
        assert "gis" in md
        assert "power" in md
        assert "gap" in md.lower() or "Gap" in md or "zero test" in md.lower() or "0 tests" in md.lower()


@pytest.mark.parametrize("word", ["error", "errors"])
def test_parse_singular_and_plural_errors(word):
    """A literal summary containing one error must record exactly one error."""
    dashboard = _import_dashboard()
    assert dashboard.parse_pytest_summary(f"1 {word} in 0.1s")["errors"] == 1


@pytest.mark.parametrize("returncode", [1, 2, 3, 4, 5])
def test_unsummarized_failed_process_is_visible(tmp_path, returncode):
    """A failed process with no summary contributes one diagnostic error."""
    dashboard = _import_dashboard()
    (tmp_path / "digitalmodel/tests/example").mkdir(parents=True)
    process = MagicMock(returncode=returncode, stdout="", stderr="cannot start")
    with patch.object(dashboard.subprocess, "run", return_value=process):
        packages = dashboard.run_pytest_per_package(tmp_path)
    assert packages["example"]["errors"] == 1
    assert packages["example"]["total"] == 1


def test_runner_preserves_reported_failure_without_extra_error(tmp_path):
    """Two passes plus one failure gives three outcomes, not four."""
    dashboard = _import_dashboard()
    (tmp_path / "digitalmodel/tests/example").mkdir(parents=True)
    process = MagicMock(returncode=1, stdout="2 passed, 1 failed", stderr="")
    with patch.object(dashboard.subprocess, "run", return_value=process):
        packages = dashboard.run_pytest_per_package(tmp_path)
    assert packages["example"]["total"] == 3
    assert packages["example"]["errors"] == 0


def test_skipped_only_package_is_not_green():
    """Two skipped tests provide no passing-test evidence."""
    dashboard = _import_dashboard()
    packages = {"example": {"passed": 0, "failed": 0, "skipped": 2, "errors": 0, "total": 2}}
    report = dashboard.generate_markdown_report(packages, datetime.now(UTC))
    assert "| ⚠️ | example |" in report


def test_history_append_preserves_existing_record(tmp_path):
    """Hand calculation: 3 passes / (3 passes + 1 failure) * 100 = 75.0%."""
    dashboard = _import_dashboard()
    history_path = tmp_path / "history.json"
    packages = {"example": {"passed": 3, "failed": 1, "skipped": 0, "errors": 0, "total": 4}}
    now = datetime(2026, 10, 22, tzinfo=UTC)
    first = dashboard.append_history(history_path, packages, now)
    assert first == [{"timestamp": "2026-10-22T00:00:00+00:00", "total": 4,
                          "passed": 3, "failed": 1, "skipped": 0, "errors": 0, "pass_rate": 75.0}]
    second = dashboard.append_history(history_path, {}, now)
    assert second == [first[0], {"timestamp": first[0]["timestamp"], "total": 0,
                                   "passed": 0, "failed": 0, "skipped": 0, "errors": 0, "pass_rate": 0.0}]
    import json
    assert json.loads(history_path.read_text(encoding="utf-8")) == second


@pytest.mark.parametrize("payload", ["not json", "{}", '[{"passed": -1}]'])
def test_invalid_history_is_preserved(tmp_path, payload):
    """Invalid persisted evidence must remain unchanged for diagnosis."""
    dashboard = _import_dashboard()
    path = tmp_path / "history.json"
    path.write_text(payload, encoding="utf-8", newline="\n")
    with pytest.raises((ValueError, TypeError)):
        dashboard.append_history(path, {}, datetime.now(UTC))
    assert path.read_text(encoding="utf-8") == payload


@pytest.mark.parametrize("current,warning", [(75, False), (74, True), (85, False)])
def test_trend_threshold(current, warning):
    """Issue 1666 criterion 4: 80-75=5 does not warn; 80-74=6 warns."""
    dashboard = _import_dashboard()
    records = [{"timestamp": "earlier", "pass_rate": 80.0},
               {"timestamp": "current", "pass_rate": float(current)}]
    report = dashboard.generate_markdown_report(
        {}, datetime.now(UTC), history=records)
    assert ("WARNING" in report) == warning
    if warning:
        assert "6.0 percentage points" in report


@pytest.mark.parametrize("current,warning", [(34, False), (33, False), (32, True)])
def test_decimal_trend_threshold(tmp_path, current, warning):
    """100*(83-34)/1000=4.9; (83-33)/10=5.0; (83-32)/10=5.1 points."""
    dashboard = _import_dashboard()
    path = tmp_path / "history.json"
    for passed in (83, current):
        packages = {"example": {"passed": passed, "failed": 1000 - passed,
                                 "skipped": 0, "errors": 0, "total": 1000}}
        records = dashboard.append_history(path, packages, datetime.now(UTC))
    report = dashboard.generate_markdown_report({}, datetime.now(UTC), history=records)
    assert ("WARNING" in report) == warning
    if warning:
        assert "5.1 percentage points" in report


def test_all_exact_five_point_drops_do_not_warn():
    """For 1000 outcomes, 50 fewer passes gives exactly 100*50/1000=5 points."""
    dashboard = _import_dashboard()
    for previous_passes in range(50, 1001):
        records = [
            {"timestamp": "earlier", "pass_rate": previous_passes / 10},
            {"timestamp": "current", "pass_rate": (previous_passes - 50) / 10},
        ]
        report = dashboard.generate_markdown_report({}, datetime.now(UTC), history=records)
        assert "WARNING" not in report, previous_passes


def test_trend_contains_only_latest_eight_records():
    """Issue 1666 criterion 3: nine records minus the oldest leaves eight."""
    dashboard = _import_dashboard()
    records = [{"timestamp": f"run-{i}", "pass_rate": 100.0} for i in range(9)]
    report = dashboard.generate_markdown_report(
        {}, datetime.now(UTC), history=records)
    assert "run-0" not in report
    assert all(f"run-{i}" in report for i in range(1, 9))


def test_missing_test_tree_is_not_success(tmp_path):
    """An unavailable test tree cannot supply a successful test run."""
    dashboard = _import_dashboard()
    with pytest.raises(FileNotFoundError):
        dashboard.run_pytest_per_package(tmp_path)


@pytest.mark.parametrize("field,value", [
    ("total", 5), ("passed", -1), ("skipped", True),
    ("pass_rate", float("nan")), ("pass_rate", 74.0),
    ("timestamp", "2026-10-22"), ("timestamp", None),
])
def test_history_rejects_inconsistent_records(tmp_path, field, value):
    """The independent 3/4=75.0% record rejects each corrupt field."""
    import json

    dashboard = _import_dashboard()
    record = {"timestamp": "2026-10-22T00:00:00+00:00", "total": 4,
              "passed": 3, "failed": 1, "errors": 0, "skipped": 0, "pass_rate": 75.0}
    record[field] = value
    path = tmp_path / "history.json"
    original = json.dumps([record])
    path.write_text(original, encoding="utf-8", newline="\n")
    with pytest.raises((ValueError, TypeError)):
        dashboard.append_history(path, {}, datetime.now(UTC))
    assert path.read_text(encoding="utf-8") == original


def test_history_failed_replace_preserves_previous_bytes(tmp_path):
    """Atomic replacement failure must not truncate earlier observations."""
    dashboard = _import_dashboard()
    path = tmp_path / "history.json"
    dashboard.append_history(path, {}, datetime.now(UTC))
    original = path.read_bytes()
    with (
        patch.object(dashboard.os, "replace", side_effect=OSError("write denied")),
        pytest.raises(OSError, match="write denied"),
    ):
        dashboard.append_history(path, {}, datetime.now(UTC))
    assert path.read_bytes() == original


@pytest.mark.parametrize("exception", [TimeoutError, OSError])
def test_runner_launch_failure_is_visible(tmp_path, exception):
    """One package that cannot launch supplies one diagnostic error."""
    dashboard = _import_dashboard()
    (tmp_path / "digitalmodel/tests/example").mkdir(parents=True)
    with patch.object(dashboard.subprocess, "run", side_effect=exception("unavailable")):
        packages = dashboard.run_pytest_per_package(tmp_path)
    assert packages["example"]["errors"] == 1


def test_runner_timeout_is_visible(tmp_path):
    """A package timeout supplies one diagnostic error."""
    dashboard = _import_dashboard()
    (tmp_path / "digitalmodel/tests/example").mkdir(parents=True)
    error = dashboard.subprocess.TimeoutExpired("pytest", timeout=1)
    with patch.object(dashboard.subprocess, "run", side_effect=error):
        packages = dashboard.run_pytest_per_package(tmp_path)
    assert packages["example"]["errors"] == 1


def test_main_persists_history_and_renders_trend(tmp_path, capsys):
    """Two complete mocked runs: 4/4=100.0%, then 3/4=75.0%, drop 25.0 points."""
    import json

    dashboard = _import_dashboard()
    dashboard.__file__ = str(tmp_path / "scripts/quality/test-health-dashboard.py")
    first = {"example": {"passed": 4, "failed": 0, "skipped": 0, "errors": 0, "total": 4}}
    second = {"example": {"passed": 3, "failed": 1, "skipped": 0, "errors": 0, "total": 4}}
    with patch.object(dashboard, "run_pytest_per_package", side_effect=[first, second]):
        dashboard.main()
        dashboard.main()
    directory = tmp_path / "docs/dashboards"
    history = json.loads((directory / "test-health-history.json").read_text(encoding="utf-8"))
    assert [record["pass_rate"] for record in history] == [100.0, 75.0]
    assert "25.0 percentage points" in (directory / "test-health-dashboard.md").read_text(encoding="utf-8")
    assert "docs/dashboards/test-health-dashboard.md" in capsys.readouterr().out
    for path in directory.iterdir():
        assert b"\r" not in path.read_bytes()


def test_empty_history_has_no_regression_warning():
    """No previous observation means no comparison can be established."""
    dashboard = _import_dashboard()
    assert "WARNING" not in dashboard.generate_markdown_report(
        {}, datetime.now(UTC), history=[])


def test_empty_source_inventory_does_not_claim_coverage():
    """An empty inventory proves no package coverage claim."""
    dashboard = _import_dashboard()
    report = dashboard.generate_markdown_report({}, datetime.now(UTC), gaps=[])
    assert "All source packages have tests" not in report
    assert "supplied package inventory" in report


def test_report_labels_diagnostic_counts_as_outcomes():
    """One launch failure is one outcome; no collected test is established."""
    dashboard = _import_dashboard()
    packages = {"example": {"passed": 0, "failed": 0, "skipped": 0, "errors": 1, "total": 1}}
    report = dashboard.generate_markdown_report(packages, datetime.now(UTC))
    assert "Total outcomes | 1" in report
    assert "diagnostic execution errors" in report
