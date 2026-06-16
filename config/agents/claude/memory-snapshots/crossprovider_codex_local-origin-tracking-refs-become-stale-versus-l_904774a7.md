---
name: crossprovider codex local-origin-tracking-refs-become-stale-versus-l
description: Local origin tracking refs become stale versus live remote
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [git, remote-state, sync]
---

`git status` may show 0/0 ahead/behind even when the remote has advanced; local `refs/remotes/origin/*` caches lag live remote state. Always use `git fetch` or `git ls-remote` to verify true upstream state before claiming repos are synced.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
