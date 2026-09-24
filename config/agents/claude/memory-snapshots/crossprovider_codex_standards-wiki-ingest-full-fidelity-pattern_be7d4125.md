---
name: crossprovider codex standards-wiki-ingest-full-fidelity-pattern
description: Standards wiki ingest full-fidelity pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [wiki-ingest, data-quality, standards, pdfplumber]
---

For documentation/standards ingest: emit table CSVs only if columns provably faithful (consistent structure, no collapsed rows); otherwise use raw_layout with 'columns unverified' disclaimer. Figure inventory must be caption-only, no prose mentions, de-duplicated by ID. Source PDFs stay off-repo; cite via source_pdf frontmatter.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
