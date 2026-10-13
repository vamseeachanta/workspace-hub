---
name: git-large-file-staging-conflict-recovery
description: Recover from pre-commit hook blocks on oversized files and corrupted rebase states during bulk repo syncs
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["git", "debugging", "bulk-operations", "conflict-resolution"]
---

# Git Large File Staging & Rebase Corruption Recovery

When pre-commit hooks block commits due to oversized files (e.g., >5MB logs), unstage the problematic files, reset the staging area, then selectively re-add excluding large aggregated files. If a rebase-merge directory exists with only an autostash file, it signals corruption — remove it and switch to merge-pull instead. For untracked files blocking pulls, move them to /tmp, complete the pull, then restore. Use `git status` and `git log` to verify state before proceeding.