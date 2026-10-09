---
name: git-stale-lock-recovery
description: Diagnose and recover from git stale lock files and corrupted rebase states in multi-repo workflows
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["git", "debugging", "repo-sync", "lock-recovery"]
---

# Git Stale Lock Recovery

When git operations fail with lock errors across multiple repos, identify stale `.git/index.lock` files left by crashed processes. Remove locks with `rm .git/index.lock`, then retry. For corrupted rebase states, check `git rebase-merge/` — if only `autostash` exists, the rebase is corrupted; abort with `git rebase --abort` and use merge instead. Always wait for background git processes (check `ps`) before retrying, as incomplete operations leave stale locks.