---
name: crossprovider codex symlink-cache-pruning-must-be-applied-consistent
description: Symlink/cache pruning must be applied consistently to all count fields
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [traversal-safety, cache-pruning, symlink-handling]
---

Exclude `.git`, `.venv`, `.pytest_cache`, `__pycache__`, `node_modules`, and symlinked entries from all count aggregates. A prior #731 fix showed `top_level_entry_count` was not pruning symlinks while file/dir counts were—inconsistency led to wrong inventory totals. Apply the same PRUNE_DIRS list and symlink-skip logic to every count-aggregation code path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
