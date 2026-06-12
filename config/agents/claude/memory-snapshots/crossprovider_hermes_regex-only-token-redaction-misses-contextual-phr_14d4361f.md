---
name: crossprovider hermes regex-only-token-redaction-misses-contextual-phr
description: Regex-only token redaction misses contextual phrases; context-aware patterns needed
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [redaction, token-fragments, pattern-coverage]
---

Redacting `bot token tail ZYXWV` or `token fragment ABCD` is hard with simple regex (risks matching legitimate words). Require adversarial test cases that verify both redaction coverage (no leakage) and false-positive rate (legitimate text preserved). Fallback: allowlist known token formats, deny contextual phrases only when high-confidence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
