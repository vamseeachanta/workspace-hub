---
name: crossprovider codex validation-must-be-fail-closed
description: Validation must be fail-closed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, correctness, error-handling]
---

New status checks must validate semantic consistency (matching top-level vs. nested values, numeric validity), not just field existence. Comparison operators silently accept NaN/inf/malformed inputs. Fail-closed means reject invalid state with reason, not avoid exceptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
