---
name: crossprovider gemini pre-commit-hooks-use-git-diff-cached-not-head-1
description: Pre-commit hooks: use git diff --cached, not HEAD~1
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git-hooks, pre-commit, edge-case-handling]
---

Using `git diff HEAD~1..HEAD` in pre-commit hooks misses staged files and working directory changes. Use `git diff --cached --name-only` for staged files in pre-commit context. Add graceful fallback for initial commits where HEAD~1 doesn't exist (check for ENOENT, use `git ls-files` as fallback).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
