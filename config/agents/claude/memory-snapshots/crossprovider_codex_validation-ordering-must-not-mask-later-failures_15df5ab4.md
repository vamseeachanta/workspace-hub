---
name: crossprovider codex validation-ordering-must-not-mask-later-failures
description: Validation ordering must not mask later failures with earlier denials
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [validation-ordering, privacy-gates, regression-testing]
---

When a batch system validates multiple rows/targets sequentially, a missing required input (e.g., HMAC key) early in the loop must not prevent detection of validation failures in later rows (e.g., corrupt markers, untracked targets). Testing must verify both: missing-key case fails early, AND that same missing-key case surfaces later-row failures when key is present. This applies to any gated multi-row operation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
