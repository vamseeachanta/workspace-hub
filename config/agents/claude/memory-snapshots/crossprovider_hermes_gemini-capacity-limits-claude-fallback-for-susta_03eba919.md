---
name: crossprovider hermes gemini-capacity-limits-claude-fallback-for-susta
description: Gemini capacity limits; Claude fallback for sustained batches
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-limits, model-routing, fallback-patterns]
---

Gemini via OpenRouter hits 429 (MODEL_CAPACITY_EXHAUSTED) or 402 (credit cap) under load. Local Gemini CLI with embedded context (no tools) is a fallback for reconnaissance. Claude remains more reliable for sustained review/planning batches; route batch work to Claude when Gemini capacity is exhausted.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
