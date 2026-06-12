---
name: crossprovider hermes weak-tdd-masks-incomplete-implementations
description: Weak TDD masks incomplete implementations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, testing, defect-masking]
---

Tests that pass on placeholder values or missing fields provide false confidence; the bug manifests at runtime (undefined JS properties, missing data in output). TDD requires red tests first—tests that fail on the incomplete implementation and pass only when all fields are correctly implemented.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
