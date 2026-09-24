---
name: crossprovider codex batch-pdf-extraction-should-maintain-partial-suc
description: Batch PDF extraction should maintain partial-success inventory and queue failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pdf, ingest, pdfplumber, resilience, batch-processing]
---

pdfplumber table extraction is opportunistic; some tables fail while others succeed. Design the pipeline to capture extraction inventories (succeeded/failed) and queue failed extracts for separate processing rather than failing the entire batch. Mark partial failures for later manual or vision-based review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
