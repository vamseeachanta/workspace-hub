---
name: crossprovider gemini parser-test-fixtures-must-satisfy-parser-validat
description: Parser-test fixtures must satisfy parser validation rules
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, fixtures, test-coverage]
---

If a parser requires dates in filenames (`extract_date(file.name)`), test fixtures must include them. Fixtures that bypass validation hide test-production divergence.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
