---
name: crossprovider codex staleness-tracking-via-re-read-is-fragile
description: Staleness tracking via re-read is fragile
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monitoring, scheduler, contracts]
---

Checking staleness by re-reading a just-written status file misses parallel/concurrent updates to other jobs. Staleness must be tracked durably in manifest files with explicit timestamps and refresh intervals, not inferred from a single re-read of ephemeral status.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
