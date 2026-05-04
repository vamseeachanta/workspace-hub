---
name: pdf-text-extractor-dependencies
description: 'Sub-skill of pdf-text-extractor: Dependencies (+5).'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Dependencies (+5)

## Dependencies


```bash
pip install PyMuPDF
# or
uv pip install PyMuPDF
```

## Basic Extraction


```python
import fitz  # PyMuPDF

def extract_pdf_text(filepath):
    """Extract all text from a PDF file."""
    doc = fitz.open(filepath)

    pages = []
    for page_num, page in enumerate(doc, 1):
        text = page.get_text()

*See sub-skills for full details.*

## Chunked Extraction


```python
def extract_with_chunks(filepath, chunk_size=2000, overlap=200):
    """Extract text with overlapping chunks for better context."""
    doc = fitz.open(filepath)
    chunks = []

    for page_num, page in enumerate(doc, 1):
        text = page.get_text().strip()
        if not text:
            continue

*See sub-skills for full details.*

## Metadata Extraction


```python
def extract_metadata(filepath):
    """Extract PDF metadata."""
    doc = fitz.open(filepath)

    metadata = {
        'filename': Path(filepath).name,
        'filepath': str(filepath),
        'page_count': len(doc),
        'file_size': Path(filepath).stat().st_size,

*See sub-skills for full details.*

## Batch Processor


```python
import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFBatchExtractor:
    def __init__(self, db_path, chunk_size=2000):

*See sub-skills for full details.*

## CLI Script


```python
#!/usr/bin/env python3
"""PDF Text Extraction CLI."""

import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Extract text from PDFs')
    parser.add_argument('path', help='PDF file or directory')

*See sub-skills for full details.*
