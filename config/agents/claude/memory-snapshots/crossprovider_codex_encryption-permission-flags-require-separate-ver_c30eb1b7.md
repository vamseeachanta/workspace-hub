---
name: crossprovider codex encryption-permission-flags-require-separate-ver
description: Encryption-permission flags require separate verification — 'copy allowed' ≠ extractable
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [drm-classification, pdf-extraction, ingest-policy]
---

PDF metadata can show Encrypted:yes but copy/print:allowed, or Encrypted:no but extract:disabled. Check both flags independently. Per llm-wiki#122, Encrypted:yes → metadata-only regardless of permission bits; inspect actual extraction success with pdftotext before committing full-fidelity ingest.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
