---
name: crossprovider codex python-bool-int-validation-hazard
description: Python bool/int validation hazard
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, python, correctness]
---

When validating numeric fields with `isinstance(value, int)`, remember that `bool` is a subclass of `int` in Python, so `True`/`False` will pass `int` checks and may route to wrong branches. Use explicit `isinstance(value, int) and not isinstance(value, bool)` or strict type checking for correctness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
