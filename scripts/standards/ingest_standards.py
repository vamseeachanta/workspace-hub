#!/usr/bin/env python3
"""
ABOUTME: Standards PDF ingestion pipeline for WRK-1132.
ABOUTME: Extracts page-level chunks from PDFs in docs/domains/ into
ABOUTME: data/standards-index/chunks.jsonl and builds a BM25 index.

Usage:
    python ingest_standards.py ingest [--source docs/domains/] [--out data/standards-index/]
    python ingest_standards.py build-index [--out data/standards-index/]
"""

import argparse
import hashlib
import json
import pickle
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Page extraction
# ---------------------------------------------------------------------------

CODE_FAMILY_PATTERNS = [
    ("DNV", r"(?<![a-z])dnv(?![a-z])"),
    ("API", r"(?<![a-z])api(?![a-z])"),
    ("ABS", r"(?<![a-z])abs(?![a-z])"),
    ("BS",  r"(?<![a-z])bs[_\-\s]"),
    ("ISO", r"(?<![a-z])iso(?![a-z])"),
    ("NORSOK", r"norsok"),
    ("ASTM", r"(?<![a-z])astm(?![a-z])"),
]


def detect_code_family(filename: str) -> str:
    """Detect code family from filename using regex patterns."""
    lower = filename.lower()
    for family, pattern in CODE_FAMILY_PATTERNS:
        if re.search(pattern, lower):
            return family
    return "UNKNOWN"


def extract_pages(pdf_path: str) -> list:
    """
    Extract page-level text chunks from a PDF using PyMuPDF.

    Args:
        pdf_path: Absolute or relative path to a PDF file.

    Returns:
        List of dicts with keys: chunk_id, doc_name, page, code_family, text, source_path.
        Pages with no extractable text are silently skipped.
    """
    try:
        import fitz
    except ImportError:
        print("ERROR: pymupdf not installed. Run: uv run --no-project --with pymupdf python", file=sys.stderr)
        return []

    path = Path(pdf_path)
    doc_name = path.name
    code_family = detect_code_family(doc_name)
    chunks = []

    try:
        doc = fitz.open(str(path))
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if not text.strip():
                continue
            chunk_id = f"{doc_name}::p{page_num}::0"
            chunks.append({
                "chunk_id": chunk_id,
                "doc_name": doc_name,
                "page": page_num,
                "code_family": code_family,
                "text": text.strip(),
                "source_path": str(path.resolve()),
            })
        doc.close()
    except Exception as exc:
        print(f"WARNING: could not extract {pdf_path}: {exc}", file=sys.stderr)

    return chunks
