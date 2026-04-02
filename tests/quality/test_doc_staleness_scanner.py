"""TDD tests for doc-staleness-scanner.py — #1568.

Tests cover:
  1. Date extraction from git log output
  2. Frontmatter date extraction
  3. Classification logic (current/stale/critical)
  4. JSON report format
  5. Mock file dates
  6. CLI invocation
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

# We'll import from the script once it exists.  The test file is written first (TDD).
import importlib, sys, types


@pytest.fixture(autouse=True)
def _add_scripts_to_path():
    """Ensure scripts.quality is importable."""
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    yield
    sys.path.pop(0)


def _import_scanner():
    """Import the scanner module dynamically (handles hyphenated filename)."""
    mod_path = Path(__file__).resolve().parents[2] / "scripts" / "quality" / "doc-staleness-scanner.py"
    spec = importlib.util.spec_from_file_location("doc_staleness_scanner", mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# 1. extract_git_date
# ---------------------------------------------------------------------------

class TestExtractGitDate:
    """Test date extraction from git log output."""

    def test_valid_iso_date(self, tmp_path):
        """Given a file in a git repo, extract_git_date returns a datetime."""
        scanner = _import_scanner()
        # Create a mini git repo
        subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, check=True, capture_output=True)
        md = tmp_path / "doc.md"
        md.write_text("# Hello\n")
        subprocess.run(["git", "add", "doc.md"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init", "--no-gpg-sign"], cwd=tmp_path, check=True, capture_output=True)

        dt = scanner.extract_git_date(md, repo_root=tmp_path)

        assert isinstance(dt, datetime)
        # Should be today (within a minute)
        assert (datetime.now(timezone.utc) - dt).total_seconds() < 120

    def test_untracked_file_returns_none(self, tmp_path):
        """A file not in git returns None."""
        scanner = _import_scanner()
        subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
        md = tmp_path / "untracked.md"
        md.write_text("# Not committed\n")

        dt = scanner.extract_git_date(md, repo_root=tmp_path)

        assert dt is None


# ---------------------------------------------------------------------------
# 2. extract_frontmatter_date
# ---------------------------------------------------------------------------

class TestExtractFrontmatterDate:
    """Test frontmatter date/version extraction."""

    def test_yaml_frontmatter_date_field(self, tmp_path):
        scanner = _import_scanner()
        md = tmp_path / "doc.md"
        md.write_text("---\ntitle: Test\ndate: 2025-06-15\n---\n# Content\n")

        dt = scanner.extract_frontmatter_date(md)

        assert isinstance(dt, datetime)
        assert dt.year == 2025
        assert dt.month == 6
        assert dt.day == 15

    def test_yaml_frontmatter_version_with_date(self, tmp_path):
        scanner = _import_scanner()
        md = tmp_path / "doc.md"
        md.write_text("---\nversion: v2.1.0\nversion_date: 2025-10-20\n---\n# Hi\n")

        dt = scanner.extract_frontmatter_date(md)

        assert isinstance(dt, datetime)
        assert dt.year == 2025
        assert dt.month == 10

    def test_no_frontmatter_returns_none(self, tmp_path):
        scanner = _import_scanner()
        md = tmp_path / "doc.md"
        md.write_text("# Just markdown\nNo frontmatter here.\n")

        dt = scanner.extract_frontmatter_date(md)

        assert dt is None


# ---------------------------------------------------------------------------
# 3. classify_staleness
# ---------------------------------------------------------------------------

class TestClassifyStaleness:
    """Test the current / stale / critical classification."""

    def test_current_within_90_days(self):
        scanner = _import_scanner()
        now = datetime.now(timezone.utc)
        recent = now - timedelta(days=30)
        assert scanner.classify_staleness(recent, now) == "current"

    def test_stale_90_to_180_days(self):
        scanner = _import_scanner()
        now = datetime.now(timezone.utc)
        old = now - timedelta(days=120)
        assert scanner.classify_staleness(old, now) == "stale"

    def test_critical_over_180_days(self):
        scanner = _import_scanner()
        now = datetime.now(timezone.utc)
        ancient = now - timedelta(days=200)
        assert scanner.classify_staleness(ancient, now) == "critical"

    def test_boundary_exactly_90_days_is_stale(self):
        scanner = _import_scanner()
        now = datetime.now(timezone.utc)
        boundary = now - timedelta(days=90)
        assert scanner.classify_staleness(boundary, now) == "stale"

    def test_boundary_exactly_180_days_is_critical(self):
        scanner = _import_scanner()
        now = datetime.now(timezone.utc)
        boundary = now - timedelta(days=180)
        assert scanner.classify_staleness(boundary, now) == "critical"


# ---------------------------------------------------------------------------
# 4. JSON output format
# ---------------------------------------------------------------------------

class TestJsonOutput:
    """Test the JSON report structure."""

    def test_build_report_structure(self):
        scanner = _import_scanner()
        now = datetime.now(timezone.utc)

        entries = [
            {
                "path": "docs/README.md",
                "last_modified": (now - timedelta(days=10)).isoformat(),
                "classification": "current",
                "age_days": 10,
                "source": "git",
            },
            {
                "path": "docs/OLD.md",
                "last_modified": (now - timedelta(days=200)).isoformat(),
                "classification": "critical",
                "age_days": 200,
                "source": "git",
            },
        ]

        report = scanner.build_report(entries, now)

        assert "generated_at" in report
        assert "summary" in report
        assert "files" in report
        assert report["summary"]["total"] == 2
        assert report["summary"]["current"] == 1
        assert report["summary"]["critical"] == 1

    def test_report_serializes_to_json(self):
        scanner = _import_scanner()
        now = datetime.now(timezone.utc)
        entries = []
        report = scanner.build_report(entries, now)

        # Must be JSON-serializable
        json_str = json.dumps(report)
        parsed = json.loads(json_str)
        assert parsed["summary"]["total"] == 0


# ---------------------------------------------------------------------------
# 5. Mock file dates / scan_directory
# ---------------------------------------------------------------------------

class TestScanDirectory:
    """Test scanning a directory for .md files with mock dates."""

    def test_scan_finds_md_files(self, tmp_path):
        scanner = _import_scanner()
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "a.md").write_text("# A\n")
        (docs / "b.md").write_text("# B\n")
        (docs / "c.txt").write_text("Not markdown\n")

        md_files = scanner.find_md_files([docs])

        paths = [str(p) for p in md_files]
        assert len(md_files) == 2
        assert any("a.md" in p for p in paths)
        assert any("b.md" in p for p in paths)
        # .txt should NOT be included
        assert not any("c.txt" in p for p in paths)

    def test_scan_recurses_subdirectories(self, tmp_path):
        scanner = _import_scanner()
        docs = tmp_path / "docs"
        sub = docs / "sub"
        sub.mkdir(parents=True)
        (docs / "top.md").write_text("# Top\n")
        (sub / "nested.md").write_text("# Nested\n")

        md_files = scanner.find_md_files([docs])
        assert len(md_files) == 2


# ---------------------------------------------------------------------------
# 6. format_dashboard
# ---------------------------------------------------------------------------

class TestFormatDashboard:
    """Test the ASCII table dashboard output."""

    def test_dashboard_contains_header_and_rows(self):
        scanner = _import_scanner()
        entries = [
            {
                "path": "docs/README.md",
                "last_modified": "2026-03-01T00:00:00+00:00",
                "classification": "current",
                "age_days": 31,
                "source": "git",
            },
            {
                "path": "docs/OLD.md",
                "last_modified": "2025-06-01T00:00:00+00:00",
                "classification": "critical",
                "age_days": 305,
                "source": "git",
            },
        ]

        dashboard = scanner.format_dashboard(entries)

        assert "README.md" in dashboard
        assert "OLD.md" in dashboard
        assert "current" in dashboard.lower() or "CURRENT" in dashboard
        assert "critical" in dashboard.lower() or "CRITICAL" in dashboard

    def test_dashboard_sorted_by_age_descending(self):
        scanner = _import_scanner()
        entries = [
            {"path": "docs/NEW.md", "last_modified": "2026-03-30", "classification": "current", "age_days": 2, "source": "git"},
            {"path": "docs/OLD.md", "last_modified": "2025-01-01", "classification": "critical", "age_days": 456, "source": "git"},
            {"path": "docs/MID.md", "last_modified": "2025-12-01", "classification": "stale", "age_days": 121, "source": "git"},
        ]

        dashboard = scanner.format_dashboard(entries)
        lines = dashboard.strip().split("\n")
        # OLD.md should appear before MID.md, and MID.md before NEW.md
        old_idx = next(i for i, l in enumerate(lines) if "OLD.md" in l)
        mid_idx = next(i for i, l in enumerate(lines) if "MID.md" in l)
        new_idx = next(i for i, l in enumerate(lines) if "NEW.md" in l)
        assert old_idx < mid_idx < new_idx
