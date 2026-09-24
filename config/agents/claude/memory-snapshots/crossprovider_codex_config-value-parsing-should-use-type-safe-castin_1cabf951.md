---
name: crossprovider codex config-value-parsing-should-use-type-safe-castin
description: Config value parsing should use type-safe casting with fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, configuration, fail-closed]
---

Raw `int(config_value)` crashes during execution if the value is malformed. Use typed casting with fallback defaults and controlled error messages that fail at config-load time, not runtime.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
