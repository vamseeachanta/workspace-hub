---
name: crossprovider codex split-large-technical-reports-across-multiple-wi
description: Split large technical reports across multiple wiki subpages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest-contract, page-structure, scale-limits]
---

Standards >120 KB or with 20+ tables should be split into bounded subpages with extracted table CSVs, not committed as monolithic ~300 KB blobs (e.g., ISO 19905-2 at 306 pages, 23 tables). Use scripts/wiki/chunk_wiki_index.py or manual splitting to keep pages scannable and maintainable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
