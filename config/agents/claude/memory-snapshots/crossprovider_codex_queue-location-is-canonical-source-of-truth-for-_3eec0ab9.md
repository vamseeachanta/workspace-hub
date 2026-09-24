---
name: crossprovider codex queue-location-is-canonical-source-of-truth-for-
description: Queue location is canonical source of truth for claim state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [work-queue, state-management, gates]
---

For work-queue items, the file location in the queue directory (working/ vs pending/ vs blocked/) is the authoritative claim status, not the lock file contents. Guards must verify working/WRK-NNN.md exists, not just check that pending/ does not.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
