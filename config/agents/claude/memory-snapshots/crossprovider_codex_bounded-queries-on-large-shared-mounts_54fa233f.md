---
name: crossprovider codex bounded-queries-on-large-shared-mounts
description: Bounded queries on large shared mounts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [shared-storage, performance, queries]
---

Recursive filesystem searches on large shared mounts (e.g., /mnt/ace with ~3M files) spiral unbounded; use direct likely-path queries, bounded recursion, or timeouts instead of exploratory grepping.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
