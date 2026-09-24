---
name: crossprovider gemini deterministic-routing-should-be-shell-not-llm
description: Deterministic routing should be shell, not LLM
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cost-optimization, shell-patterns, routing-logic]
---

When an event field determines routing (not requiring model judgment), use pure-shell case statements instead of calling APIs. Saves quota, reduces latency, improves reliability. Example: `classify.sh` should route signals by event type via `case`, not send to anthropic API.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
