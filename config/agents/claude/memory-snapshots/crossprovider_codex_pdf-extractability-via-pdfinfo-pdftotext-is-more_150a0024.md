---
name: crossprovider codex pdf-extractability-via-pdfinfo-pdftotext-is-more
description: PDF extractability via pdfinfo/pdftotext is more reliable than file headers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pdf-tooling, extractability-classification, encryption-handling]
---

Encrypted PDFs often yield extractable text; ICC warnings and xref corruption are not hard failures. Use pdfinfo + pdftotext for actual extractability classification before skip/metadata-only decisions; these signals are more reliable than defensive file-header reading.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
