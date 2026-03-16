---
name: pdf-text-extractor
description: Extract text from PDF files with intelligent chunking and metadata preservation.
  IMPORTANT - For best results, first convert PDFs to markdown using OpenAI Codex
  (see pdf skill), then process the markdown. Also supports direct PDF text extraction
  for batch processing, technical documents, standards libraries, research papers,
  or any PDF collection.
version: 1.2.0
last_updated: 2026-01-04
category: data
related_skills:
- pdf
- knowledge-base-builder
- semantic-search-setup
- document-inventory
capabilities: []
requires: []
see_also:
- pdf-text-extractor-features
- pdf-text-extractor-dependencies
- pdf-text-extractor-readability-classification
- pdf-text-extractor-encrypted-pdfs
- pdf-text-extractor-example-usage
tags: []
---

# Pdf Text Extractor

## Overview

This skill extracts text from PDF files using PyMuPDF (fitz), with intelligent chunking, page tracking, and metadata preservation. Handles large PDF collections with batch processing and error recovery.

**RECOMMENDED WORKFLOW:** For all PDF documents, first convert to markdown using OpenAI Codex (see `pdf` skill), then process the structured markdown. This skill is best used for:
- Batch processing where Codex conversion is impractical
- Legacy workflows requiring direct PDF extraction
- Cases where raw text is sufficient

**Note:** The doc-intelligence pipeline uses pdfplumber directly, not Codex conversion.
For bulk extraction across the 420K+ corpus, use
`scripts/data/doc-intelligence/extract-document.py` instead of the Codex workflow.

## Quick Start

**Recommended Approach (with Codex conversion):**
```python
# 1. Convert PDF to markdown first (see pdf skill)
from pdf_skill import pdf_to_markdown_codex

md_path = pdf_to_markdown_codex("document.pdf")

# 2. Process the markdown
with open(md_path) as f:
    markdown = f.read()
    # Work with structured markdown
```

**Direct Extraction (when Codex not needed):**
```python
import fitz  # PyMuPDF

doc = fitz.open("document.pdf")
for page in doc:
    text = page.get_text()
    print(text)
doc.close()
```

## When to Use

- Processing PDF document collections for search indexing
- Extracting text from technical standards and specifications
- Converting PDF libraries to searchable text databases
- Preparing documents for AI/ML processing
- Building knowledge bases from PDF archives

## Related Skills

- `knowledge-base-builder` - Build searchable database from extracted text
- `semantic-search-setup` - Add vector embeddings for AI search
- `document-inventory` - Catalog documents before extraction

## Version History

- **1.2.0** (2026-01-04): Added OpenAI Codex workflow recommendation as preferred approach; updated Quick Start to show Codex-first workflow; added reference to `pdf` skill for markdown conversion
- **1.1.0** (2026-01-02): Added Quick Start, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with PyMuPDF, batch processing, OCR support, metadata extraction

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)
- [Dependencies](dependencies/SKILL.md)

## Sub-Skills

- [Features](features/SKILL.md)
- [Dependencies (+5)](dependencies/SKILL.md)
- [Readability Classification](readability-classification/SKILL.md)
- [Encrypted PDFs (+2)](encrypted-pdfs/SKILL.md)
- [Example Usage](example-usage/SKILL.md)
