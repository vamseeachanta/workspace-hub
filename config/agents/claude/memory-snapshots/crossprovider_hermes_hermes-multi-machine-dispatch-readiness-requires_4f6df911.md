---
name: crossprovider hermes hermes-multi-machine-dispatch-readiness-requires
description: Hermes multi-machine dispatch readiness requires allowlist + clean state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram, readiness, multi-machine]
---

Multi-machine Telegram-Hermes dispatch fails closed on missing `TELEGRAM_HERMES_BOT_TOKEN` or `TELEGRAM_HERMES_ALLOWED_USER_IDS` env vars, uncommitted git changes, or missing remote host evidence. Service-running check alone is insufficient; `scripts/readiness/telegram-hermes-readiness.sh` enforces all three gates.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
