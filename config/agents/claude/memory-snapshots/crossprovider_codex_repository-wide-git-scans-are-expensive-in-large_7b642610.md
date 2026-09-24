---
name: crossprovider codex repository-wide-git-scans-are-expensive-in-large
description: Repository-wide git scans are expensive in large worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, git, workspace-hub]
---

Operations like `git status` and `git diff` across the full workspace-hub take 7–10 seconds each. For targeted change detection (e.g., skill nudging), use SessionStart timestamps + bounded `find` on specific subdirectories (`.claude/skills/`) instead of repo-wide git scans.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
