import json
import pytest
from pathlib import Path


def test_extract_pages_returns_list(mini_pdf):
    from scripts.standards.ingest_standards import extract_pages
    chunks = extract_pages(str(mini_pdf))
    assert isinstance(chunks, list)


def test_extract_pages_has_correct_fields(mini_pdf):
    from scripts.standards.ingest_standards import extract_pages
    chunks = extract_pages(str(mini_pdf))
    assert len(chunks) >= 1
    chunk = chunks[0]
    assert "page" in chunk
    assert "text" in chunk
    assert "doc_name" in chunk
    assert chunk["doc_name"] == "mini.pdf"


def test_extract_pages_page_numbers_start_at_one(mini_pdf):
    from scripts.standards.ingest_standards import extract_pages
    chunks = extract_pages(str(mini_pdf))
    pages = [c["page"] for c in chunks]
    assert 1 in pages


def test_extract_pages_skips_empty_text(tmp_path):
    """Scanned / image PDFs yield empty text — should be skipped."""
    import fitz
    pdf_path = tmp_path / "blank.pdf"
    doc = fitz.open()
    doc.new_page()  # blank page, no text
    doc.save(str(pdf_path))
    from scripts.standards.ingest_standards import extract_pages
    chunks = extract_pages(str(pdf_path))
    assert chunks == []


def test_detect_code_family_from_path():
    from scripts.standards.ingest_standards import detect_code_family
    assert detect_code_family("DNV-RP-C203.pdf") == "DNV"
    assert detect_code_family("API_RP_2RD_3rd.pdf") == "API"
    assert detect_code_family("ABS_offshore_structures.pdf") == "ABS"
    assert detect_code_family("ISO_13628-4.pdf") == "ISO"
    assert detect_code_family("BS_EN_ISO_19902.pdf") == "BS"
    assert detect_code_family("unknown_doc.pdf") == "UNKNOWN"
