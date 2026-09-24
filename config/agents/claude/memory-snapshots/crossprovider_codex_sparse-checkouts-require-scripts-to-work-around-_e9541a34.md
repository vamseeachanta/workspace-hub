---
name: crossprovider codex sparse-checkouts-require-scripts-to-work-around-
description: Sparse checkouts require scripts to work around intentionally absent subtrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sparse-checkout, script-design]
---

When a checkout intentionally omits large subdirs (e.g., 19K-file sources/ tree), scripts operating on parent indexes must not assume those trees are readable. Chunking and pagination scripts should handle missing source materialization gracefully and document the sparse-checkout constraint.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
