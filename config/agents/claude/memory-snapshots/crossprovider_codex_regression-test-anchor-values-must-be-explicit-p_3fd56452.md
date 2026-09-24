---
name: crossprovider codex regression-test-anchor-values-must-be-explicit-p
description: Regression test anchor values must be explicit pytest assertions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, regression, pytest]
---

Implicit regression validation through smoke-test generation is insufficient. Regression anchor values (e.g., yaw moment +112.158527 kN-m) must be explicitly asserted in pytest tests, not just checked by artifact generation. This ensures regression coverage is verifiable and maintainable across refactors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
