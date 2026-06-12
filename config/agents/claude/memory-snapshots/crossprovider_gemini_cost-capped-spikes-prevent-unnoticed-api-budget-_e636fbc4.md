---
name: crossprovider gemini cost-capped-spikes-prevent-unnoticed-api-budget-
description: Cost-capped spikes prevent unnoticed API budget overruns
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cost-control, spikes, api-budget]
---

Exploration loops trying multiple LLM models or large corpus samples can rack up $100+ in API costs without oversight. Solution: set hard cost cap via env var (e.g., `SPIKE_MAX_USD=5`) and abort if projected cost exceeds it. Forces deliberate sampling and makes cost tradeoffs visible. Pattern from #2403 embeddings spike that generalizes to any external-API exploration.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
