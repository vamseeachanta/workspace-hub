---
name: crossprovider gemini priority-ordered-keyword-regex-classification-fo
description: Priority-ordered keyword-regex classification for enums
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pattern-text-classification, enum-mapping, regex]
---

Map free-text descriptions to standardized enums using a list of (regex_pattern, enum_value) tuples with case-insensitive matching, evaluated in priority order (first match wins). Handles terminology variations robustly while ensuring consistent categorization across incident taxonomies.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
