---
name: crossprovider codex automatic-worktree-deletion-has-unfixable-toctou
description: Automatic worktree deletion has unfixable TOCTOU race
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, concurrency, toctou, safety]
---

Verification-then-delete cannot prevent concurrent writes; another agent can enter/write between pre-delete checks. Nested repos, submodules, symlinks, and ignored content risk loss. Worktree cleanup must be report-only or use two-phase quarantine with grace period, not automatic deletion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
