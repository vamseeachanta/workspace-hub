---
name: pdf
description: Comprehensive PDF manipulation toolkit. For batch/bulk extraction (1K+ PDFs),
  use pdftotext (poppler) via subprocess — fastest and most reliable at scale. For
  single-document understanding, OpenAI Codex PDF-to-Markdown gives best results.
  Also supports text/table extraction, PDF creation, merging/splitting, and forms.
version: 1.2.2
last_updated: 2026-01-04
category: data
related_skills:
- pdf-text-extractor
- document-rag-pipeline
- knowledge-base-builder
capabilities: []
requires: []
see_also:
- pdf-why-convert-to-markdown-first
- pdf-openai-codex-conversion
- pdf-pypdf-core-pdf-operations
- pdf-pdftotext-poppler
- pdf-why-use-pdf-large-reader
- pdf-ocr-for-scanned-documents
- pdf-execution-checklist
- pdf-common-errors
- pdf-metrics
- pdf-quick-reference
- pdf-dependencies
tags: []
---

# Pdf

## Overview

This skill enables comprehensive PDF operations through Python libraries and command-line tools. Use it for reading, creating, modifying, and analyzing PDF documents.

## Quick Start

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
for page in reader.pages:
    text = page.extract_text()
    print(text)
```

## Tool Selection (WRK-1277 + WRK-1302 Learnings)

| Scenario | Tool | Why |
|----------|------|-----|
| Batch extraction (1K+ PDFs) | **pdftotext (poppler)** via subprocess | Proven at 297K scale; reliable timeout via SIGTERM; subprocess isolation |
| Single-doc understanding | **OpenAI Codex** PDF→Markdown | Best quality; too expensive for bulk |
| Single-doc text extraction | **PyMuPDF (fitz)** | Fast, good API, in-process |
| Readability classification | **pypdfium2** | Replaces pdfplumber for page sampling; no D-state hangs; Apache-2.0 license |
| Table extraction | **pdfplumber** (single doc only) | Best table detection; DO NOT use in multiprocessing pools |
| LLM/RAG markdown | **pymupdf4llm** (monitor only) | 0.12s/doc, good markdown; **AGPL license blocks adoption** |

> **WARNING**: pdfplumber hangs in kernel D-state (disk sleep) on NTFS and NFS mounts.
> SIGALRM cannot interrupt kernel I/O. Use pdftotext via `subprocess.run(timeout=N)` for
> any batch/parallel work — the subprocess can be killed reliably on timeout.

> **WRK-1302 Finding (2026-03-17)**: pypdfium2 is NOT faster than pdftotext for batch
> extraction on ace-linux-1 (0.9-1.1x, within noise). The 0.003s/doc claim applies only
> to tiny single-page documents. However, pypdfium2 IS the right replacement for
> pdfplumber in readability classification — same accuracy, no D-state risk, Apache license.
> Benchmark: `scripts/data/doc_intelligence/benchmark_pdf_tools.py`

## When to Use

- **Batch PDF processing** - Use pdftotext (poppler) via subprocess for bulk extraction
- **Converting PDFs to Markdown** - Use OpenAI Codex for intelligent conversion (single docs)
- Extracting text and metadata from PDF files
- Merging multiple PDFs into a single document
- Splitting large PDFs into individual pages
- Adding watermarks or annotations to PDFs
- Password-protecting or decrypting PDFs
- Extracting images from PDF documents
- OCR processing for scanned documents
- Creating new PDFs with reportlab
- Extracting tables from structured PDFs

## Version History

- **1.2.2** (2026-01-04): Fixed P2 issue - added `parents=True` to all `mkdir()` calls to handle nested output paths; prevents FileNotFoundError when creating directories with non-existent parent paths
- **1.2.1** (2026-01-04): Fixed CLI tool missing imports - added complete standalone script with all required imports (openai, pypdf, logging) and function definitions; resolved P1 issue from Codex review
- **1.2.0** (2026-01-04): **MAJOR UPDATE** - Added OpenAI Codex integration for PDF-to-Markdown conversion as recommended first step for all PDF processing; includes batch conversion, chunking for large files, cost-effective options, and complete CLI tool
- **1.1.0** (2026-01-02): Added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with pypdf, pdfplumber, reportlab, CLI tools

## Sub-Skills

- [Why Convert to Markdown First?](why-convert-to-markdown-first/SKILL.md)
- [OpenAI Codex Conversion](openai-codex-conversion/SKILL.md)
- [pypdf - Core PDF Operations (+2)](pypdf-core-pdf-operations/SKILL.md)
- [pdftotext (Poppler) (+2)](pdftotext-poppler/SKILL.md)
- [Why Use PDF-Large-Reader? (+8)](why-use-pdf-large-reader/SKILL.md)
- [OCR for Scanned Documents (+3)](ocr-for-scanned-documents/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Common Errors](common-errors/SKILL.md)
- [Metrics](metrics/SKILL.md)
- [Quick Reference](quick-reference/SKILL.md)
- [Dependencies](dependencies/SKILL.md)
