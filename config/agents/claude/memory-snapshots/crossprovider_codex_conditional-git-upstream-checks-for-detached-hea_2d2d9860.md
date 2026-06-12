---
name: crossprovider codex conditional-git-upstream-checks-for-detached-hea
description: Conditional git upstream checks for detached HEAD
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git, prerequisites, detached-head]
---

Detached HEAD repos fail `git rev-parse --abbrev-ref --symbolic-full-name @{u}`. Prerequisites should use `if [ "$(git rev-parse --abbrev-ref HEAD)" != "HEAD" ]` to conditionally require upstream tracking, not always.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
