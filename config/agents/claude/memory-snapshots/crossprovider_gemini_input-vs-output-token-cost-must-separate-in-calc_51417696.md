---
name: crossprovider gemini input-vs-output-token-cost-must-separate-in-calc
description: Input vs output token cost must separate in calculations
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [pricing, tokens, cost-tracking]
---

LLM APIs charge different rates for input (prompt) tokens vs output (completion) tokens. Pricing table must store input_per_1m and output_per_1m separately. Cost = (input_tokens / 1M) × input_rate + (output_tokens / 1M) × output_rate. Single unified rate incorrect.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
