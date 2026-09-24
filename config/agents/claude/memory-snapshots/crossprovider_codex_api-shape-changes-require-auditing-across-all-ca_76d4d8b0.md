---
name: crossprovider codex api-shape-changes-require-auditing-across-all-ca
description: API shape changes require auditing across all call sites
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-design, refactoring-hazards, test-regression]
---

Return-value unpacking changes (e.g., function returning tuple vs bare value) hide regressions in test code and conditional branches. Audit every caller—including tests and skip paths—not just primary callers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
