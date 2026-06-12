---
name: crossprovider codex read-only-git-with-locks-disabled-mitigates-work
description: Read-only git with locks disabled mitigates workspace-hub contention
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-operations, workspace-hub, concurrency]
---

Large-repo scouts use `timeout 10s env GIT_OPTIONAL_LOCKS=0 git <cmd>` to prevent `git status` freezes and lock-wait timeouts on workspace-hub during parallel activity. Applies to `git status`, `git worktree list`, `git branch` — use consistently in read-only scout contexts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
