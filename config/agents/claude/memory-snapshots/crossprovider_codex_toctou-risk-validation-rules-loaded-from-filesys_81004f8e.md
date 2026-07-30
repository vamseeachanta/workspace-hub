---
name: crossprovider codex toctou-risk-validation-rules-loaded-from-filesys
description: TOCTOU risk: validation rules loaded from filesystem, not Git
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [git, staging, validation]
---

If validation taxonomy/rules are loaded from the working tree instead of Git blobs, an unstaged edit can authorize staged content that is absent from both HEAD and index. Bind all validation rules to `HEAD:<path>` or staged index blobs, never the working-tree filesystem.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
