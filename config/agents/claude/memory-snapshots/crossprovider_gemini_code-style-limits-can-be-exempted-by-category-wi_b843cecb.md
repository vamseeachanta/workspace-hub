---
name: crossprovider gemini code-style-limits-can-be-exempted-by-category-wi
description: Code style limits can be exempted by category with justification
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [code-style, large-files, WRK-090]
---

400-line hard limit on code files can be exempted via category in exclusion config: legacy (frozen code), data (taxonomy/constants), reference (standards implementations), generated, ops (infrequent scripts). Requires explicit reason; enables large-scale audits without refactoring critical-path files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
