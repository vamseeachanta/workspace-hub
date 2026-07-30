---
name: crossprovider codex parallel-session-residue-in-worktrees-requires-r
description: Parallel-session residue in worktrees requires read-only coordination
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [coordination, worktree, parallel-agents, multi-session]
---

When multiple agents operate on the same worktree, untracked files and edits from other sessions will be present (e.g., review artifacts, concurrent CI config changes). Keep each agent's changes to its approved scope and treat untracked/out-of-scope edits as off-limits. Verify evidence from committed diffs and tracked files only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
