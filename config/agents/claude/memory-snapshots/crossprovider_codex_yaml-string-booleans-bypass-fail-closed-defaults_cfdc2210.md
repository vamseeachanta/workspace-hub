---
name: crossprovider codex yaml-string-booleans-bypass-fail-closed-defaults
description: YAML string booleans bypass fail-closed defaults via truthiness
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [config-safety, boolean-coercion]
---

Python's truthiness coercion turns YAML `allow_default_density: "false"` into `True` when loaded without strict parsing. Scheduler passes the raw value to code that checks `if allow_default_density:`, undermining fail-closed behavior. **Tags**: boolean coercion, YAML loading, config safety

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
