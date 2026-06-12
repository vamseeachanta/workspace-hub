---
name: crossprovider hermes hermes-multi-machine-dispatch-readiness-requires
description: Hermes multi-machine dispatch readiness requires TELEGRAM_HERMES_BOT_TOKEN and TELEGRAM_HERMES_ALLOWED_USER_IDS env vars
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram, multi-machine, readiness]
---

scripts/readiness/telegram-hermes-readiness.py validates env var presence, file permissions, dirty workspace state, and host evidence. Gateway running alone is insufficient; missing either env var fails readiness check and prevents dispatchable=true status.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
