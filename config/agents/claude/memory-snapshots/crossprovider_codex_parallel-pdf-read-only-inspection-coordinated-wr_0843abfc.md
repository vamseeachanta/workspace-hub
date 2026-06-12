---
name: crossprovider codex parallel-pdf-read-only-inspection-coordinated-wr
description: Parallel PDF read-only inspection + coordinated writes
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [parallel-work, standards-ingest]
---

Dispatch read-only explorers over disjoint PDF subsets for metadata/text extraction; main session coordinates all writes and runs verification gates before completion. Avoids git-lock contention and scales to large batches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
