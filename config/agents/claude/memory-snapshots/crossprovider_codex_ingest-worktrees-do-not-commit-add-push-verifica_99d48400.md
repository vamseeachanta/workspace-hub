---
name: crossprovider codex ingest-worktrees-do-not-commit-add-push-verifica
description: Ingest worktrees do not commit/add/push; verification and edits are in-tree, promotion is separate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, worktree, discipline, ingest-safety]
---

Temporary ingest worktrees (ingest/api-corpus, ingest/iso-branch) are ahead of origin with prior local commits. During ingest, perform writes and verification in-worktree only; do NOT stage, commit, or push. Commits and promotions happen in a separate workflow. Worktree isolation prevents accidental upstream pushes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
