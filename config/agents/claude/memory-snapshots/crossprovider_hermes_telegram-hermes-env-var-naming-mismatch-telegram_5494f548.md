---
name: crossprovider hermes telegram-hermes-env-var-naming-mismatch-telegram
description: Telegram-Hermes env var naming mismatch: TELEGRAM_BOT_TOKEN vs TELEGRAM_HERMES_BOT_TOKEN
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram, env-vars, naming-mismatch]
---

Readiness script expects TELEGRAM_HERMES_BOT_TOKEN and TELEGRAM_HERMES_ALLOWED_USER_IDS, but ~/.hermes/.env contains TELEGRAM_BOT_TOKEN. Requires aliasing in readiness check or documentation clarifying the naming boundary between generic Telegram setup and Hermes-specific readiness.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
