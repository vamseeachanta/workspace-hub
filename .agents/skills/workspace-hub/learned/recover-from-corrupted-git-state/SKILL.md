---
name: recover-from-corrupted-git-state
description: Diagnose and recover from corrupted git states (stale locks, failed rebases, pre-commit hook blocks) during bulk operations
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["git", "troubleshooting", "bulk-sync", "state-recovery"]
---

# Recover from Corrupted Git State

When bulk git operations (large commits, background pulls, rebases) fail or leave stale state: (1) Check for lock files and background processes (`ps aux | grep git`); (2) Detect corrupted rebase state via `rebase-merge` directory — abort with `git rebase --abort` and switch to merge; (3) If pre-commit hooks block large files, unstage oversized files and recommit selectively; (4) For untracked file conflicts during pull, move conflicting files to `/tmp`, pull, then restore; (5) Always verify final state with `git status` and divergence count (should be 0/0 after sync).