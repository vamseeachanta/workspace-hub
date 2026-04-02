#!/usr/bin/env python3
"""Tests for the doc staleness scanner (scripts/docs/staleness-scanner.py).

Tests cover:
  - test_detects_stale_files: mock git log output, verify detection
  - test_freshness_thresholds: 30/60/90 day bucket classification
  - test_yaml_output_format: YAML report structure validation
  - test_handles_missing_files: graceful handling of absent files

Ref: GH #1568
"""
from __future__ import annotations

import sys
import textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

# ---------------------------------------------------------------------------
# Ensure the scripts/docs/ module is importable
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "docs"
sys.path.insert(0, str(SCRIPTS_DIR))

# We import the module functions after path setup
# The scanner module is named with a hyphen so we use importlib
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "staleness_scanner",
    SCRIPTS_DIR / "staleness-scanner.py",
)
staleness_scanner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(staleness_scanner)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

NOW = datetime(2026, 4, 2, 0, 0, 0, tzinfo=timezone.utc)


def _make_date(days_ago: int) -> datetime:
    """Return a UTC datetime `days_ago` days before NOW."""
    return NOW - timedelta(days=days_ago)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDetectsStaleFiles:
    """test_detects_stale_files — mock git log output, verify detection."""

    def test_fresh_file_detected_as_fresh(self, tmp_path: Path):
        """A file modified 10 days ago should be FRESH."""
        md_file = tmp_path / "recent.md"
        md_file.write_text("# Recent doc\n")

        git_date = _make_date(10)

        with patch.object(
            staleness_scanner,
            "get_git_last_modified",
            return_value=git_date.isoformat(),
        ):
            result = staleness_scanner.classify_file(str(md_file), now=NOW)
            assert result["status"] == "FRESH"
            assert result["age_days"] == 10

    def test_stale_file_detected_as_stale(self, tmp_path: Path):
        """A file modified 120 days ago should be STALE."""
        md_file = tmp_path / "old.md"
        md_file.write_text("# Old doc\n")

        git_date = _make_date(120)

        with patch.object(
            staleness_scanner,
            "get_git_last_modified",
            return_value=git_date.isoformat(),
        ):
            result = staleness_scanner.classify_file(str(md_file), now=NOW)
            assert result["status"] == "STALE"
            assert result["age_days"] == 120

    def test_moderate_file_detected_as_moderate(self, tmp_path: Path):
        """A file modified 50 days ago should be MODERATE."""
        md_file = tmp_path / "moderate.md"
        md_file.write_text("# Moderate doc\n")

        git_date = _make_date(50)

        with patch.object(
            staleness_scanner,
            "get_git_last_modified",
            return_value=git_date.isoformat(),
        ):
            result = staleness_scanner.classify_file(str(md_file), now=NOW)
            assert result["status"] == "MODERATE"
            assert result["age_days"] == 50


class TestFreshnessThresholds:
    """test_freshness_thresholds — 30/60/90 day bucket boundaries."""

    @pytest.mark.parametrize(
        "days_ago, expected_status",
        [
            (0, "FRESH"),
            (15, "FRESH"),
            (29, "FRESH"),
            (30, "MODERATE"),  # boundary: exactly 30 days
            (60, "MODERATE"),
            (89, "MODERATE"),
            (90, "STALE"),     # boundary: exactly 90 days
            (91, "STALE"),
            (365, "STALE"),
        ],
    )
    def test_threshold_boundaries(self, days_ago: int, expected_status: str):
        """Verify classification at boundary values."""
        modified = _make_date(days_ago)
        status = staleness_scanner.classify_staleness(modified, now=NOW)
        assert status == expected_status, (
            f"Expected {expected_status} for {days_ago} days ago, got {status}"
        )


class TestYamlOutputFormat:
    """test_yaml_output_format — YAML report structure validation."""

    def test_report_has_required_keys(self):
        """Report dict must have summary, generated_at, and files keys."""
        entries = [
            {
                "file": "docs/README.md",
                "status": "FRESH",
                "age_days": 5,
                "last_modified": "2026-03-28T00:00:00+00:00",
                "date_source": "git",
            },
            {
                "file": "docs/old.md",
                "status": "STALE",
                "age_days": 120,
                "last_modified": "2025-12-03T00:00:00+00:00",
                "date_source": "git",
            },
        ]
        report = staleness_scanner.build_yaml_report(entries, now=NOW)

        assert "generated_at" in report
        assert "summary" in report
        assert "files" in report

    def test_summary_counts(self):
        """Summary must contain FRESH, MODERATE, STALE counts."""
        entries = [
            {"file": "a.md", "status": "FRESH", "age_days": 5,
             "last_modified": "2026-03-28", "date_source": "git"},
            {"file": "b.md", "status": "MODERATE", "age_days": 45,
             "last_modified": "2026-02-15", "date_source": "git"},
            {"file": "c.md", "status": "STALE", "age_days": 100,
             "last_modified": "2025-12-23", "date_source": "git"},
            {"file": "d.md", "status": "STALE", "age_days": 200,
             "last_modified": "2025-09-14", "date_source": "git"},
        ]
        report = staleness_scanner.build_yaml_report(entries, now=NOW)
        summary = report["summary"]

        assert summary["total"] == 4
        assert summary["FRESH"] == 1
        assert summary["MODERATE"] == 1
        assert summary["STALE"] == 2

    def test_yaml_serializable(self):
        """Report must be serializable to valid YAML."""
        entries = [
            {"file": "a.md", "status": "FRESH", "age_days": 5,
             "last_modified": "2026-03-28", "date_source": "git"},
        ]
        report = staleness_scanner.build_yaml_report(entries, now=NOW)
        yaml_str = yaml.dump(report, default_flow_style=False)
        parsed = yaml.safe_load(yaml_str)
        assert parsed["summary"]["total"] == 1

    def test_summary_line_format(self):
        """Summary line should be: 'N FRESH, M MODERATE, P STALE'."""
        entries = [
            {"file": "a.md", "status": "FRESH", "age_days": 5,
             "last_modified": "2026-03-28", "date_source": "git"},
            {"file": "b.md", "status": "MODERATE", "age_days": 45,
             "last_modified": "2026-02-15", "date_source": "git"},
        ]
        report = staleness_scanner.build_yaml_report(entries, now=NOW)
        summary_line = staleness_scanner.format_summary_line(report["summary"])
        assert "1 FRESH" in summary_line
        assert "1 MODERATE" in summary_line
        assert "0 STALE" in summary_line


class TestHandlesMissingFiles:
    """test_handles_missing_files — graceful handling of absent files."""

    def test_missing_file_returns_none(self):
        """classify_file should return None for a non-existent file."""
        result = staleness_scanner.classify_file(
            "/nonexistent/path/missing.md", now=NOW
        )
        assert result is None

    def test_git_returns_empty_for_untracked(self, tmp_path: Path):
        """If git log returns empty, fall back to content date stamps."""
        md_file = tmp_path / "untracked.md"
        md_file.write_text("# Untracked\nUpdated: 2026-03-01\n")

        with patch.object(
            staleness_scanner,
            "get_git_last_modified",
            return_value=None,
        ):
            result = staleness_scanner.classify_file(str(md_file), now=NOW)
            # Should fall back to content date stamp or filesystem
            assert result is not None
            assert "status" in result

    def test_scan_skips_missing_directories(self, tmp_path: Path):
        """scan_directory should skip dirs that don't exist without error."""
        missing = tmp_path / "nonexistent"
        files = staleness_scanner.scan_directory(str(missing))
        assert files == []
