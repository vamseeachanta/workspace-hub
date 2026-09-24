---
name: crossprovider codex quarantine-root-size-measurement-requires-stat-n
description: Quarantine root size measurement requires stat, not walk-based traversal
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-privacy, filesystem-ops, test-coverage]
---

Even 'root-level size only' via du or os.walk traverses private directory entries and can leak info or trigger permissions issues. Quarantine roots should use stat-level metadata only, or size should come from precomputed cache with tests asserting the walk function is never called on private roots.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
