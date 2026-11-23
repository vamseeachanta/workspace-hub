---
name: multi-repo-sync-diagnosis-repair
description: Diagnose and repair failed pulls across multi-repo ecosystems with stale locks, submodule conflicts, and untracked files
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["git", "multi-repo", "debugging", "workspace-management"]
---

# Multi-Repo Sync Diagnosis and Repair

When bulk pulls fail across repos in a multi-repo workspace, diagnose failures in parallel and categorize by type: diverged branches (ahead/behind), stale lock files, submodule issues, or untracked file conflicts. For each failure, identify root cause (deleted symlinks, untracked dirs, stale `.git/index.lock`), remove blocking artifacts, then retry with appropriate merge strategy. Handle background git processes that may leave stale locks by checking running processes and waiting before retry.