---
name: crossprovider hermes gateway-allow-all-users-is-a-safety-blocker-for-
description: GATEWAY_ALLOW_ALL_USERS is a safety blocker for Telegram/Hermes dispatch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram, security]
---

Setting `GATEWAY_ALLOW_ALL_USERS=true` in `~/.hermes/.env` blocks safe multi-machine dispatch. Must be false or unset before enabling Telegram bot control of any machine. This is checked by the readiness audit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
