---
name: crossprovider codex builder-resume-safety-idempotent-upserts-scan-st
description: Builder resume-safety: idempotent upserts + scan state, no path shortcuts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [implementation, data-integrity]
---

When building incremental indexes, use idempotent upserts with scan state checkpointing. On resume, re-walk from the start of the drive, not from the last scanned path—path-skipping shortcuts break tombstone reactivation semantics and cause data loss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
