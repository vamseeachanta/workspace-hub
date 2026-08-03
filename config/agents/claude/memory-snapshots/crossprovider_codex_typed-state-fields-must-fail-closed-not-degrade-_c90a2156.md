---
name: crossprovider codex typed-state-fields-must-fail-closed-not-degrade-
description: Typed state fields must fail-closed, not degrade to unknown on cast failure
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [state-validation, fail-closed, error-classification]
---

Runtime state JSON that fails type validation (int field with string value, missing enum field) should reject as `invalid_state`, not attempt unsafe casts that produce KeyError/ValueError/TypeError. Those exceptions then degrade to `unknown` health status, letting spoofed/corrupted state bypass the status contract. All typed fields must be validated before use.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
