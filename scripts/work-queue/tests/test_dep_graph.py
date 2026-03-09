"""Tests for dep-graph.py — WRK dependency graph.

TDD: written before implementation.
"""
import sys
import textwrap
from pathlib import Path

import pytest

# Add scripts/work-queue to path so we can import dep_graph
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dep_graph as dg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_item(wrk_id: str, blocked_by: list[str], status: str = "pending",
              category: str = "harness") -> dg.WRKItem:
    return dg.WRKItem(
        wrk_id=wrk_id,
        title=f"Test item {wrk_id}",
        status=status,
        category=category,
        blocked_by=blocked_by,
    )


# ---------------------------------------------------------------------------
# Test 1: Empty graph
# ---------------------------------------------------------------------------

def test_empty_graph_zero_unblocked():
    result = dg.compute_graph([])
    assert result.unblocked == []
    assert result.critical_path == []
    assert result.chain_length == 0


def test_empty_graph_summary():
    result = dg.compute_graph([])
    summary = dg.format_summary(result)
    assert "0 unblocked" in summary
    assert "0 nodes" in summary


# ---------------------------------------------------------------------------
# Test 2: Single chain A → B → C
# ---------------------------------------------------------------------------

def test_single_chain_critical_path():
    items = [
        make_item("WRK-001", []),
        make_item("WRK-002", ["WRK-001"]),
        make_item("WRK-003", ["WRK-002"]),
    ]
    result = dg.compute_graph(items)
    assert result.chain_length == 3
    assert result.critical_path == ["WRK-001", "WRK-002", "WRK-003"]


def test_single_chain_unblocked():
    items = [
        make_item("WRK-001", []),
        make_item("WRK-002", ["WRK-001"]),
        make_item("WRK-003", ["WRK-002"]),
    ]
    result = dg.compute_graph(items)
    # Only WRK-001 has no blockers and is pending
    assert result.unblocked == ["WRK-001"]


# ---------------------------------------------------------------------------
# Test 3: Diamond dependency A→C, B→C
# ---------------------------------------------------------------------------

def test_diamond_dependency():
    items = [
        make_item("WRK-001", []),
        make_item("WRK-002", []),
        make_item("WRK-003", ["WRK-001", "WRK-002"]),
    ]
    result = dg.compute_graph(items)
    # WRK-001 or WRK-002 → WRK-003: longest chain = 2 nodes
    assert result.chain_length == 2
    assert "WRK-003" in result.critical_path


def test_diamond_unblocked():
    items = [
        make_item("WRK-001", []),
        make_item("WRK-002", []),
        make_item("WRK-003", ["WRK-001", "WRK-002"]),
    ]
    result = dg.compute_graph(items)
    assert set(result.unblocked) == {"WRK-001", "WRK-002"}


# ---------------------------------------------------------------------------
# Test 4: Cycle detection
# ---------------------------------------------------------------------------

def test_cycle_detection_raises():
    items = [
        make_item("WRK-001", ["WRK-002"]),
        make_item("WRK-002", ["WRK-001"]),
    ]
    with pytest.raises(dg.CycleError):
        dg.compute_graph(items)


# ---------------------------------------------------------------------------
# Test 5: Archived blocker treated as satisfied
# ---------------------------------------------------------------------------

def test_archived_blocker_is_satisfied():
    items = [
        # WRK-999 is "archived" (not in items list)
        make_item("WRK-002", ["WRK-999"]),
    ]
    archived_ids = {"WRK-999"}
    result = dg.compute_graph(items, archived_ids=archived_ids)
    # WRK-002 should be unblocked because its only blocker is archived
    assert "WRK-002" in result.unblocked


def test_non_archived_blocker_keeps_item_blocked():
    items = [
        make_item("WRK-002", ["WRK-001"]),
        # WRK-001 is NOT archived and NOT in items (dangling ref)
    ]
    archived_ids: set[str] = set()
    result = dg.compute_graph(items, archived_ids=archived_ids)
    # WRK-002 should NOT be unblocked — blocker WRK-001 is unresolved
    assert "WRK-002" not in result.unblocked


# ---------------------------------------------------------------------------
# Test 6: --category filter with cross-category opaque blocker
# ---------------------------------------------------------------------------

