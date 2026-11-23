# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Tests for deduplicate_manifests.py — TDD, written before implementation."""

import sys
from pathlib import Path

import pytest

# Allow import from scripts/data/doc_intelligence when run from workspace root
sys.path.insert(0, str(Path(__file__).parents[3]))

from scripts.data.doc_intelligence.deduplicate_manifests import (
    compute_section_hash,
    compute_table_hash,
    deduplicate_sections,
    deduplicate_tables,
    merge_manifests,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SECTION_A = {
    "heading": "Intro",
    "level": 1,
    "text": "Hello world",
    "source": {"document": "a.pdf", "page": 1},
}

SECTION_B = {
    "heading": "Background",
    "level": 2,
    "text": "Some background text here.",
    "source": {"document": "a.pdf", "page": 2},
}

TABLE_A = {
    "title": "Results",
    "columns": ["col1", "col2"],
    "rows": [["v1", "v2"], ["v3", "v4"]],
    "source": {"document": "a.pdf", "page": 3},
}

TABLE_B = {
    "title": "Summary",
    "columns": ["x", "y", "z"],
    "rows": [["1", "2", "3"]],
    "source": {"document": "b.pdf", "page": 1},
}

MANIFEST_TEMPLATE = {
    "version": "1.0.0",
    "tool": "test",
    "domain": "test",
    "extraction_stats": {},
    "errors": [],
}


def make_manifest(filename: str, sections=None, tables=None, figure_refs=None):
    import copy

    m = copy.deepcopy(MANIFEST_TEMPLATE)
    m["metadata"] = {"filename": filename, "format": "pdf", "size_bytes": 100}
    m["sections"] = sections or []
    m["tables"] = tables or []
    m["figure_refs"] = figure_refs or []
    return m


# ---------------------------------------------------------------------------
# compute_section_hash
# ---------------------------------------------------------------------------


def test_compute_section_hash_deterministic():
    section = {"heading": "Intro", "level": 1, "text": "Hello world"}
    h1 = compute_section_hash(section)
    h2 = compute_section_hash(section)
    assert h1 == h2
    assert len(h1) == 16


def test_compute_section_hash_returns_str():
    h = compute_section_hash({"heading": "H", "level": 1, "text": "T"})
    assert isinstance(h, str)


def test_compute_section_hash_differs_on_different_content():
    h1 = compute_section_hash({"heading": "A", "level": 1, "text": "foo"})
    h2 = compute_section_hash({"heading": "B", "level": 1, "text": "foo"})
    assert h1 != h2


def test_compute_section_hash_differs_on_different_text():
    h1 = compute_section_hash({"heading": "A", "level": 1, "text": "foo"})
    h2 = compute_section_hash({"heading": "A", "level": 1, "text": "bar"})
    assert h1 != h2


def test_compute_section_hash_none_heading():
    # heading=None should not crash
    h = compute_section_hash({"heading": None, "level": 0, "text": "body text"})
    assert isinstance(h, str)
    assert len(h) == 16


# ---------------------------------------------------------------------------
# compute_table_hash
# ---------------------------------------------------------------------------


def test_compute_table_hash_deterministic():
    h1 = compute_table_hash(TABLE_A)
    h2 = compute_table_hash(TABLE_A)
    assert h1 == h2
    assert len(h1) == 16


def test_compute_table_hash_returns_str():
    h = compute_table_hash(TABLE_A)
    assert isinstance(h, str)


def test_compute_table_hash_differs_on_different_columns():
    t1 = {"title": "T", "columns": ["a", "b"], "rows": []}
    t2 = {"title": "T", "columns": ["a", "c"], "rows": []}
    assert compute_table_hash(t1) != compute_table_hash(t2)


def test_compute_table_hash_differs_on_different_rows():
    t1 = {"title": "T", "columns": ["a"], "rows": [["x"]]}
    t2 = {"title": "T", "columns": ["a"], "rows": [["y"]]}
    assert compute_table_hash(t1) != compute_table_hash(t2)


# ---------------------------------------------------------------------------
# deduplicate_sections
# ---------------------------------------------------------------------------


def test_deduplicate_sections_removes_exact_dupes():
    sections = [
        {"heading": "A", "level": 1, "text": "content", "source": {"document": "a.pdf", "page": 1}},
        {"heading": "A", "level": 1, "text": "content", "source": {"document": "a.pdf", "page": 1}},
        {"heading": "B", "level": 1, "text": "different", "source": {"document": "a.pdf", "page": 2}},
    ]
    result = deduplicate_sections(sections)
    assert len(result) == 2


def test_deduplicate_sections_keeps_first_occurrence():
    s1 = {"heading": "A", "level": 1, "text": "content", "source": {"document": "first.pdf"}}
    s2 = {"heading": "A", "level": 1, "text": "content", "source": {"document": "second.pdf"}}
    result = deduplicate_sections([s1, s2])
    assert len(result) == 1
    assert result[0]["source"]["document"] == "first.pdf"


def test_deduplicate_sections_empty():
    assert deduplicate_sections([]) == []


def test_deduplicate_sections_no_dupes():
    sections = [SECTION_A, SECTION_B]
    result = deduplicate_sections(sections)
    assert len(result) == 2


def test_deduplicate_sections_all_dupes():
    sections = [SECTION_A, SECTION_A, SECTION_A]
    result = deduplicate_sections(sections)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# deduplicate_tables
# ---------------------------------------------------------------------------


def test_deduplicate_tables_removes_exact_dupes():
    tables = [TABLE_A, TABLE_A, TABLE_B]
    result = deduplicate_tables(tables)
    assert len(result) == 2


def test_deduplicate_tables_keeps_first_occurrence():
    t1 = {"title": "T", "columns": ["a"], "rows": [["x"]], "source": {"document": "first.pdf"}}
    t2 = {"title": "T", "columns": ["a"], "rows": [["x"]], "source": {"document": "second.pdf"}}
    result = deduplicate_tables([t1, t2])
    assert len(result) == 1
    assert result[0]["source"]["document"] == "first.pdf"


def test_deduplicate_tables_empty():
    assert deduplicate_tables([]) == []


def test_deduplicate_tables_no_dupes():
    result = deduplicate_tables([TABLE_A, TABLE_B])
    assert len(result) == 2


# ---------------------------------------------------------------------------
# merge_manifests
# ---------------------------------------------------------------------------


def test_merge_manifests_combines_sections():
    m1 = make_manifest(
        "a.pdf",
        sections=[{"heading": "A", "level": 1, "text": "first", "source": {"document": "a.pdf"}}],
    )
    m2 = make_manifest(
        "b.pdf",
        sections=[{"heading": "B", "level": 1, "text": "second", "source": {"document": "b.pdf"}}],
    )
    merged = merge_manifests([m1, m2])
    assert len(merged["sections"]) == 2
    assert merged["metadata"]["source_count"] == 2


def test_merge_manifests_deduplicates_sections():
    section = {"heading": "A", "level": 1, "text": "shared", "source": {"document": "a.pdf"}}
    m1 = make_manifest("a.pdf", sections=[section])
    m2 = make_manifest("b.pdf", sections=[section])
    merged = merge_manifests([m1, m2])
    assert len(merged["sections"]) == 1


def test_merge_manifests_combines_tables():
    m1 = make_manifest("a.pdf", tables=[TABLE_A])
    m2 = make_manifest("b.pdf", tables=[TABLE_B])
    merged = merge_manifests([m1, m2])
    assert len(merged["tables"]) == 2


def test_merge_manifests_deduplicates_tables():
    m1 = make_manifest("a.pdf", tables=[TABLE_A])
    m2 = make_manifest("b.pdf", tables=[TABLE_A])
    merged = merge_manifests([m1, m2])
    assert len(merged["tables"]) == 1


def test_merge_manifests_combines_figure_refs():
    fig1 = {"caption": "Fig 1", "figure_id": "f1", "source": {"document": "a.pdf"}}
    fig2 = {"caption": "Fig 2", "figure_id": "f2", "source": {"document": "b.pdf"}}
    m1 = make_manifest("a.pdf", figure_refs=[fig1])
    m2 = make_manifest("b.pdf", figure_refs=[fig2])
    merged = merge_manifests([m1, m2])
    assert len(merged["figure_refs"]) == 2


def test_merge_manifests_deduplicates_figure_refs():
    fig = {"caption": "Fig 1", "figure_id": "f1", "source": {"document": "a.pdf"}}
    m1 = make_manifest("a.pdf", figure_refs=[fig])
    m2 = make_manifest("b.pdf", figure_refs=[fig])
    merged = merge_manifests([m1, m2])
    assert len(merged["figure_refs"]) == 1


def test_merge_manifests_empty_input():
    merged = merge_manifests([])
    assert merged["sections"] == []
    assert merged["tables"] == []
    assert merged["figure_refs"] == []
    assert merged["metadata"]["source_count"] == 0


def test_merge_manifests_single_manifest():
    m = make_manifest(
        "a.pdf",
        sections=[SECTION_A],
        tables=[TABLE_A],
    )
    merged = merge_manifests([m])
    assert len(merged["sections"]) == 1
    assert len(merged["tables"]) == 1
    assert merged["metadata"]["source_count"] == 1


def test_merge_manifests_source_count_field():
    manifests = [make_manifest(f"{i}.pdf") for i in range(5)]
    merged = merge_manifests(manifests)
    assert merged["metadata"]["source_count"] == 5


def test_merge_manifests_preserves_version_and_domain():
    m1 = make_manifest("a.pdf")
    m1["version"] = "2.0.0"
    m1["domain"] = "engineering"
    merged = merge_manifests([m1])
    assert merged["version"] == "2.0.0"
    assert merged["domain"] == "engineering"
