---
name: crossprovider codex linked-worktree-provisioning-needs-git-c-checks-
description: Linked worktree provisioning needs git-C checks, not stat checks on .git
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, provisioning, testing]
---

.git is a file (not directory) in linked worktrees, so `[[ -d .git ]]` fails silently. Use `git -C <dir> rev-parse --is-inside-work-tree` to detect worktrees reliably. Existing tests that check wrong variable names pass vacuously.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
