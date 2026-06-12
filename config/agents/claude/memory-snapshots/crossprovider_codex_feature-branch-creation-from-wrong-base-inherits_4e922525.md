---
name: crossprovider codex feature-branch-creation-from-wrong-base-inherits
description: Feature branch creation from wrong base inherits unrelated commits
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-workflow, feature-branches, trunk-based]
---

`git checkout -b feature/WRK-X` without explicit base uses current HEAD, not trunk. If run while on another feature branch, new branch inherits unrelated commits. Must explicitly `git checkout -b feature/WRK-X origin/main` to ensure trunk-based branching.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
