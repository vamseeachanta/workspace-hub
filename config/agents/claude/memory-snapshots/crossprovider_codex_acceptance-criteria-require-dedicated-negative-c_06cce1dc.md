---
name: crossprovider codex acceptance-criteria-require-dedicated-negative-c
description: Acceptance Criteria Require Dedicated Negative-Case Tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, acceptance-criteria, test-design]
---

Tests passing positive paths while plan acceptance criteria remain unmet (e.g., quota/cap enforcement asserted in plan but not tested). Acceptance criteria that specify restrictions need explicit negative-case tests; relying on positive-path coverage alone misses cases where validators accept invalid data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
