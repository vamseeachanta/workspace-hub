---
name: crossprovider gemini eliminate-llm-invocation-for-deterministic-routi
description: Eliminate LLM invocation for deterministic routing
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [llm-orchestration, cost-optimization, cron-jobs]
---

Replacing `claude --skill` with direct script call when logic is purely deterministic (event-based routing via `case` statement, format conversion, filtering) eliminates quota spend and session overhead. LLM adds no value when event field + fixed schema suffice; reserve LLM for judgment tasks.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
