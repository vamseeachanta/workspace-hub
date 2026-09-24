---
name: crossprovider codex non-finite-and-edge-values-require-explicit-vali
description: Non-finite and edge values require explicit validation and tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, edge-cases, numerical-stability]
---

Checks like `<= 0` do not reject `NaN` or positive infinity. If a formula requires finite positive values, enforce that explicitly (e.g., `isinf()`, `isnan()`, `not (0 < x < inf)`). Add dedicated tests for NaN, infinity, zero, and negative edge cases. These can produce physically inconsistent or silent-fail outputs otherwise.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
