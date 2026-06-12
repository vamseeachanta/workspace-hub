---
name: crossprovider codex sparse-worktree-state-is-pre-existing-avoid-broa
description: Sparse worktree state is pre-existing; avoid broad git operations
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [worktree, git, state-management, parallel-work]
---

Ingest worktrees (e.g., ingest/api-corpus, ingest/iso-corpus) often start 'ahead N, behind M' from prior batches. Treat this as owned state; confine edits to your batch scope and avoid `git reset`, `git clean`, or other broad repo operations that could sweep parallel work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
