---
name: document-rag-pipeline
description: Build complete document knowledge bases with PDF text extraction, OCR
  for scanned documents, vector embeddings, and semantic search. Use this for creating
  searchable document libraries from folders of PDFs, technical standards, or any
  document collection.
type: reference
version: 1.1.0
last_updated: 2026-01-02
category: data
related_skills:
- semantic-search-setup
- rag-system-builder
- knowledge-base-builder
capabilities: []
requires: []
tags: []
---

# Document Rag Pipeline

## Overview

This skill creates a complete Retrieval-Augmented Generation (RAG) system from a folder of documents. It handles:
- Regular PDF text extraction
- OCR for scanned/image-based PDFs
- DRM-protected file detection
- Text chunking with overlap
- Vector embedding generation
- SQLite storage with full-text search
- Semantic similarity search

## Quick Start

```bash
# Install dependencies
pip install PyMuPDF pytesseract Pillow sentence-transformers numpy tqdm

# Build knowledge base
python build_knowledge_base.py /path/to/documents --embed

# Search documents
python build_knowledge_base.py /path/to/documents --search "your query"
```

## When to Use

- Building searchable knowledge bases from document folders
- Processing technical standards libraries (API, ISO, ASME, etc.)
- Creating semantic search over engineering documents
- OCR processing of scanned historical documents
- Any collection of PDFs needing intelligent search

## Prerequisites

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils

# macOS
brew install tesseract poppler

# Verify Tesseract
tesseract --version  # Should show 5.x
```
### Python Dependencies

```bash
pip install PyMuPDF pytesseract Pillow sentence-transformers numpy tqdm
```

Or with UV:
```bash
uv pip install PyMuPDF pytesseract Pillow sentence-transformers numpy tqdm
```

## Related Skills

- `pdf/text-extractor` - Just text extraction
- `semantic-search-setup` - Just embeddings/search
- `rag-system-builder` - Add LLM Q&A layer
- `knowledge-base-builder` - Simpler document catalog

---

## Version History

- **1.1.0** (2026-01-02): Added Quick Start, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with OCR support, chunking, vector embeddings, semantic search

## Sub-Skills

- [Build Knowledge Base (+2)](build-knowledge-base/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)

## Sub-Skills

- [Architecture](architecture/SKILL.md)
- [Step 1: Database Schema (+5)](step-1-database-schema/SKILL.md)
- [Complete Pipeline Script](complete-pipeline-script/SKILL.md)
- [Performance Metrics (Real-World)](performance-metrics-real-world/SKILL.md)
