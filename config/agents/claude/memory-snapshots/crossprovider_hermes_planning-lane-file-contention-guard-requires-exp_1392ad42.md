---
name: crossprovider hermes planning-lane-file-contention-guard-requires-exp
description: Planning-lane file-contention guard requires explicit path constraints
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, git-contention, worktree-isolation]
---

Parallel planning sessions writing shared artifacts (e.g., docs/plans/README.md) require explicit session-constraint prohibition, not just documentation. Docs-only statements are insufficient to prevent branch conflicts when 3+ planning worktrees modify the same file simultaneously.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
