---
name: crossprovider codex git-worktree-paths-drift-in-parallel-work-enviro
description: Git worktree paths drift in parallel work environments
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [git, worktree, parallel-work]
---

Worktree checkout paths can become orphaned or shift between sessions in shared directories. Always verify active worktrees via `git worktree list` before assuming a path is canonical; assign per-agent worktree directories to prevent branch contamination during multi-agent runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
