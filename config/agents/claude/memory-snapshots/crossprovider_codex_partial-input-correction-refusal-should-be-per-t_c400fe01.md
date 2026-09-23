---
name: crossprovider codex partial-input-correction-refusal-should-be-per-t
description: Partial-input correction refusal should be per-term, not all-or-nothing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [correction-semantics, api-design, partial-results]
---

When a multi-part correction has missing inputs, compute independent sub-terms anyway; don't suppress one correction just because another part is missing. Patterson slippage should compute even if formation-volume-factor is absent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
