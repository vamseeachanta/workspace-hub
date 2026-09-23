---
name: crossprovider codex worktree-virtualenv-via-shared-symlink-preserves
description: Worktree virtualenv via shared symlink preserves interpreter paths
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [virtualenv, worktree, python]
---

When a worktree lacks `.venv`, symlink to a shared venv instead of substituting `uv run` or hardcoding absolute paths. This keeps relative interpreter references in tracked files stable and avoids forcing tool-specific paths into the codebase.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
