---
name: fix-symlink-shebang-persistence
description: Permanently fix shebang issues in symlinked CLI tools that get overwritten by git updates
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["debugging", "symlinks", "cli-tools", "python", "venv"]
---

# Fix Symlink Shebang Persistence

When a symlink points to a git-tracked repo file with a generic shebang (e.g., `#!/usr/bin/env python3`), edits get overwritten on `git pull`. Instead of editing the repo file, repoint the symlink to the venv's generated entry point (e.g., `~/.venv/bin/hermes`), which has the correct venv-specific shebang and isn't git-tracked. Use `ln -sf <new-target> <symlink>` to update the symlink target.