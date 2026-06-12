---
name: crossprovider hermes hermes-multi-machine-dispatch-string-level-redac
description: Hermes multi-machine dispatch: string-level redaction gaps leak Telegram identifiers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram-dispatch, security, redaction]
---

Redaction in `scripts/telegram_dispatch/redaction.py` only scrubs token/API-key patterns at string level; freeform status messages containing `chat_id`, allowlist values, invite links, or phone numbers are passed through unredacted. Pattern-matching token/env patterns is insufficient—must also scrub Telegram-private values anywhere they appear in arbitrary strings.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
