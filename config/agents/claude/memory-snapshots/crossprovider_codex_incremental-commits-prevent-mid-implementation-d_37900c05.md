---
name: crossprovider codex incremental-commits-prevent-mid-implementation-d
description: Incremental commits prevent mid-implementation data loss
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [workflow, git, safety]
---

Commit as soon as test suite passes, not at the end. A previous session lost work by batching commits; timeout or crash mid-implementation clobbers unsaved changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
