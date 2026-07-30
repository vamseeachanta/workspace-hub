---
name: crossprovider codex licensed-run-queue-retry-rc-75-signals-contentio
description: Licensed run queue retry: rc 75 signals contention, delete result.json
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [dispatch, queue-retry, licensed-runs, operational-pattern]
---

Return code 75 = serialized queue-seat contention. Retry by deleting only the result JSON file, leaving input/config intact. Frozen heartbeat on remote Windows host is documented running signature, not hung state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
