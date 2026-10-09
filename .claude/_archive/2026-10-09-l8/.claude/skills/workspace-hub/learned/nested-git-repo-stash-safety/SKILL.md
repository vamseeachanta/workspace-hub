---
name: nested-git-repo-stash-safety
description: How to safely stash changes in a parent repo containing dirty nested git repositories
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["git", "submodules", "nested-repos", "stash", "workflow"]
---

# Nested Git Repo Stash Safety

When a parent repo contains a nested git repository (gitlink pointer), `git stash` in the parent only captures the SHA pointer to the nested repo, not the nested repo's actual working-tree changes. Modified files inside the nested repo are invisible to the parent's stash and will survive or be left behind unpredictably. Always manually snapshot or stash changes inside nested repos separately before performing parent-repo operations. Use `git status` to detect `m` (modified gitlink) entries indicating a dirty nested repo state.