---
name: crossprovider codex pre-commit-hooks-in-shared-git-directories-must-
description: Pre-commit hooks in shared Git directories must resolve worktree context at hook execution time
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [git, hooks, worktree-isolation, git-plumbing]
---

Storing the installing worktree's root in a hook makes the shared hook scan wrong checkouts when other worktrees commit. Instead, resolve `REPO_ROOT` at hook execution time from the active worktree's `.git` directory, and validate against refs/paths using exact Git object IDs and NUL-delimited parsing to prevent option-injection attacks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
