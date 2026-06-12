---
name: crossprovider hermes review-stall-signatures-vary-by-provider-watch-f
description: Review stall signatures vary by provider; watch for known hangs before assuming productivity
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-dispatch, stall-recovery, monitoring]
---

Codex logs stuck at 'Reading additional input from stdin...', Gemini 429 RESOURCE_EXHAUSTED / capacity failures, Claude stream-json without --verbose, and sandbox bwrap failures are known stall signatures. Grep logs for these patterns before crediting lanes as productive. Appearance of output does not equal throughput.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
