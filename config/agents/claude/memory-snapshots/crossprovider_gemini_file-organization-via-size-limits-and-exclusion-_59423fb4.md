---
name: crossprovider gemini file-organization-via-size-limits-and-exclusion-
description: File organization via size limits and exclusion categories
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [code-quality, architecture, maintainability]
---

Use 400-line hard limit and 200-line soft target for file complexity; categorize exclusions (legacy, data, reference, generated, ops) to distinguish refactoring candidates from acceptable exceptions. Helps identify which large files are organizational debt vs. legitimate single-purpose modules.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
