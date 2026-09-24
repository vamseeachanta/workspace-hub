---
name: crossprovider codex git-add-u-silently-skips-untracked-files
description: git add -u silently skips untracked files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, testing, commit-hazard]
---

Using `git add -u` in a final commit stages only modifications to tracked files and omits untracked new files. New unit tests or fixtures added during development must be explicitly added by name, or they will be silently dropped from the commit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
