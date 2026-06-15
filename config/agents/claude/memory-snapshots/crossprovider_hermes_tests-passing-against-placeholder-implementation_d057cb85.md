---
name: crossprovider hermes tests-passing-against-placeholder-implementation
description: Tests passing against placeholder implementations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, proj-a, tdd, placeholder-risk]
---

Tests for OCIMF coefficient generation passed despite using placeholder trigonometric formulas instead of workbook-derived values. Tests were checking for the placeholder string presence rather than correctness against requirements. Requirement-based tests (e.g., verifying specific workbook coefficients) would have failed the weak implementation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
