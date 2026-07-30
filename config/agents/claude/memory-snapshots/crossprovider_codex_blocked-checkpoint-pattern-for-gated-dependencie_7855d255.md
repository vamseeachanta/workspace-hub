---
name: crossprovider codex blocked-checkpoint-pattern-for-gated-dependencie
description: Blocked-checkpoint pattern for gated dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [workflow-patterns, dependency-management, concurrent-work]
---

When a task receives approval but has open dependencies or missing proof-handoff contracts, stop implementation at Task 0 and post a blocked-checkpoint comment with the exact dependency queue to GitHub. This prevents scope creep into parallel sessions without blocking the approval gate itself.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
