#!/usr/bin/env python3
"""Tests for check_config_drift.py — Agent harness file drift detector (WRK-1094).

Uses tmp_path fixtures; no real filesystem access.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

# Allow importing the module under test from the parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
import check_config_drift as ccd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_file(tmp_path: Path, filename: str, lines: int, content: str | None = None) -> Path:
    """Write a file with the specified number of lines (or custom content)."""
    p = tmp_path / filename
    if content is not None:
        p.write_text(content)
    else:
        p.write_text("\n".join([f"line {i}" for i in range(lines)]) + "\n")
    return p


def _make_agents_md(tmp_path: Path, frontmatter: str | None = None) -> Path:
    """Write an AGENTS.md file with optional YAML frontmatter block."""
    p = tmp_path / "AGENTS.md"
    if frontmatter is None:
        # No YAML block at all
        p.write_text("# AGENTS\n\nsome content\n")
    else:
        p.write_text(f"---\n{frontmatter}---\n# AGENTS\n")
    return p


# ---------------------------------------------------------------------------
# Test 1: line limit — exactly 20 lines → no findings
# ---------------------------------------------------------------------------

def test_line_limit_pass(tmp_path: Path) -> None:
    path = _make_file(tmp_path, "CLAUDE.md", lines=20)
    baseline: dict = {}
    findings = ccd.check_line_limit(path, "workspace-hub", baseline)
    assert findings == []


# ---------------------------------------------------------------------------
# Test 2: 21-line file, not in baseline → FAIL (new regression)
# ---------------------------------------------------------------------------

def test_line_limit_fail_new_regression(tmp_path: Path) -> None:
    path = _make_file(tmp_path, "CLAUDE.md", lines=21)
    baseline: dict = {}
    findings = ccd.check_line_limit(path, "workspace-hub", baseline)
    assert len(findings) == 1
    f = findings[0]
    assert f.severity == "FAIL"
    assert f.rule == "line_limit"
    assert "21" in f.detail


# ---------------------------------------------------------------------------
# Test 3: 21-line file, in baseline → WARN (known debt)
# ---------------------------------------------------------------------------

def test_line_limit_warn_in_baseline(tmp_path: Path) -> None:
    path = _make_file(tmp_path, "CLAUDE.md", lines=21)
    baseline = {
        "violations": [
            {"repo": "workspace-hub", "file": "CLAUDE.md", "rule": "line_limit"}
        ]
    }
    findings = ccd.check_line_limit(path, "workspace-hub", baseline)
    assert len(findings) == 1
    f = findings[0]
    assert f.severity == "WARN"
    assert f.rule == "line_limit"


# ---------------------------------------------------------------------------
# Test 4: AGENTS.md with no YAML block → FAIL
# ---------------------------------------------------------------------------

def test_agents_frontmatter_missing(tmp_path: Path) -> None:
    _make_agents_md(tmp_path, frontmatter=None)
    findings = ccd.check_agents_frontmatter(tmp_path / "AGENTS.md", "workspace-hub")
    severities = [f.severity for f in findings]
    assert "FAIL" in severities
    rules = [f.rule for f in findings]
    assert any("frontmatter" in r for r in rules)


# ---------------------------------------------------------------------------
# Test 5: AGENTS.md with valid YAML frontmatter → no FAIL findings
# ---------------------------------------------------------------------------

def test_agents_frontmatter_valid(tmp_path: Path) -> None:
    frontmatter = (
        "purpose: Test repo\n"
        "entry_points: [src/main.py]\n"
        "test_command: uv run python -m pytest\n"
        "depends_on: []\n"
        "maturity: stable\n"
    )
    _make_agents_md(tmp_path, frontmatter=frontmatter)
    findings = ccd.check_agents_frontmatter(tmp_path / "AGENTS.md", "workspace-hub")
    fail_findings = [f for f in findings if f.severity == "FAIL"]
    assert fail_findings == []


# ---------------------------------------------------------------------------
# Test 6: CODEX.md absent → WARN (not required)
# ---------------------------------------------------------------------------

def test_missing_file_warn(tmp_path: Path) -> None:
    # CODEX.md is optional → WARN
    findings = ccd.check_missing_files(tmp_path, "workspace-hub")
    warn_files = [f.file for f in findings if f.severity == "WARN"]
    assert "CODEX.md" in warn_files
    # Should not be FAIL
    fail_files = [f.file for f in findings if f.severity == "FAIL"]
    assert "CODEX.md" not in fail_files


# ---------------------------------------------------------------------------
# Test 7: AGENTS.md absent → FAIL
# ---------------------------------------------------------------------------

def test_missing_file_fail(tmp_path: Path) -> None:
    findings = ccd.check_missing_files(tmp_path, "workspace-hub")
    fail_files = [f.file for f in findings if f.severity == "FAIL"]
    assert "AGENTS.md" in fail_files


# ---------------------------------------------------------------------------
# Test 8: generate_report writes YAML with expected keys
# ---------------------------------------------------------------------------

def test_report_format(tmp_path: Path) -> None:
    findings = [
        ccd.Finding(
            repo="workspace-hub",
            file="CLAUDE.md",
            rule="line_limit",
            severity="WARN",
            detail="31 lines (limit 20, known debt)",
        ),
        ccd.Finding(
            repo="assethold",
            file="AGENTS.md",
            rule="frontmatter_missing",
            severity="FAIL",
            detail="No YAML frontmatter block found",
        ),
    ]
    output_dir = tmp_path / "logs" / "quality"
    report_path = ccd.generate_report(findings, output_dir)

    assert report_path.exists()
    data = yaml.safe_load(report_path.read_text())

    # Required top-level keys
    assert "generated_at" in data
    assert "summary" in data
    assert "findings" in data

    # Summary counts
    assert data["summary"]["total"] == 2
    assert data["summary"]["fail"] == 1
    assert data["summary"]["warn"] == 1

    # Each finding has expected fields
    for item in data["findings"]:
        for key in ("repo", "file", "rule", "severity", "detail"):
            assert key in item, f"Missing key {key!r} in finding"

    # latest symlink / copy exists
    latest = output_dir / "config-drift-latest.yaml"
    assert latest.exists()


# ---------------------------------------------------------------------------
# Test 9: AGENTS.md has frontmatter but missing fields → WARN (not FAIL)
# ---------------------------------------------------------------------------

def test_agents_frontmatter_missing_fields_is_warn(tmp_path: Path) -> None:
    # Only 'purpose' present; rest are missing
    frontmatter = "purpose: Test repo\n"
    _make_agents_md(tmp_path, frontmatter=frontmatter)
    findings = ccd.check_agents_frontmatter(tmp_path / "AGENTS.md", "myrepo")
    assert len(findings) == 1
    f = findings[0]
    assert f.rule == "frontmatter_missing_fields"
    assert f.severity == "WARN", "Missing fields should be WARN, not FAIL"


# ---------------------------------------------------------------------------
# Test 10: run_checks emits WARN when repo directory is absent
# ---------------------------------------------------------------------------

def test_run_checks_missing_repo_emits_warn(tmp_path: Path) -> None:
    # Point REPO_MAP at a non-existent subdir
    absent_repo = tmp_path / "no-such-repo"
    # Patch REPO_MAP temporarily
    original = ccd.REPO_MAP.copy()
    ccd.REPO_MAP["phantom"] = str(absent_repo.relative_to(tmp_path))
    try:
        findings = ccd.run_checks(["phantom"], {}, tmp_path)
    finally:
        ccd.REPO_MAP.clear()
        ccd.REPO_MAP.update(original)
    assert len(findings) == 1
    f = findings[0]
    assert f.repo == "phantom"
    assert f.rule == "repo_missing"
    assert f.severity == "WARN"


# ---------------------------------------------------------------------------
# Test 11: check_missing_files treats a directory named CLAUDE.md as missing
# ---------------------------------------------------------------------------

def test_missing_file_directory_not_counted_as_present(tmp_path: Path) -> None:
    # Create a *directory* named CLAUDE.md — is_file() should return False
    (tmp_path / "CLAUDE.md").mkdir()
    (tmp_path / "AGENTS.md").mkdir()
    findings = ccd.check_missing_files(tmp_path, "workspace-hub")
    fail_files = [f.file for f in findings if f.severity == "FAIL"]
    assert "AGENTS.md" in fail_files, "Directory named AGENTS.md should not count as file"


# ---------------------------------------------------------------------------
# Test 12: check_line_limit returns WARN finding on unreadable file (OSError)
# ---------------------------------------------------------------------------

def test_line_limit_oserror_emits_warn(tmp_path: Path) -> None:
    non_existent = tmp_path / "CLAUDE.md"
    # File doesn't exist → read_text raises OSError
    findings = ccd.check_line_limit(non_existent, "workspace-hub", {})
    assert len(findings) == 1
    f = findings[0]
    assert f.rule == "file_unreadable"
    assert f.severity == "WARN"


# ---------------------------------------------------------------------------
# Test 13: check_agents_frontmatter returns WARN finding on unreadable file
# ---------------------------------------------------------------------------

def test_agents_frontmatter_oserror_emits_warn(tmp_path: Path) -> None:
    non_existent = tmp_path / "AGENTS.md"
    findings = ccd.check_agents_frontmatter(non_existent, "myrepo")
    assert len(findings) == 1
    f = findings[0]
    assert f.rule == "file_unreadable"
    assert f.severity == "WARN"
