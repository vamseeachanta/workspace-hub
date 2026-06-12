---
name: crossprovider codex publisher-parallel-chunk-sequential-ingest-archi
description: Publisher-parallel, chunk-sequential ingest architecture
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [architecture, ingest, parallelism, conflict-avoidance]
---

Parallelize across publishers (≤3 concurrent) but run chunks sequentially within each publisher's worktree. This prevents conflicts when chunks edit shared per-domain files (index.md, log.md, _verification-queue.csv) and allows later chunks to build on earlier edits correctly. Emerged from session 2's fix to patch-apply race condition (BUG A).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
