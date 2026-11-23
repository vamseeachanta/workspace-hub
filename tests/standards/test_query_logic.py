import json
import pickle
import pytest
from pathlib import Path


@pytest.fixture
def built_index(tmp_path):
    """Fixture: pre-built index with 3 known chunks."""
    from scripts.standards.ingest_standards import build_index
    chunks = [
        {"chunk_id": "DNV::p1::0", "doc_name": "DNV-RP-C203.pdf", "page": 1,
         "code_family": "DNV", "text": "fatigue design criteria S-N curves DNV offshore structures", "source_path": "/dnv.pdf"},
        {"chunk_id": "API::p2::0", "doc_name": "API-RP-2RD.pdf", "page": 2,
         "code_family": "API", "text": "riser design wall thickness pressure containment API offshore", "source_path": "/api.pdf"},
        {"chunk_id": "ABS::p1::0", "doc_name": "ABS-offshore-structures.pdf", "page": 1,
         "code_family": "ABS", "text": "cathodic protection impressed current design ABS rules", "source_path": "/abs.pdf"},
    ]
    with open(tmp_path / "chunks.jsonl", "w") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")
    build_index(str(tmp_path))
    return tmp_path


def test_query_returns_results(built_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("fatigue S-N", str(built_index))
    assert len(results) >= 1


def test_query_ranks_best_match_first(built_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("fatigue S-N curves", str(built_index))
    assert results[0]["doc_name"] == "DNV-RP-C203.pdf"


def test_query_filters_by_code_family(built_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("design", str(built_index), code_family="API")
    assert all(r["code_family"] == "API" for r in results)


def test_query_returns_page_citation(built_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("cathodic protection", str(built_index))
    assert "page" in results[0]
    assert isinstance(results[0]["page"], int)
    assert results[0]["page"] >= 1


def test_query_no_results_returns_empty_list(built_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("xyzzy_nonexistent_term", str(built_index))
    assert isinstance(results, list)
    assert len(results) == 0
