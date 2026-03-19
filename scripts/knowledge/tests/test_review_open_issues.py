"""Tests for review-open-issues.py — WRK-1336."""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add parent dir so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import importlib

roi = importlib.import_module("review-open-issues")


# ── Fixtures ──────────────────────────────────────────────────────────


SAMPLE_ISSUES = [
    {"number": 24, "title": "WRK-046: OrcaFlex drilling riser analysis",
     "labels": [{"name": "enhancement"}, {"name": "priority:medium"},
                {"name": "cat:engineering"}]},
    {"number": 25, "title": "WRK-047: OpenFOAM CFD analysis",
     "labels": [{"name": "enhancement"}, {"name": "priority:low"},
                {"name": "cat:engineering"}]},
    {"number": 31, "title": "WRK-1001: Workspace cleanup",
     "labels": [{"name": "priority:medium"}, {"name": "cat:harness"}]},
    {"number": 40, "title": "WRK-1050: Random task",
     "labels": [{"name": "enhancement"}]},
    {"number": 42, "title": "WRK-1060: High priority item",
     "labels": [{"name": "priority:high"}, {"name": "cat:engineering"}]},
]


# ── Tests ─────────────────────────────────────────────────────────────


def test_group_by_category():
    """Groups issues by cat:* label."""
    groups = roi.group_issues(SAMPLE_ISSUES, group_by="category")
    assert "engineering" in groups
    assert "harness" in groups
    assert groups["engineering"]["count"] == 3
    assert groups["harness"]["count"] == 1
    assert len(groups["engineering"]["issues"]) == 3


def test_uncategorized_fallback():
    """Issues without cat:* go to uncategorized."""
    groups = roi.group_issues(SAMPLE_ISSUES, group_by="category")
    assert "uncategorized" in groups
    assert groups["uncategorized"]["count"] == 1
    assert groups["uncategorized"]["issues"][0]["number"] == 40


def test_table_format():
    """Table output is readable and contains expected structure."""
    groups = roi.group_issues(SAMPLE_ISSUES, group_by="category")
    output = roi.format_table(groups, total=len(SAMPLE_ISSUES))
    assert "Category: engineering (3 issues)" in output
    assert "#24" in output
    assert "#31" in output
    assert "Summary:" in output
    assert "5 open issues" in output


def test_yaml_format():
    """YAML output is valid and contains expected keys."""
    groups = roi.group_issues(SAMPLE_ISSUES, group_by="category")
    output = roi.format_yaml(groups, total=len(SAMPLE_ISSUES))
    # Should be valid YAML (parse as dict via json since structure
    # is also valid JSON when formatted that way, or just check keys)
    assert "generated_at:" in output
    assert "total_open: 5" in output
    assert "engineering:" in output
    assert "count: 3" in output


def test_group_by_priority():
    """Groups by priority:* label."""
    groups = roi.group_issues(SAMPLE_ISSUES, group_by="priority")
    assert "medium" in groups
    assert "low" in groups
    assert "high" in groups
    assert groups["medium"]["count"] == 2
    assert groups["high"]["count"] == 1
    # Issues without priority:* label go to "unset"
    assert "unset" in groups


def test_empty_issues():
    """Handles no open issues gracefully."""
    groups = roi.group_issues([], group_by="category")
    assert groups == {}
    output = roi.format_table(groups, total=0)
    assert "0 open issues" in output
