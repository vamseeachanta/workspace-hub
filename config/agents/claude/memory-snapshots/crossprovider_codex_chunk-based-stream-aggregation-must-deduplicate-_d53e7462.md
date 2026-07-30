---
name: crossprovider codex chunk-based-stream-aggregation-must-deduplicate-
description: Chunk-based stream aggregation must deduplicate across boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [streaming, aggregation, chunked-io, correctness]
---

Aggregating by chunks then combining incremental results can miss duplicates when the same lease/month spans chunk boundaries. Implement cross-chunk dedup via cache or sort-merge, not per-chunk incremental aggregation. Verify with tests that split data across chunk sizes produces identical results to in-memory aggregation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
