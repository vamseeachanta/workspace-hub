---
name: crossprovider codex offline-fallback-patterns-for-distributed-id-gen
description: Offline fallback patterns for distributed ID generation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [distributed-work, resilience, infrastructure]
---

When generating IDs via remote tools (gh), use a local fallback pattern (WRK-LOCAL-YYYYMMDD-HHMMSS) that can promote to real IDs when connectivity returns. Allows work to proceed offline without blocking on network availability. Pair with a promotion script (promote-local-ids.sh) for batch conversion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
