---
name: crossprovider codex large-batch-ingest-parallel-discovery-then-seque
description: Large batch ingest: parallel discovery, then sequential writes
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest, workflow, parallel, coordination]
---

Use parallel agents for per-PDF discovery (text extraction, classification, dedupe checks), then execute all writes sequentially in a single session to keep repo state controlled. This avoids race conditions on shared index/log/CSV files while maximizing discovery speed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
