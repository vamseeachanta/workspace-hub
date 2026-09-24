---
name: crossprovider codex validation-must-live-in-the-dataclass-not-just-t
description: Validation must live in the dataclass, not just the loader
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation-design, python-dataclass, security]
---

Validation rules that live only in a loader/builder can be bypassed by direct dataclass construction. For audit and data classes, validation must be enforced in `__post_init__` or via a private constructor pattern, not assumed to happen upstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
