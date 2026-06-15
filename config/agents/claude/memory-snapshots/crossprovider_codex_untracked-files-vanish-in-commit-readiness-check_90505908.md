---
name: crossprovider codex untracked-files-vanish-in-commit-readiness-check
description: Untracked files vanish in commit-readiness checks
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git-workflows, commit-safety, risk-mitigation]
---

`git diff --name-only` omits untracked files; use `git status --untracked-files=all` to inventory before committing. Pathspec commits risk dropping new artifacts while index/log references stay, leaving dangling references. Always validate staged state before invoking commit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
