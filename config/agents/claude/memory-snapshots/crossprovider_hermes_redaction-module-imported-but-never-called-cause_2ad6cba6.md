---
name: crossprovider hermes redaction-module-imported-but-never-called-cause
description: Redaction module imported but never called causes Telegram PII leakage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [redaction-bypass, telegram-pii, safety-regression]
---

Readiness CLI imports `redact_status()` from redaction module but never uses it; instead calls `_redact_output()` which only filters secret-like keys, missing explicit Telegram fields (chat_id, allowlists, invite links, phone numbers). Remote evidence failures leak unredacted identifiers to logs/reports despite explicit redaction module existing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
