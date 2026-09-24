---
name: crossprovider gemini session-locks-record-state-transitions-never-del
description: Session locks record state transitions; never delete them (audit trail)
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [work-queue, audit, concurrency]
---

Write lock files at start (status=in_progress), update on state changes (status=claimed), include pid/hostname/timestamp. Immutable logs help debug stale crashes and concurrent collisions without adding race conditions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
