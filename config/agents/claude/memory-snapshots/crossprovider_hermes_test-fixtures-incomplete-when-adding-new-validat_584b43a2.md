---
name: crossprovider hermes test-fixtures-incomplete-when-adding-new-validat
description: Test fixtures incomplete when adding new validation layers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-regression, test-fixtures, validation-layers, test-maintenance]
---

Issue #2766 added `upstream_policy` validation but test fixtures weren't updated to include it. Downstream tests failed due to missing required field. When adding policy/schema constraints, audit all fixtures for new required fields, not just test the new layer.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
