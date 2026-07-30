---
name: crossprovider codex git-performance-on-large-tracked-trees
description: Git performance on large tracked trees
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [performance, git, environment-fact]
---

Repos with ~16k tracked files see slow worktree creation and expensive `git status` scans. On shared/active checkouts, avoid even read-only status output; use narrow `git show origin/main:<path>` and `git diff`-scoped queries instead. Read-only probes should skip aggregate status and preserve unrelated worktree state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
