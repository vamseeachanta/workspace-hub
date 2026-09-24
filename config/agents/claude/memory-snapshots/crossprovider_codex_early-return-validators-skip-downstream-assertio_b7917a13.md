---
name: crossprovider codex early-return-validators-skip-downstream-assertio
description: Early-return validators skip downstream assertions unless explicitly tested
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validator-pattern, test-coverage, regression-hazard]
---

When a validator has a guard (e.g., 'skip non-ready rows'), the skipped assertions remain invisible until tested in isolation on a ready row or with the guard removed. Early returns prevent cascades, but tests must verify both the guard AND the guarded logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
