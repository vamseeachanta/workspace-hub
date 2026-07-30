---
name: crossprovider codex yaml-manifest-validation-must-reject-duplicate-k
description: YAML manifest validation must reject duplicate keys and validate exact types
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [yaml, schema-validation, security, manifest-parsing]
---

yaml.safe_load() silently accepts duplicate mapping keys (last-value-wins) and compares scalar types loosely (e.g., true == 1). Validation must use a SafeLoader subclass that rejects duplicate keys and type(x) checks for scalar constraints, not equality comparisons.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
