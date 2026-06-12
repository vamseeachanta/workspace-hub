---
name: crossprovider hermes hermes-readiness-script-env-var-names-diverge-fr
description: Hermes readiness script env var names diverge from actual config
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram, env-var-naming, config-drift]
---

Readiness checker expects `TELEGRAM_HERMES_BOT_TOKEN` and `TELEGRAM_HERMES_ALLOWED_USER_IDS`, but `.hermes/.env` uses `TELEGRAM_BOT_TOKEN` and `GATEWAY_ALLOW_ALL_USERS=true`. Config drift causes silent dispatch failures despite valid credentials.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
