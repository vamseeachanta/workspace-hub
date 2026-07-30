---
name: crossprovider codex config-schema-names-must-match-exactly-between-p
description: Config schema names must match exactly between plan and code
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [config, schema, plan-review]
---

Plan specifying `density_registry_path` while implementation uses `oil_density_registry_path` breaks consumer code and is easy to miss. Require config schema tests that verify plan-specified keys exist and match the actual code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
