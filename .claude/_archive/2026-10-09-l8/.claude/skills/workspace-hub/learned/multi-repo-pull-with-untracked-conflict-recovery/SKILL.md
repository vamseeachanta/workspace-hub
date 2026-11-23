---
name: multi-repo-pull-with-untracked-conflict-recovery
description: Diagnose and resolve multi-repo pull failures caused by untracked files conflicting with remote changes
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["git", "multi-repo", "workflow", "debugging", "conflict-resolution"]
---

# Multi-Repo Pull with Untracked Conflict Recovery

When a multi-repo pull fails due to untracked local files conflicting with incoming remote files, use `git stash -u` (not plain `git stash`) to capture both tracked and untracked changes. This temporarily moves marker files like `.codex/` and `.claude/skills/` out of the way before pulling. After pull succeeds, restore the stash and verify no conflict markers remain — then safely drop the stash. This pattern handles the common case where workflow metadata or generated files block standard pulls in workspace ecosystems.