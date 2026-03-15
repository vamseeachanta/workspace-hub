# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "pytest"]
# ///
"""Tests for generate_research_brief.py — TDD first."""
import os
import sys

import pytest
import yaml

# Ensure the parent package (doc_intelligence/) is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from generate_research_brief import (
    generate_brief,
    query_capability_map,
    query_document_index,
    query_standards_ledger,
)


def test_query_document_index(tmp_path):
    index = tmp_path / "index.jsonl"
    index.write_text(
        '{"path": "doc1.pdf", "source": "og_standards", "category": "structural"}\n'
        '{"path": "doc2.pdf", "source": "ace_standards", "category": "pipeline"}\n'
        '{"path": "doc3.pdf", "source": "og_standards", "category": "structural"}\n'
    )
    results = query_document_index(str(index), "structural")
    assert len(results) == 2
    assert all(r["category"] == "structural" for r in results)


def test_query_document_index_with_subcategory(tmp_path):
    index = tmp_path / "index.jsonl"
    index.write_text(
        '{"path": "a.pdf", "source": "s1", "category": "structural", "subcategory": "fatigue"}\n'
        '{"path": "b.pdf", "source": "s1", "category": "structural", "subcategory": "buckling"}\n'
    )
    results = query_document_index(str(index), "structural", subcategory="fatigue")
    assert len(results) == 1


def test_query_document_index_empty(tmp_path):
    index = tmp_path / "index.jsonl"
    index.write_text("")
    results = query_document_index(str(index), "structural")
    assert results == []


def test_query_standards_ledger(tmp_path):
    ledger = tmp_path / "ledger.yaml"
    ledger.write_text(
        yaml.dump(
            {
                "standards": [
                    {"body": "DNV", "code": "RP-C203", "category": "structural"},
                    {"body": "API", "code": "RP 2A", "category": "structural"},
                    {"body": "DNV", "code": "ST-F101", "category": "pipeline"},
                ]
            }
        )
    )
    results = query_standards_ledger(str(ledger), "structural")
    assert len(results) == 2


def test_query_capability_map(tmp_path):
    capmap = tmp_path / "capmap.yaml"
    capmap.write_text(
        yaml.dump(
            {
                "functions": [
                    {
                        "name": "fatigue_scf",
                        "category": "structural",
                        "status": "implemented",
                    },
                    {
                        "name": "fatigue_sn_curve",
                        "category": "structural",
                        "status": "gap",
                    },
                    {
                        "name": "wall_thickness",
                        "category": "pipeline",
                        "status": "implemented",
                    },
                ]
            }
        )
    )
    result = query_capability_map(str(capmap), "structural")
    assert result["implemented"] == ["fatigue_scf"]
    assert result["gaps"] == ["fatigue_sn_curve"]


def test_generate_brief(tmp_path):
    index = tmp_path / "index.jsonl"
    index.write_text(
        '{"path": "d.pdf", "source": "og_standards", "category": "structural"}\n'
    )
    ledger = tmp_path / "ledger.yaml"
    ledger.write_text(
        yaml.dump(
            {
                "standards": [
                    {"body": "DNV", "code": "RP-C203", "category": "structural"}
                ]
            }
        )
    )
    capmap = tmp_path / "capmap.yaml"
    capmap.write_text(
        yaml.dump(
            {
                "functions": [
                    {
                        "name": "fatigue_scf",
                        "category": "structural",
                        "status": "gap",
                    }
                ]
            }
        )
    )

    brief = generate_brief(
        "structural",
        index_path=str(index),
        ledger_path=str(ledger),
        capmap_path=str(capmap),
    )
    assert brief["category"] == "structural"
    assert brief["document_coverage"]["total_documents"] == 1
    assert len(brief["relevant_standards"]) == 1
    assert "fatigue_scf" in brief["capability_status"]["gaps"]
    assert any("fatigue_scf" in a for a in brief["recommended_actions"])


def test_generate_brief_missing_optional_files(tmp_path):
    """Missing ledger/capmap should not crash — return empty results."""
    index = tmp_path / "index.jsonl"
    index.write_text(
        '{"path": "d.pdf", "source": "og_standards", "category": "structural"}\n'
    )
    brief = generate_brief(
        "structural",
        index_path=str(index),
        ledger_path=str(tmp_path / "nonexistent_ledger.yaml"),
        capmap_path=str(tmp_path / "nonexistent_capmap.yaml"),
    )
    assert brief["category"] == "structural"
    assert brief["relevant_standards"] == []
    assert brief["capability_status"]["implemented"] == []
    assert brief["capability_status"]["gaps"] == []


def test_query_document_index_limit(tmp_path):
    """Limit parameter caps the number of results returned."""
    index = tmp_path / "index.jsonl"
    lines = "\n".join(
        f'{{"path": "doc{i}.pdf", "source": "og_standards", "category": "structural"}}'
        for i in range(10)
    )
    index.write_text(lines + "\n")
    results = query_document_index(str(index), "structural", limit=3)
    assert len(results) == 3


def test_generate_brief_by_source_aggregation(tmp_path):
    """document_coverage.by_source groups correctly by source field."""
    index = tmp_path / "index.jsonl"
    index.write_text(
        '{"path": "a.pdf", "source": "og_standards", "category": "structural"}\n'
        '{"path": "b.pdf", "source": "og_standards", "category": "structural"}\n'
        '{"path": "c.pdf", "source": "ace_standards", "category": "structural"}\n'
    )
    brief = generate_brief("structural", index_path=str(index))
    by_source = brief["document_coverage"]["by_source"]
    assert by_source.get("og_standards") == 2
    assert by_source.get("ace_standards") == 1
