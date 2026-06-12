---
name: crossprovider hermes pdf-structured-knowledge-extraction-pattern-for-
description: PDF structured knowledge extraction pattern for naval architecture resources
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [methodology, pdf-extraction, naval-architecture, reference-ingestion]
---

To ingest naval architecture PDFs (textbooks, standards) into engineering wiki: use pdfinfo for metadata, pdftotext with -layout flag for structure preservation, pdfplumber/PyMuPDF for precise page-range extraction, map printed vs PDF page numbers as locators, and fall back to tesseract-OCR for scanned documents. Critical for reference ingestion workflows like #2564 yaw-moment calculations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
