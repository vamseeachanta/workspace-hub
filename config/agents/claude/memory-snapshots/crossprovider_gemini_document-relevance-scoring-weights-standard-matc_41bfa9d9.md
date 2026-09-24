---
name: crossprovider gemini document-relevance-scoring-weights-standard-matc
description: Document relevance scoring weights standard match highest
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [search-ranking, relevance-scoring, information-retrieval]
---

When ranking documents by relevance to an engineering standard, weight the match as: standard/alias match = 3 pts, expanded form match = 2 pts, calc-file pattern = 2 pts, xlsx/spreadsheet type = 1 pt, domain match = 1 pt. This weighting prioritizes documents that explicitly reference the standard over file type hints.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
