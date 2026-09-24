---
name: crossprovider codex contested-worktree-git-prefer-github-api-data
description: Contested worktree Git = prefer GitHub API data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, worktree, operational]
---

In shared or linked Git worktrees where concurrent operations cause `git status`/`git log` to hang, avoid local git commands for validation. Instead use live GitHub API/PR/CI data for target state checks (PR metadata, workflow runs, branch SHA). Unblocks inspection when worktree Git is contested by other processes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
