---
name: crossprovider codex fail-closed-validation-contract
description: Fail-closed validation contract
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [validation, error-handling, security]
---

Validators must return error lists on malformed input (nested dicts, non-object roots, wrong types), never crash with AttributeError or TypeError. This prevents security-gate bypasses where bad input silently passes as success.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
