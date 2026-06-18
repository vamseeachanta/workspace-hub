---
name: crossprovider codex read-only-git-audit-under-parallel-work-git-opti
description: Read-only git audit under parallel work: GIT_OPTIONAL_LOCKS=0 + caveat labels
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [git, audit, read-only, parallel-work, methodology]
---

Use `GIT_OPTIONAL_LOCKS=0` to avoid taking optional index locks during status probes. Do not fetch (would update remote-tracking refs). Report point-in-time git state with caveat timestamp marking concurrent external activity (push hooks, fetch loops, running tests). Preserves user work during parallel sessions; prevents stale metadata interpretation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
