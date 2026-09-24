---
name: crossprovider gemini validate-structured-output-before-rendering-to-p
description: Validate structured output before rendering to prevent false-valid states
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-validation, error-handling, reliability]
---

When parsing external provider output, validate schema match before rendering to standard format. Preserve raw output on validation failure instead of silently defaulting. Prevents false-valid review states and maintains debuggability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
