---
name: crossprovider codex documented-field-requirements-must-be-enforced-b
description: Documented field requirements must be enforced by validator and test fixture
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [test-coverage, documentation-tracking, contract-enforcement]
---

When documentation lists required fields (`logical_target_store`, `extraction_estimate`), the validator must reject rows missing them, and the test fixture must include them. Documentation + documentation alone leaves enforcement to runtime discovery. The #52 fixtures omitted required fields and the validator accepted them because neither enforced the written requirement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
