---
name: crossprovider codex concurrent-worktree-state-drift-in-shared-checko
description: Concurrent worktree state drift in shared checkouts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [worktree, concurrency, state-drift, audit-hazard]
---

workspace-hub exhibits transient state changes (ahead/behind counts drift 3→4, index locks appear/disappear) during parallel /tmp/wt-* worktree work. Read-only audits in shared checkouts cannot assume stable state; process checks and clock-aware re-checks are needed for accuracy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
