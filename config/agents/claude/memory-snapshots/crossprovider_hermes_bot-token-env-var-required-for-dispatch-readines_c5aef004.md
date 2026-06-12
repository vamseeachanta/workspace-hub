---
name: crossprovider hermes bot-token-env-var-required-for-dispatch-readines
description: Bot token env var required for dispatch readiness
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, readiness, defaults]
---

Dispatch readiness must fail if TELEGRAM_HERMES_BOT_TOKEN env var is unset. Missing token is unsafe default and should not permit execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
