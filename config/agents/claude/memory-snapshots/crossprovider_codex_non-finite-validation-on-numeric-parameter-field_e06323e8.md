---
name: crossprovider codex non-finite-validation-on-numeric-parameter-field
description: Non-finite validation on numeric parameter fields
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, pydantic, numeric-correctness]
---

Pydantic validators with range checks miss NaN/inf because NaN comparisons are false and inf passes bounds. Add explicit `math.isfinite()` checks on all float parameter fields to catch invalid priors and distribution parameters.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
