---
name: crossprovider hermes remote-host-readiness-must-explicitly-validate-a
description: Remote host readiness must explicitly validate all OS types
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch, readiness, semantic-gap, fail-closed]
---

Telegram dispatch readiness check skipped validation for non-Linux remote hosts entirely. Readiness must fail closed for ALL host types when dispatch criteria unmet, not conditionally based on OS.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
