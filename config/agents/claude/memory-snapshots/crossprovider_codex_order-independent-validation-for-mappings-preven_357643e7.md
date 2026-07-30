---
name: crossprovider codex order-independent-validation-for-mappings-preven
description: Order-independent validation for mappings prevents subprocess failures
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [yaml, validation, subprocess, testing]
---

When validating YAML or mapping structures, insertion order is not validation semantics. If a subprocess expects keys in alphabetical order but receives insertion-order, validation fails despite logical equivalence. Use order-independent comparison for mappings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
