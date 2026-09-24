---
name: crossprovider codex environment-variable-validation-must-normalize-w
description: Environment variable validation must normalize whitespace and quotes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [env-vars, security, validation, bug-pattern]
---

Boolean env vars like `GATEWAY_ALLOW_ALL_USERS` can bypass checks if not normalized. The verifier strips leading/trailing whitespace and quotes, then compares lowercase value against known falsy set (false/0/no/off/disabled). Whitespace-padded or quoted truthy values (`" yes "`) will pass unmodified checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
