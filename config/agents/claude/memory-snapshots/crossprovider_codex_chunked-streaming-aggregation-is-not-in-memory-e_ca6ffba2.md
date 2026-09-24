---
name: crossprovider codex chunked-streaming-aggregation-is-not-in-memory-e
description: Chunked streaming aggregation is not in-memory equivalent when rows span boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integrity, streaming, aggregation]
---

When ingesting data in chunked/streaming mode with potential duplicate rows, grouping only within each chunk can overstate counts and understate peak values if the same key-value spans chunks. Must verify chunked streaming against in-memory aggregation in tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
