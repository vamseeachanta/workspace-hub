---
name: crossprovider hermes git-operation-chains-under-heavy-load-use-not-gi
description: Git operation chains under heavy load: use `;` not `&&`, GIT_OPTIONAL_LOCKS=0
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, concurrency, timeout, performance, load]
---

Under multi-git load (>20 concurrent procs), chain operations with `;` instead of `&&` to prevent one stuck step from blocking the entire chain. Use `GIT_OPTIONAL_LOCKS=0` to bypass lock waits; timeout worktree ops at 30–60s and write recovery notes on hang.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
