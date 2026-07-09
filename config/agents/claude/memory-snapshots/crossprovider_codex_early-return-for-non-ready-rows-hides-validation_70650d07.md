---
name: crossprovider codex early-return-for-non-ready-rows-hides-validation
description: Early-return for non-ready rows hides validation drift
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [validator-design, non-ready-state, regression-hazard]
---

Skipping validation on pending/non-ready rows (e.g., `if not ready: return`) prevents detecting state inconsistencies that should be caught regardless of readiness; red conditions can hide in that bypass path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
