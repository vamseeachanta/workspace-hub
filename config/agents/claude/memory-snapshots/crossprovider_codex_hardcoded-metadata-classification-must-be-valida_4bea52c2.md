---
name: crossprovider codex hardcoded-metadata-classification-must-be-valida
description: Hardcoded metadata classification must be validated against actual content
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest, classification, validation, metadata]
---

Catalog-level disposition labels (metadata-only, full-fidelity) should be cross-checked against extracted content (pdfinfo encryption flags, pdftotext word count, control-char density) before trusting the label. Encryption-copy-permitted PDFs are extractable even if catalog says otherwise.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
