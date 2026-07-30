---
name: crossprovider codex use-origin-main-snapshots-during-slow-worktree-m
description: Use origin/main snapshots during slow worktree materialization
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [git-workflow, worktrees, large-repos]
---

On large repos (~16k tracked files), initial worktree checkout is slow but safe to wait for. During checkout, use `git show origin/<branch>:<file>` to inspect current code structure and prepare TDD targets rather than blocking on worktree completion, keeping parallel work productive.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
