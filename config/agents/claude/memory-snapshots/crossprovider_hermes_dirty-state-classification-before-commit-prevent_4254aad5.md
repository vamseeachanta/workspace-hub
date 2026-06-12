---
name: crossprovider hermes dirty-state-classification-before-commit-prevent
description: Dirty state classification before commit prevents scope creep
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, hygiene, scope]
---

Before staging/committing implementation work, classify all dirty files into (1) task-owned, (2) unrelated pre-existing, (3) unrelated session-generated. Commit only task-owned changes; never sweep unrelated dirt into implementation commits. Use pathspec or explicit `git add` to scope commits.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
