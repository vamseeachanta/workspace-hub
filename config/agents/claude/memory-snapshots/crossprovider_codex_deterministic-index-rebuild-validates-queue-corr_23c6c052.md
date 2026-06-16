---
name: crossprovider codex deterministic-index-rebuild-validates-queue-corr
description: Deterministic index rebuild validates queue correctness
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [index-rebuild, queue-verification, deterministic-pipelines]
---

If index generation is deterministic and fully queue-driven (no manual edits), rebuilding the index and comparing aggregate row counts against expected queue changes proves queue completeness and catches stale index state. Use as a gate-passing verification artifact.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
