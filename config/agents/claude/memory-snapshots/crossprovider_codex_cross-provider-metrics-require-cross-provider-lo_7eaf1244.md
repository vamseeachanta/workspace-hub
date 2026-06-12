---
name: crossprovider codex cross-provider-metrics-require-cross-provider-lo
description: Cross-provider metrics require cross-provider log sampling
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [metrics, cross-provider, scope]
---

Plans claiming health metrics across all providers (Claude, Codex, Gemini, Hermes) but sampling only one provider's logs are under-scoped. Must validate event schema for each provider or explicitly label metric as best-available coverage (e.g., 'Hermes logs only, last 15 days').

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
