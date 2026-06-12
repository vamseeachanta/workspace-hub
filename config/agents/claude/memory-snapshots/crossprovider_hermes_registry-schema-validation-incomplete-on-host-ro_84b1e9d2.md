---
name: crossprovider hermes registry-schema-validation-incomplete-on-host-ro
description: Registry schema validation incomplete on host/root consistency
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, schema, contracts]
---

Schema contracts validate presence but not consistency between `repo_root`, `workspace_root`, and hostname scope. Mismatched hostname can silently produce wrong paths. Add cross-field validator in schema contract tests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
