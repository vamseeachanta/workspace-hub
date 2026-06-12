---
name: crossprovider codex idempotent-dispatch-state-tracking-enables-resum
description: Idempotent dispatch state tracking enables resumable ingest
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [workflow, ingest, resumability, idempotency]
---

Maintain `.dispatch-state.json` tracking completed publishers and chunks. Re-running the dispatcher skips done work and enables resumable ingest after transient bwrap failures or manual retries without re-processing completed batches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
