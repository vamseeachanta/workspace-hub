---
name: crossprovider codex pdfplumber-not-guaranteed-in-sandbox-bootstrap-t
description: pdfplumber not guaranteed in sandbox—bootstrap to /tmp for batch table extraction
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf-tooling, sandbox-limitations, installation-workaround]
---

Ingest sandbox may lack pdfplumber; for multi-PDF table extraction (e.g., 124-page DNV standard), bootstrap `pip install pdfplumber` to /tmp/ and import from there. pdfinfo + pdftotext more reliable for metadata/text; reserve pdfplumber only for structured table CSV export.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
