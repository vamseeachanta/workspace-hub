---
name: crossprovider hermes worktree-per-lane-isolation-eliminates-git-conte
description: Worktree-per-lane isolation eliminates git contention in multi-agent parallel execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-parallelization, worktree-pattern, contention-avoidance]
---

Validated across 6+ concurrent branches per session: clean worktree per issue cluster + one-at-a-time commits to main prevents lock races. Pattern requires serialized commit dispatch, not concurrent writes to origin/main.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
