---
name: multi-repo-git-recovery
description: Diagnose and recover from stale lock files, diverged branches, and untracked file conflicts across multiple repos in a workspace ecosystem
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["git", "multi-repo", "debugging", "workspace-management"]
---

# Multi-Repo Git Recovery Pattern

When bulk operations (pull/push) fail across multiple repos, diagnose each failure in parallel first. Common blockers: stale `.git/index.lock` files from crashed processes, diverged branches requiring merge-pulls, and untracked files conflicting with incoming changes. Kill any lingering git processes, remove stale locks, restore deleted symlinks/files, then retry. Use `git add -A` with force flags when needed to stage untracked files before merge operations.