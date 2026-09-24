---
name: crossprovider codex deterministic-signal-routing-doesn-t-need-llm-pu
description: Deterministic signal routing doesn't need LLM; pure shell case statements save cost and complexity
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cost-efficiency, architectural-patterns, automation]
---

When signal classification is entirely deterministic (field-based routing: `event == X → sink Y`), invoking an LLM to make the routing decision adds cost and quota consumption with zero value. A shell `case` statement on the event field is correct. Discovered in WRK-1102: `call_anthropic_api()` in classify.sh sent nightly signal batches to Anthropic for event-based routing that could be done in pure shell, violating patterns.md: 'scripts > LLM judgment'.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
