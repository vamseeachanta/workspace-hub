---
name: diagnose-symlink-shebang-persistence
description: Fix persistent shebang issues in symlinked CLI entry points that revert after git operations
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["debugging", "symlinks", "python-venv", "cli-tools", "git"]
---

# Diagnose Symlink Shebang Persistence Issues

When a CLI tool's shebang keeps reverting after updates, check if the symlink points to a repo file vs. a venv entry point. If `~/.local/bin/tool` → `repo/tool` (symlink), edits revert on `git pull`. Solution: repoint the symlink to the venv entry point instead (`~/.local/bin/tool` → `~/.venv/bin/tool`). This bypasses repo resets while preserving the correct shebang and venv context. Verify with `ls -l` and `file` commands.