---
name: crossprovider codex worktree-git-metadata-path-determines-sandbox-wr
description: Worktree git-metadata path determines sandbox write permissions
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [sandbox, worktree, permissions, git]
---

Worktree files at /mnt/local-analysis/wt-2802 were writable, but git metadata under .git/worktrees/wt-2802 was read-only, blocking commits. Relocating to /mnt/local-analysis/workspace-hub/.claude/worktrees/wt-2802 (parent .git writable) unblocked both. The git metadata location is the permission boundary, not the worktree files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
