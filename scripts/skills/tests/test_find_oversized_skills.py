#!/usr/bin/env python3
"""Tests for find-oversized-skills.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "find-oversized-skills.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _run(args: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_finds_oversized_fixture():
    """find-oversized-skills.py should list the 316-line fixture as oversized."""
    result = _run(["--root", str(FIXTURES), "--min-lines", "200"])
    assert result.returncode == 0
    assert "SKILL.md" in result.stdout


def test_respects_min_lines_threshold():
    """When min-lines is higher than fixture, nothing should be reported."""
    result = _run(["--root", str(FIXTURES), "--min-lines", "5000"])
    assert result.returncode == 0
    assert "SKILL.md" not in result.stdout


def test_output_includes_line_count():
    """Output should include the line count for each file."""
    result = _run(["--root", str(FIXTURES), "--min-lines", "100"])
    assert result.returncode == 0
    # Should contain a number (the line count)
    lines = [l for l in result.stdout.strip().splitlines() if "SKILL.md" in l]
    assert len(lines) >= 1
    # Line should contain numeric count
    assert any(c.isdigit() for c in lines[0])


def test_sorted_by_line_count_descending():
    """Results should be sorted by line count descending (largest first)."""
    result = _run(["--root", str(FIXTURES), "--min-lines", "1"])
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    counts = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        # First token should be the line count
        try:
            counts.append(int(parts[0]))
        except (ValueError, IndexError):
            continue
    assert counts == sorted(counts, reverse=True)
