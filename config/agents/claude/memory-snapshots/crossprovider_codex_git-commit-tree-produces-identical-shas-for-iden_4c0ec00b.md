---
name: crossprovider codex git-commit-tree-produces-identical-shas-for-iden
description: Git commit-tree produces identical SHAs for identical content+timestamp
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, cas, distributed-systems]
---

When tree, message, author/committer, and timestamp match, commit-tree produces the same commit SHA. Identical-content CAS updates silently no-op, breaking generation/version monotonicity if treated as version advances.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
