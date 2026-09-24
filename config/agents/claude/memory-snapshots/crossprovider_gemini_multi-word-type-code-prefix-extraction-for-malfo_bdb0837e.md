---
name: crossprovider gemini multi-word-type-code-prefix-extraction-for-malfo
description: Multi-word type code prefix extraction for malformed structured data
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-cleaning, parsing, robustness, malformed-input]
---

Data sources often leak design details into type fields (e.g., 'SS F&G 9500', 'DS Gusto, MSC Bully PRD'). Extract the first word as a fallback for type mapping when exact match fails. Handles common data quality issues without maintaining per-variant parsing rules.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
