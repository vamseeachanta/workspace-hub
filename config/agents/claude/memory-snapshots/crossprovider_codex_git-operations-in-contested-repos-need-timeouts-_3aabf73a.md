---
name: crossprovider codex git-operations-in-contested-repos-need-timeouts-
description: Git operations in contested repos need timeouts and lock-disable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, shared-infrastructure, operational-pattern]
---

Use `timeout 10s env GIT_OPTIONAL_LOCKS=0 git <command>` pattern when probing shared repos to avoid hangs on actively-held git locks. Prevents agents from stalling indefinitely on `git status`, `git worktree list`, and similar operations in environments with concurrent access.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