def test_category_filter_retains_cross_category_blocker():
    items = [
        make_item("WRK-001", [], category="engineering"),
        make_item("WRK-002", ["WRK-001"], category="harness"),
    ]
    result = dg.compute_graph(items, category_filter="harness")
    # WRK-001 is in "engineering" category — not included in filtered graph
    # WRK-002 depends on WRK-001 which is cross-category — treat as opaque blocker
    # So WRK-002 is NOT unblocked
    assert "WRK-002" not in result.unblocked


def test_category_filter_shows_local_unblocked():
    items = [
        make_item("WRK-001", [], category="harness"),
        make_item("WRK-002", ["WRK-001"], category="harness"),
        make_item("WRK-003", [], category="engineering"),
    ]
    result = dg.compute_graph(items, category_filter="harness")
    # Only WRK-001 is unblocked within harness category
    assert result.unblocked == ["WRK-001"]
    # WRK-003 is not in filtered graph
    assert "WRK-003" not in result.all_ids


# ---------------------------------------------------------------------------
# Test 7: blocked folder items excluded from unblocked even with empty blocked_by
# ---------------------------------------------------------------------------

def test_blocked_status_item_not_in_unblocked():
    items = [
        make_item("WRK-001", [], status="blocked"),
    ]
    result = dg.compute_graph(items)
    assert "WRK-001" not in result.unblocked


# ---------------------------------------------------------------------------
# Test 8: format_summary always prints even on empty
# ---------------------------------------------------------------------------

def test_format_summary_non_empty_on_empty_graph():
    result = dg.compute_graph([])
    summary = dg.format_summary(result)
    assert len(summary) > 0
    assert "unblocked" in summary


def test_format_summary_shows_chain():
    items = [
        make_item("WRK-001", []),
        make_item("WRK-002", ["WRK-001"]),
    ]
    result = dg.compute_graph(items)
    summary = dg.format_summary(result)
    assert "1 unblocked" in summary
    assert "2 nodes" in summary


# ---------------------------------------------------------------------------
# Test 9: multiline blocked_by YAML parsing
# ---------------------------------------------------------------------------

def _make_wrk_text(wrk_id: str, blocked_by_yaml: str) -> str:
    """Build a minimal WRK frontmatter string."""
    return (
        f"---\nid: {wrk_id}\ntitle: Test {wrk_id}\nstatus: pending\n"
        f"category: harness\n{blocked_by_yaml}\n---\n## Mission\nTest.\n"
    )


def test_parse_frontmatter_inline_list():
    text = _make_wrk_text("WRK-001", "blocked_by: [WRK-002, WRK-003]")
    fm = dg._parse_frontmatter(text)
    assert fm["blocked_by"] == ["WRK-002", "WRK-003"]


def test_parse_frontmatter_multiline_list():
    text = _make_wrk_text("WRK-001", "blocked_by:\n  - WRK-002\n  - WRK-003")
    fm = dg._parse_frontmatter(text)
    assert fm["blocked_by"] == ["WRK-002", "WRK-003"]


def test_parse_frontmatter_empty_inline():
    text = _make_wrk_text("WRK-001", "blocked_by: []")
    fm = dg._parse_frontmatter(text)
    assert fm["blocked_by"] == []


def test_parse_frontmatter_bare_empty():
    text = _make_wrk_text("WRK-001", "blocked_by:")
    fm = dg._parse_frontmatter(text)
    assert fm.get("blocked_by", []) == []


def test_compute_graph_multiline_blocked_by():
    """Regression: multiline blocked_by must produce dependency edges."""
    text_a = _make_wrk_text("WRK-001", "blocked_by: []")
    text_b = _make_wrk_text("WRK-002", "blocked_by:\n  - WRK-001")

    items = []
    for text in (text_a, text_b):
        fm = dg._parse_frontmatter(text)
        wrk_id = str(fm["id"])
        raw = fm.get("blocked_by", [])
        blocked_by = raw if isinstance(raw, list) else dg._parse_inline_list(str(raw))
        items.append(dg.WRKItem(
            wrk_id=wrk_id,
            title=str(fm.get("title", "")),
            status=str(fm.get("status", "pending")),
            category=str(fm.get("category", "")),
            blocked_by=blocked_by,
        ))

    result = dg.compute_graph(items)
    # WRK-002 is blocked by WRK-001 (multiline) → should NOT be unblocked
    assert "WRK-002" not in result.unblocked
    assert "WRK-001" in result.unblocked
    assert result.chain_length == 2
