---
name: recover-from-stale-git-locks
description: Diagnose and recover from stale git lock files caused by crashed background processes
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["git", "debugging", "automation", "recovery"]
---

# Recover from Stale Git Locks

When git operations fail with `.git/index.lock` errors, the lock file may persist after a crash. Check if any git process is actually running with `ps aux | grep git`. If none exist, safely remove the stale lock file with `rm .git/index.lock`, then retry the operation. For submodules or nested repos, check and clean locks in each `.git` directory. Always verify the background process completed before proceeding.