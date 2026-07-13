---
name: crossprovider codex cleanup-disposition-requires-per-folder-verifica
description: Cleanup disposition requires per-folder verification, never age-based deletion
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [cleanup-operations, workspace-governance, verification-first]
---

Workspace cleanup contract: classify every folder by origin (canonical repo, worktree, artifact), state (dirty, untracked, stashed), active references (live process, approved issue), and residue type. Ambiguous items are preserved and reported; only clearly disposable items are removed. This prevents silent data loss in a multi-agent, multi-session environment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
