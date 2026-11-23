---
name: multi-repo-sync-diagnosis-and-repair
description: Systematic approach to diagnosing and repairing failures across a multi-repo workspace
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["git", "multi-repo", "debugging", "automation"]
---

# Multi-Repo Sync Diagnosis and Repair

When bulk operations fail across multiple repos, diagnose failures in parallel by isolating each repo's specific state (ahead/behind, working tree changes, submodule status). Identify and clear stale lock files that block git operations. Handle untracked files that conflict with incoming changes by temporarily moving them aside before pull, then restoring after. For pre-commit hook failures (e.g., oversized files), selectively exclude problematic files and recommit rather than abandoning the entire staging.