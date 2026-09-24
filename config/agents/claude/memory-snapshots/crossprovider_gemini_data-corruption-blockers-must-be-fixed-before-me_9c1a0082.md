---
name: crossprovider gemini data-corruption-blockers-must-be-fixed-before-me
description: Data corruption blockers must be fixed before merge, not deferred
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [blocker-management, code-review, idempotency]
---

A defect that corrupts persistent state (duplicate children in feature decomposition) when an operation is re-run is a blocker. Deferring to 'future work' merges broken code; instead, add guard conditions (e.g., 'already-populated → abort') in the same PR.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
