---
name: crossprovider codex validators-crash-on-malformed-input-instead-of-f
description: Validators crash on malformed input instead of fail-closed error returns
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [error-handling, robustness, validator-api]
---

Validators that assume well-formed JSON structure (non-null objects, present keys) throw AttributeError/KeyError on malformed input instead of returning structured errors. Wrap entry points with try-catch and return validator-native error objects for all edge cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
