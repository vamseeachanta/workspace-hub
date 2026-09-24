---
name: crossprovider codex cross-branch-duplicate-resolution-via-target-exi
description: Cross-branch duplicate resolution via target-existence check
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, merge-conflict, ingest, deduplication]
---

When resolving merge conflicts in multi-branch ingest scenarios, for unmerged paths that already exist on the merge target (origin/main), check existence with `git cat-file -e origin/main:<path>` and resolve by taking the target's version. This handles cross-branch duplicates that are already canonical on main without requiring manual conflict resolution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
