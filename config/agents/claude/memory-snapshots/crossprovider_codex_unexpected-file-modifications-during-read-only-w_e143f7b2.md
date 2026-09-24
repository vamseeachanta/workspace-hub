---
name: crossprovider codex unexpected-file-modifications-during-read-only-w
description: Unexpected file modifications during read-only work signal external/parallel agents
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parallel-work, coordination, worktree-state]
---

If a worktree becomes dirty (git status shows modified files) during a read-only session and the current agent made no edits, that signals external/parallel work. Report the dirty state as context for coordination; do not resolve or validate external changes. Allows concurrent agents to work without trampling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
