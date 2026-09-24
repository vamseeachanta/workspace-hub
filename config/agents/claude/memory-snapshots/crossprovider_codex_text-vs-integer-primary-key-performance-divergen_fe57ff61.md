---
name: crossprovider codex text-vs-integer-primary-key-performance-divergen
description: TEXT vs INTEGER PRIMARY KEY performance divergence in keyset queries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sql, performance, indexing]
---

TEXT primary keys can cause 10x+ more internal row evaluations than INTEGER keys during keyset-pagination queries, while returning identical result sets (observed: 233 vs 25 visits). Choose primary key type intentionally for bounded-sample queries; type-dependent index plans affect storage-engine work invisible to result counts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
