---
name: crossprovider codex git-status-hangs-under-repository-contention-use
description: Git status hangs under repository contention; use plumbing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-operations, performance, parallelism]
---

When multiple agents/processes touch git simultaneously, git status commands timeout globally. Use faster alternatives: git diff-index --cached (cheap dirty check), git branch --list (branch identity), git worktree list --porcelain (worktree metadata), and fs inspection (.git/worktrees) to avoid hangs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
