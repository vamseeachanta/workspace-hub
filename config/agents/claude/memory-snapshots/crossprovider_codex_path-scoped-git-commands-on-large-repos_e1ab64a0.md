---
name: crossprovider codex path-scoped-git-commands-on-large-repos
description: Path-scoped Git commands on large repos
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [git, workaround, performance]
---

`git status` and `git diff` without pathspecs hang on large repositories. Use path-specific commands: `git status -- path/to/file`, `git diff HEAD -- scripts/` instead of repo-wide scans.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
