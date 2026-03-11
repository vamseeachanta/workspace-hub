import json
import subprocess
import sys
import time
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def e2e_index(tmp_path_factory):
    """Build a real BM25 index from a generated multi-page PDF."""
    import fitz
    from scripts.standards.ingest_standards import ingest_directory, build_index

    tmp = tmp_path_factory.mktemp("e2e")
    src = tmp / "docs"
    src.mkdir()
    idx = tmp / "index"

    # Create realistic test PDF
    doc = fitz.open()
    pages = [
        "Cathodic protection system design per DNV-RP-B401 section 5. Impressed current ICCP.",
        "API RP 2RD riser wall thickness pressure containment design factor.",
        "S-N fatigue curves DNV-RP-C203 offshore structural steel details.",
    ]
    for text in pages:
        p = doc.new_page()
        p.insert_text((50, 72), text)
    doc.save(str(src / "DNV-test-standard.pdf"))

    ingest_directory(str(src), str(idx))
    build_index(str(idx))
    return idx


def test_e2e_query_returns_results(e2e_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("cathodic protection", str(e2e_index))
    assert len(results) >= 1


def test_e2e_query_with_code_filter(e2e_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("design", str(e2e_index), code_family="DNV")
    assert all(r["code_family"] == "DNV" for r in results)


def test_e2e_query_returns_page_citations(e2e_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("fatigue curves", str(e2e_index))
    assert results[0]["page"] >= 1
    assert results[0]["doc_name"].endswith(".pdf")


def test_e2e_speed(e2e_index):
    """Query must complete in under 5 seconds."""
    from scripts.standards.ingest_standards import query_standards
    start = time.time()
    query_standards("wall thickness pressure", str(e2e_index))
    elapsed = time.time() - start
    assert elapsed < 5.0, f"Query took {elapsed:.2f}s — must be < 5s"
