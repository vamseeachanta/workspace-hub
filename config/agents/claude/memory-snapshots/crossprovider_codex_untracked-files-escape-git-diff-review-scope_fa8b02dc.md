---
name: crossprovider codex untracked-files-escape-git-diff-review-scope
description: Untracked files escape git diff review scope
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [review-methodology, git, testing]
---

When reviewing uncommitted changes with `git diff`, untracked files (e.g., newly-written test files not yet staged) are invisible to diff-based gates. Review scope must explicitly check for untracked artifacts or risk missing test coverage. Use `git status --short` or `git ls-files -o --exclude-standard` to surface them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
