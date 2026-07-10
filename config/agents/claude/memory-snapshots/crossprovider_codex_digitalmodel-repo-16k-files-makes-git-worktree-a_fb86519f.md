---
name: crossprovider codex digitalmodel-repo-16k-files-makes-git-worktree-a
description: digitalmodel repo 16k files makes git worktree add slow
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [environment, git-worktrees, digitalmodel, performance]
---

The dm repo has ~16k tracked files, causing `git worktree add` to take several minutes during checkout materialization. Plan worktree operations sequentially; do not expect parallelism. Verify no concurrent worktrees write to shared paths during checkout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
