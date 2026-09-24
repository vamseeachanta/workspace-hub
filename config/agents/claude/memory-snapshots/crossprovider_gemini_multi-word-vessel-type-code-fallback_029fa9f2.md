---
name: crossprovider gemini multi-word-vessel-type-code-fallback
description: Multi-word vessel type code fallback
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-cleaning, parser-pattern, xls-ingest]
---

When vessel type strings contain embedded design data (e.g., 'SS F&G 9500'), split on whitespace and use the first token as fallback key for mapping. Handles noisy XLS scraper output.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
