---
name: crossprovider codex pdf-dedupe-detection-via-text-metrics
description: PDF dedupe detection via text metrics
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pdf-ingest, deduplication, content-analysis]
---

When two PDFs have identical extractable text sample, same page count, and same character count but different SHA256 hashes, they are likely duplicate variants of the same standard (e.g., short filename vs. long filename version). Prefer one canonical ingest and note the duplicate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
