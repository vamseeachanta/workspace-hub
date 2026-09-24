---
name: crossprovider codex metadata-fields-bypass-filename-sanitization
description: Metadata fields bypass filename sanitization
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pii-leakage, sanitization-gaps, pdf-metadata]
---

Source name hashing protects source_name_digest but leaves pdfinfo_title, document metadata, and description fields unprotected, allowing purchaser names and watermark strings to leak despite sanitization. Apply parallel sanitization to all extracted metadata fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
