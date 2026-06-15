---
name: crossprovider codex git-worktree-state-can-vanish-during-parallel-ta
description: Git worktree state can vanish during parallel task coordination; recover via remote branch diff
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git, worktree, concurrency, recovery, llm-wiki#23]
---

llm-wiki #23 session: isolated worktree disappeared mid-task without user action. Recovery: use `git diff main...origin/branch` to verify artifacts and continue review without the worktree. Pattern for multi-worker coordination: assume worktree may vanish; have a git-only fallback.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
