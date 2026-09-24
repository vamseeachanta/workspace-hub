---
name: crossprovider codex schema-field-changes-in-plans-require-exact-json
description: Schema field changes in plans require exact JSON keys, types, and validator logic
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-specification, plan-review, implementability]
---

Textual plan descriptions like 'define issue-local skill groups in split row' are not implementable until the exact JSON key/type, validator checks, and test assertions are specified. Plan review should reject vague schema changes and require concrete pseudocode or diffs showing the field, validator logic, and test case together.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
