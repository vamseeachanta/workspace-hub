---
name: crossprovider gemini prefix-extraction-for-fuzzy-code-classification-
description: Prefix extraction for fuzzy code classification from noisy strings
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [parsing, data-cleaning, robustness]
---

For codes with embedded design annotations (e.g., 'SS F&G 9500'), extract first token via split()[0] for primary mapping lookup; fall back to full string if prefix unmaps. Decouples design metadata from type classification.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
