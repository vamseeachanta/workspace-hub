---
name: crossprovider codex codex-weekly-rate-limits-available-in-local-sess
description: Codex weekly rate limits available in local session logs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [codex, tooling, quota-tracking]
---

Codex weekly usage percentage and reset time are in ~/.codex/sessions/*.jsonl under rate_limits.secondary. Local parsing is faster and more reliable than external APIs for agent-facing usage queries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
