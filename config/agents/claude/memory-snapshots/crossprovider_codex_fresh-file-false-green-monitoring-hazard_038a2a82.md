---
name: crossprovider codex fresh-file-false-green-monitoring-hazard
description: Fresh-file false-green monitoring hazard
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monitoring, reliability, scheduling]
---

Stale scheduled-task state can produce false-FRESH signals if newer local files mask missing heartbeat outputs (e.g., bridge run in dry-run mode produces no fresh heartbeat, yet freshness audit returns FRESH because yesterday's files exist). Requires explicit bridge-emission verification, not just file timestamp checks. Detectable via baseline test failure in audit subsystem.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
