---
name: crossprovider hermes check-for-parallel-active-workers-before-committ
description: Check for parallel active workers before committing to branch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-work, contention, git-race-condition]
---

Before claiming a branch/issue for overnight work, verify no other agents are already working it (pgrep for active sessions, check issue-creation timestamps). Parallel writes to docs/scripts can race and silently revert commits even with separate worktrees.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
