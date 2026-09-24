---
name: crossprovider codex idempotent-dispatch-state-tracking-for-large-cor
description: Idempotent Dispatch State Tracking for Large Corpus
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [idempotency, resumability, dispatch-state]
---

Maintain .dispatch-state.json tracking completed publishers+chunks (JSON records: {publisher, chunk_id, committed_sha, timestamp}). Re-running the dispatcher skips already-processed work, enabling resumable ingest on large corpus (~27K docs). Retry logic cleans up failed chunk state back to the last successful commit so the next run can retry from a known point.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
