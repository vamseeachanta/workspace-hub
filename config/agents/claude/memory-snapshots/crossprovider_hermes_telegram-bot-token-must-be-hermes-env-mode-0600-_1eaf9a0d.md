---
name: crossprovider hermes telegram-bot-token-must-be-hermes-env-mode-0600-
description: Telegram bot token must be ~/.hermes/.env mode 0600 owner vamsee:vamsee, never expose
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [telegram, hermes, security, tokens]
---

Never paste, log, commit, or expose in chat/email. Back up to password manager separately. Readiness checks verify file presence, mode, and ownership; dispatch fails closed if missing or permissions wrong. Token hygiene is load-bearing for multi-machine security.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
