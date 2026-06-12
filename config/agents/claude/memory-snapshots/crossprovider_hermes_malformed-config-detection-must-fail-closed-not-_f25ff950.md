---
name: crossprovider hermes malformed-config-detection-must-fail-closed-not-
description: Malformed config detection must fail-closed, not default-safe
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [config-validation, defensive, fail-closed]
---

llm-wiki #88 review found that validators silently dropped invalid route entries or defaulted missing fields, weakening detection of broken configs. Instead, validators should reject malformed entries explicitly; defaults hide problems rather than solving them.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
