---
name: crossprovider codex git-operations-hang-on-large-repos-use-path-scop
description: Git operations hang on large repos; use path-scoped commands instead
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-performance, large-repos, workaround, operational-constraint]
---

In large repositories (e.g., 33K files, 78 MB), `git status`, `git diff`, and broad `git ls-files` hang due to filesystem traversal overhead. Workaround: use path-scoped commands like `git diff HEAD -- <pathspec>`, `git ls-files -- <path>`, and `git diff --cached -- <pathspec>`, which reliably complete even when full-repo commands timeout. Avoid broad git operations in reviews/reads of large checkouts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
