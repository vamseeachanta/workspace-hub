---
name: crossprovider hermes source-registry-membership-validation-only-in-te
description: Source registry membership validation only in tests, not schema
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [source-registry, validation-layers, test-gaps]
---

Execution manifest schemas accept any string in source_ids; registry membership verified only in fixture tests, not schema validation. Unknown source IDs validate successfully against schema. Runtime validator needed before report_eligible decision; add negative tests for unregistered IDs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
