---
name: crossprovider codex early-return-validation-breaks-fail-closed-error
description: Early-return validation breaks fail-closed error reporting
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [validation, error-handling]
---

When accumulating validation errors, early returns on malformed input (e.g., `if not isinstance(x, dict): return []`) skip subsequent checks instead of collecting all errors. Solution: validate field-by-field, append errors to a list, then return complete error set at end.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
