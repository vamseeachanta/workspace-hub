---
name: crossprovider codex concurrent-read-only-review-can-produce-stale-in
description: Concurrent read-only review can produce stale index.lock; use GIT_OPTIONAL_LOCKS=0 for cross-reviewer verification
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [git, concurrency, review]
---

Multiple agents reviewing the same plan in the same worktree can leave index.lock if one process hangs or times out. Set GIT_OPTIONAL_LOCKS=0 for read-only operations to avoid locking overhead. A stale lock suggests review state disagreement; do not remove it blindly — diagnose the conflict first.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
