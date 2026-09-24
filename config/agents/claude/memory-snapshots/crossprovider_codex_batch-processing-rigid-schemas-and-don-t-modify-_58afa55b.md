---
name: crossprovider codex batch-processing-rigid-schemas-and-don-t-modify-
description: Batch processing rigid schemas and 'don't modify' constraints are incompatible
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [batch-processing, schema-contracts, scope-definition]
---

Plans that require new YAML input support but say 'don't modify the batch runner' create unsolvable scope. Rigid schema and no-modify are mutually exclusive. Plans must either expand scope to modify that component or define a wrapper/adapter that translates outside the rigid boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
