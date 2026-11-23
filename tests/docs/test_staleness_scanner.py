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

import os
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
        md_file.write_text("# Recent doc\n", encoding="utf-8", newline="\n")

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
        md_file.write_text("# Old doc\n", encoding="utf-8", newline="\n")

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
        md_file.write_text("# Moderate doc\n", encoding="utf-8", newline="\n")

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
        md_file.write_text("# Untracked\nUpdated: 2026-03-01\n", encoding="utf-8", newline="\n")

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


@pytest.fixture
def mixed_documents(tmp_path: Path) -> Path:
    """Synthetic local files; no live registries are read."""
    nested = tmp_path / "nested"
    nested.mkdir()
    for relative in (
        "z.md", "a.yaml", "nested/b.yml", "nested/a.md",
        "notes.txt", "config.json", "archive.yaml.bak", "UPPER.YAML",
    ):
        (tmp_path / relative).write_text("fixture\n", encoding="utf-8", newline="\n")
    (tmp_path / "directory.yaml").mkdir()
    return tmp_path


def test_scan_yaml_is_opt_in(mixed_documents: Path):
    """Default discovery retains just the original Markdown file set."""
    expected_markdown = [
        (mixed_documents / "nested/a.md").as_posix(),
        (mixed_documents / "z.md").as_posix(),
    ]
    assert staleness_scanner.scan_directory(str(mixed_documents)) == expected_markdown
    assert staleness_scanner.scan_directory(
        str(mixed_documents), extensions=(".md",)
    ) == expected_markdown
    assert staleness_scanner.scan_directory(
        str(mixed_documents), extensions=(".yaml", ".yml")
    ) == [(mixed_documents / "a.yaml").as_posix(), (mixed_documents / "nested/b.yml").as_posix()]


@pytest.mark.parametrize("suffix", [".md", ".yaml", ".yml"])
def test_scan_filters_case_insensitive_glob_results(tmp_path: Path, monkeypatch, suffix):
    """Exact suffix selection also holds when globbing ignores case."""
    lower = tmp_path / f"lower{suffix}"
    upper = tmp_path / f"upper{suffix.upper()}"
    directory = tmp_path / f"directory{suffix}"
    lower.touch()
    upper.touch()
    directory.mkdir()
    monkeypatch.setattr(Path, "rglob", lambda self, pattern: iter((upper, directory, lower)))

    assert staleness_scanner.scan_directory(
        str(tmp_path), extensions=(suffix,)
    ) == [lower.as_posix()]


def test_scan_mixed_extensions_is_sorted_unique(mixed_documents: Path):
    """Repeated selectors and input order cannot duplicate or reorder files."""
    expected = [
        (mixed_documents / "a.yaml").as_posix(),
        (mixed_documents / "nested/a.md").as_posix(),
        (mixed_documents / "nested/b.yml").as_posix(),
        (mixed_documents / "z.md").as_posix(),
    ]
    for extensions in (
        (".yml", ".md", ".yaml", ".md", ".yaml"),
        [".yaml", ".yml", ".md"],
        {".md", ".yaml", ".yml"},
        iter((".yml", ".yaml", ".md")),
    ):
        assert staleness_scanner.scan_directory(
            str(mixed_documents), extensions=extensions
        ) == expected


@pytest.mark.parametrize(
    "extensions",
    [
        None, ".yaml", b".yaml", (), ("",), ("yaml",), ("*.yaml",),
        (".txt",), (".YAML",), ("../.yaml",), (".md", None),
        ([".yaml"],), (".md", ".json"),
    ],
)
def test_scan_rejects_invalid_extensions(tmp_path: Path, extensions):
    """Malformed or unsupported selections fail even for missing roots."""
    for directory in (tmp_path, tmp_path / "missing"):
        with pytest.raises(ValueError, match="extensions"):
            staleness_scanner.scan_directory(str(directory), extensions=extensions)


@pytest.mark.parametrize("extensions", [(".md",), (".yaml", ".yml"), (".md", ".yaml", ".yml")])
def test_scan_empty_or_missing_directories(tmp_path: Path, extensions):
    for directory in (tmp_path, tmp_path / "missing"):
        assert staleness_scanner.scan_directory(
            str(directory), extensions=extensions
        ) == []


def test_yaml_fixtures_use_existing_date_precedence_and_report_counts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    """Exercise discovery through reporting using the existing fixed NOW.

    Policy: scripts/docs/staleness-scanner.py::classify_staleness, cited by
    GH #1568 and TestFreshnessThresholds above: FRESH <30, MODERATE 30-89,
    STALE >=90 days. Independent boundary examples: 29, 30 and 90 days.
    Hand count below: one git-fresh, two content-moderate, two filesystem-stale.
    """
    # Conflicting evidence makes each precedence decision observable.
    # NOW - 29 days = March 4; NOW - 30 = March 3; NOW - 90 = January 2.
    fixtures = [
        ("git.yaml", "Updated: 2026-01-02\n", 90,
         "2026-03-04T00:00:00+00:00", "git", 29, "FRESH"),
        ("content.yml", "Updated: 2026-03-03\n", 29,
         None, "content", 30, "MODERATE"),
        ("filesystem.yaml", "value: [deliberately unclosed\n", 90,
         None, "filesystem", 90, "STALE"),
        ("invalid-git.yml", "Updated: 2026-03-03\n", 29,
         "invalid", "content", 30, "MODERATE"),
        ("invalid-content.yaml", "Updated: 2026-02-30\n", 90,
         None, "filesystem", 90, "STALE"),
    ]
    git_dates = {}
    expected = {}
    for name, content, mtime_age, git_date, source, age, status in fixtures:
        path = tmp_path / name
        path.write_text(content, encoding="utf-8", newline="\n")
        timestamp = _make_date(mtime_age).timestamp()
        os.utime(path, (timestamp, timestamp))
        git_dates[path.as_posix()] = git_date
        expected[name] = (source, age, status)
    (tmp_path / "ignored.txt").write_text("Updated: 2026-01-02\n", encoding="utf-8", newline="\n")
    (tmp_path / "ignored.md").write_text("Updated: 2026-01-02\n", encoding="utf-8", newline="\n")
    monkeypatch.setattr(staleness_scanner, "REPO_ROOT", tmp_path)
    with patch.object(
        staleness_scanner, "get_git_last_modified",
        side_effect=lambda filepath, **kwargs: git_dates[filepath],
    ), patch.object(yaml, "safe_load", side_effect=AssertionError("YAML parsing is unnecessary")):
        files = staleness_scanner.scan_directory(
            str(tmp_path), extensions=(".yaml", ".yml")
        )
        entries = [staleness_scanner.classify_file(path, now=NOW) for path in files]
        report = staleness_scanner.build_yaml_report(entries, now=NOW)

    assert {
        entry["file"]: (entry["date_source"], entry["age_days"], entry["status"])
        for entry in report["files"]
    } == expected
    assert report["generated_at"] == NOW.isoformat()
    # Five explicit fixtures: one fresh + two moderate + two stale = five total.
    assert report["summary"] == {"total": 5, "FRESH": 1, "MODERATE": 2, "STALE": 2}
    assert [entry["file"] for entry in report["files"]] == [
        "filesystem.yaml", "invalid-content.yaml", "content.yml", "invalid-git.yml", "git.yaml",
    ]
    assert yaml.safe_load(yaml.safe_dump(report)) == report
