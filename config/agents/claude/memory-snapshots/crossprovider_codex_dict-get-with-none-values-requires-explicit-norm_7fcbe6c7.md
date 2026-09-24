---
name: crossprovider codex dict-get-with-none-values-requires-explicit-norm
description: Dict.get() with None values requires explicit normalization
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python-pitfall, null-handling, data-validation]
---

When a dictionary key exists with null/None value, dict.get(key, default) returns None rather than the default—the key's presence suppresses the default. Use explicit if value is None: value = default_value normalization instead. This is especially problematic when None must be converted to a required numeric type.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
