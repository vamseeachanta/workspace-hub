---
name: crossprovider hermes freeform-string-redaction-misses-common-identifi
description: Freeform string redaction misses common identifier variants
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, hermes, redaction, telegram]
---

Telegram identifier redaction in #2720 only matches structured forms like `chat_id=...` and `allowlist=...`, missing semantic equivalents like `chat id -1009876543210` and `allowed_user_ids 12345,67890`. Leads to unredacted leakage in CLI/status/evidence outputs. Redaction must cover both structured (`key=value`) and unstructured (prose/freeform) forms, or fall back to manual/lossy approaches for safety-critical surfaces.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
