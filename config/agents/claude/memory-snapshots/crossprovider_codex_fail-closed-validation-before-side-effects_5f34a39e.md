---
name: crossprovider codex fail-closed-validation-before-side-effects
description: Fail-closed validation before side effects
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [correctness, validation, safety]
---

Validation that guards correctness (e.g., exact issue set membership, tranche completeness) must complete and pass before any side effects (mkdir, file writes, object creation). A failure after a mkdir leaves a partial artifact that masks the defect and breaks idempotent reruns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
