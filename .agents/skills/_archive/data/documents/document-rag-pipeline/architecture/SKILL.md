---
name: document-rag-pipeline-architecture
description: 'Sub-skill of document-rag-pipeline: Architecture.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Architecture

## Architecture


```
Document Folder
      │
      ▼
┌─────────────────────┐
│ 1. Build Inventory  │  SQLite catalog of all files
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 2. Extract Text     │  PyMuPDF for regular PDFs
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 3. OCR Scanned PDFs │  Tesseract + pytesseract
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 4. Chunk Text       │  1000 chars, 200 overlap
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 5. Generate Embeds  │  sentence-transformers
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 6. Semantic Search  │  Cosine similarity
└─────────────────────┘
```
