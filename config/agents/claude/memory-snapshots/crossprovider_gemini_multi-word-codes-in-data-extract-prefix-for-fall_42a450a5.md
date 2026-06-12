---
name: crossprovider gemini multi-word-codes-in-data-extract-prefix-for-fall
description: Multi-word codes in data: extract prefix for fallback mapping
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [data-parsing, legacy-data]
---

XLS/CSV vessel type codes leak design info ('SS F&G 9500', 'DS Gusto, MSC'). Parser must try full lookup, then extract prefix (split()[0]), then prefix lookup to prevent silent nulls.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
