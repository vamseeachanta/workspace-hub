---
name: crossprovider hermes telegram-private-redaction-in-readiness-output-d
description: Telegram-private redaction in readiness output delegates weakly
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [redaction, telegram, dispatch-safety]
---

Readiness module uses `_redact_output()` for CLI output, which redacts secret-shaped tokens but does NOT redact Telegram-private metadata (chat_id, allowed_user_ids, invite links, phone numbers). Must delegate to `redact_status()` or strengthen `_redact_output()` to use Telegram-aware redaction path for all output/evidence rendering.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
