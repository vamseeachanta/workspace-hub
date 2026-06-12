---
name: crossprovider codex deterministic-routing-based-on-enum-fields-shoul
description: Deterministic routing based on enum fields should use shell case, not LLM
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [API-cost, patterns-compliance, deterministic-vs-learned]
---

Sending 50+ signal lines to Claude API nightly to classify by `event` field (which deterministically maps to action) violates patterns.md and wastes quota. Replace `call_anthropic_api()` with pure `case "$event" in ... esac` routing to stubs. LLM adds no value for deterministic routing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
