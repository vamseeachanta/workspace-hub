---
name: crossprovider codex generated-index-validation-needs-row-level-cross
description: Generated index validation needs row-level cross-check beyond --check
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [validation, index-building, batch-review]
---

`build_document_index.py --check` verifies CSV syntax and consistency but not scope—it regenerates the full index. Approval requires explicit row-by-row verification: for each changed queue row, confirm the corresponding index row exists with matching values. Off-by-one or count mismatches often hide in script output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
