---
name: crossprovider hermes schema-code-contract-drift-enables-unsafe-emissi
description: Schema/code contract drift enables unsafe emissions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, schema, regression-testing, defect-class]
---

Implementation can diverge from documented schema (e.g., code emitting unresolved targets despite schema saying 'drop'), allowing violations to slip through. Regression tests must explicitly cover both the schema contract statement AND the code path that enforces it, with negative test cases for violations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
