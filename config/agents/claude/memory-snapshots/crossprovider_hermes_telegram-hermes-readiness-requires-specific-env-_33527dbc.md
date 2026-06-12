---
name: crossprovider hermes telegram-hermes-readiness-requires-specific-env-
description: Telegram-Hermes readiness requires specific env vars in .hermes/.env
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram, token-hygiene, readiness-gate]
---

Multi-machine dispatch readiness fails when `TELEGRAM_HERMES_ALLOWED_USER_IDS` or `TELEGRAM_HERMES_BOT_TOKEN` are missing from `~/.hermes/.env` (mode 600, owner vamsee:vamsee). Token hygiene setup alone is insufficient; readiness-specific variables must be populated and redacted during validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
