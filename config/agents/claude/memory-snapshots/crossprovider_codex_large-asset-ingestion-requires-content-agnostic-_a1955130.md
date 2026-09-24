---
name: crossprovider codex large-asset-ingestion-requires-content-agnostic-
description: Large asset ingestion requires content-agnostic inventory boundary
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-ingestion, privacy-boundaries, asset-catalogs]
---

A 1.3M-row asset index with missing content_hash, extraction_status=pending, and filename-derived metadata should be treated as filesystem inventory only. Metadata fields frequently contain personal/named material; full content inspection required before bulk ingestion or corpus claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
