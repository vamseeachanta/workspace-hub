---
name: crossprovider gemini column-name-flexibility-via-candidate-lists
description: Column name flexibility via candidate lists
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-ingestion, column-mapping, flexibility]
---

Handle multiple naming conventions in tabular data by maintaining candidate lists for each semantic column (e.g., _OIL_VOL_CANDIDATES = ['MON_O_PROD_VOL', 'OIL_STB']). Implement a _pick_col(df, candidates) helper that returns the first matching column or None. This increases portability across data sources.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
