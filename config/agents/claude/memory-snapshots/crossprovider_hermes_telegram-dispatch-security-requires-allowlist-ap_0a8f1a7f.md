---
name: crossprovider hermes telegram-dispatch-security-requires-allowlist-ap
description: Telegram dispatch security requires allowlist + approval-mode enforcement
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [telegram, security, authorization, redaction]
---

TELEGRAM_HERMES_ALLOWED_USER_IDS must be populated; GATEWAY_ALLOW_ALL_USERS stays disabled; approvals.mode stays manual (not off); bot tokens must be redacted from logs and outputs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
