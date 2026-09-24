---
name: crossprovider gemini cost-capping-pattern-for-ai-experiment-spikes
description: Cost-capping pattern for AI experiment spikes
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cost-control, ai-eval, spike, budget]
---

Use environment variables (e.g., SPIKE_MAX_USD) to set budget caps on model evaluation runs; scripts abort if projected cost exceeds cap, preventing accidental expensive cloud API usage during experimentation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
