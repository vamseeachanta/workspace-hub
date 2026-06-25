---
name: crossprovider codex git-tracked-state-and-origin-main-should-be-the-
description: Git-tracked state and origin/main should be the reference, not working-tree snapshots
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [git-reference-clarity, parallel-work, worktree-safety]
---

Before judging whether a repo artifact is stale, check `git show origin/main:path` not the working-copy version. A parallel session on a different branch or worktree may have different artifact versions checked out. Similarly, verify `git rev-parse --abbrev-ref HEAD` to confirm you are reviewing what you think you are reviewing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
