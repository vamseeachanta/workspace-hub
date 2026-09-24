---
name: crossprovider codex symlink-and-build-cache-pruning-pattern-for-inve
description: Symlink and build-cache pruning pattern for inventory counts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [inventory-pattern, cache-safety, llm-wiki-pattern]
---

When counting files/dirs for inventory reports, skip: `.git`, `.venv`, `.pytest_cache`, `__pycache__`, `node_modules`, and all symlinked entries. This keeps inventory counts focused on authored content and prevents false duplicates from build/cache multiplicity. Tests must verify pruning happens and that symlinks are not followed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
