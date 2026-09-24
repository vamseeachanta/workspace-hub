---
name: crossprovider codex large-shared-worktrees-timeout-on-broad-git-oper
description: Large shared worktrees timeout on broad Git operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workspace-hub, git-performance, shared-worktree]
---

workspace-hub's large worktree with many parallel agent checkouts causes `git status`, `git diff`, and untracked-file scans to timeout. Solution: use bounded queries targeting specific tracked-file paths; for commits, bypass the slow index walk with Git plumbing (`git write-tree`, `git commit-tree`, `git update-ref`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
