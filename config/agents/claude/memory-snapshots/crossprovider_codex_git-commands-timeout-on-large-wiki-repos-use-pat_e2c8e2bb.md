---
name: crossprovider codex git-commands-timeout-on-large-wiki-repos-use-pat
description: Git commands timeout on large wiki repos; use path-scoped/untracked-filtered queries instead
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, performance, large-repos, wiki]
---

Full `git status` hangs on repos with large wiki content (40+ second timeouts observed). Use `git ls-files --name-only <paths>`, `git diff --name-only <paths>`, or `git status --untracked-files=no` to get scoped output without untracked-file scanning.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
