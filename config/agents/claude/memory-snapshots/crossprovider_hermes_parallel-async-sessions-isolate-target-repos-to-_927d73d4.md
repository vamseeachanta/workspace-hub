---
name: crossprovider hermes parallel-async-sessions-isolate-target-repos-to-
description: Parallel async sessions isolate target repos to avoid git lock storms
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, git-locking, parallel-agents]
---

When Hermes spawns parallel work on shared repos (workspace-hub), explicitly isolate execution targets: #2269/#2628 target `digitalmodel` separately to avoid lock contention with C-lane or H6/H8 workspace-hub commits. Use separate git repos when parallel, not worktrees in the same repo.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
