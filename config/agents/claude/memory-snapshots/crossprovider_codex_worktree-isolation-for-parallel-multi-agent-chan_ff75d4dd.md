---
name: crossprovider codex worktree-isolation-for-parallel-multi-agent-chan
description: Worktree isolation for parallel multi-agent changes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [parallelism, git-workflow, coordination]
---

When multiple Codex sessions work on the same codebase, explicitly STAY OUT of overlapping files and use separate worktrees. Shared checkouts with --amend or concurrent edits clobber parallel work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
