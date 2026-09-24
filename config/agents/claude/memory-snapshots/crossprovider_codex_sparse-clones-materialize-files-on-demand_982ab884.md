---
name: crossprovider codex sparse-clones-materialize-files-on-demand
description: Sparse clones materialize files on demand
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, sparse-clone, performance]
---

In sparse clones, files tracked in HEAD may not be materialized in the working tree. Use `git show HEAD:<path>` to read tracked content rather than filesystem operations. Broad `git status` can timeout on large repos; prefer `git ls-tree` or targeted `git show` for read-only inspection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
