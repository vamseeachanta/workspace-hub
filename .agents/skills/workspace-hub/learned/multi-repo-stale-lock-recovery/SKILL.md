---
name: multi-repo-stale-lock-recovery
description: Diagnose and recover from stale git lock files in multi-repo workspaces, especially with submodules
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["git", "multi-repo", "debugging", "stale-locks"]
---

# Multi-Repo Stale Lock Recovery

When bulk operations fail across multiple repos with `.git/index.lock` errors, check for stale crashes from background processes (especially with submodules). Use `lsof` to verify no git process is actually running, then safely remove the lock file and retry. If the lock reappears immediately after cleanup, a background process may still be running — wait briefly and monitor with `ps` before retrying. In submodule-heavy workspaces, lock files in one repo can reference another's submodule path.