---
name: crossprovider codex truthiness-based-boolean-configuration-inverts-s
description: Truthiness-based boolean configuration inverts safety defaults
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [config-parsing, safety-defaults, boolean-logic]
---

When `allow_default_density` or similar opt-in flags are evaluated via Python truthiness (e.g., `if caller_input:`) rather than strict boolean parsing, string values like `"false"` become truthy and flip the default from fail-closed to permissive. YAML/env config must use explicit boolean coercion, not truthiness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
