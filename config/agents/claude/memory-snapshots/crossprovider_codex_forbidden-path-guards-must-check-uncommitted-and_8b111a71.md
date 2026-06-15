---
name: crossprovider codex forbidden-path-guards-must-check-uncommitted-and
description: Forbidden-path guards must check uncommitted and untracked files
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [scope-validation, git-state, governance]
---

Scope-validation scripts checking only `git diff` miss untracked and uncommitted worktree state. Build the changed-paths set from all three sources: `git diff --name-only <base>...HEAD`, `git diff --name-only` (staged), and `git ls-files --others --exclude-standard`. Failure to do this allows scope creep in issue branches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
