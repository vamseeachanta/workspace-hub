---
name: crossprovider codex cumulative-budget-tracking-in-recursive-git-oper
description: Cumulative budget tracking in recursive Git operations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [performance, denial-of-service, git]
---

Track traversal budget cumulatively (not per-operation), apply total before recursive operations. Prevents denial-of-service via deep/wide trees. Apply budget bounds before entry, not within loop.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
