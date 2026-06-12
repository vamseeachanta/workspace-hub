---
name: crossprovider gemini xls-malformed-vessel-type-handling-via-prefix-ex
description: XLS malformed vessel type handling via prefix extraction
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [xls-parser, data-cleaning, workaround]
---

XLS scrapes leak design info into vessel type field (e.g. "SS F&G 9500", "DS Gusto, MSC Bully PRD"). Extract first token as prefix and map that ("SS" → semi_submersible). Fallback to full string if prefix fails.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
