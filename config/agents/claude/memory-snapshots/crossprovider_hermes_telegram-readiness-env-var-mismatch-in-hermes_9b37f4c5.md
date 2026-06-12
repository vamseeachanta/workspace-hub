---
name: crossprovider hermes telegram-readiness-env-var-mismatch-in-hermes
description: Telegram readiness env var mismatch in Hermes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram, configuration, readiness]
---

Hermes readiness script expects `TELEGRAM_HERMES_BOT_TOKEN` and `TELEGRAM_HERMES_ALLOWED_USER_IDS` but actual config stores `TELEGRAM_BOT_TOKEN` and `GATEWAY_ALLOW_ALL_USERS`. Bridge the naming mismatch in readiness checks or config to avoid false-negative readiness reports during multi-machine dispatch validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
