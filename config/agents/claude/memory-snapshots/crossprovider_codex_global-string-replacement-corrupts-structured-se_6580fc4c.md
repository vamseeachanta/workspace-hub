---
name: crossprovider codex global-string-replacement-corrupts-structured-se
description: Global string replacement corrupts structured semantic values
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [data-mutation, sanitization, structured-data]
---

Blanket regex/keyword replacement across all output strings (e.g., replacing 'authority|auth' everywhere) will corrupt enum/status fields containing those substrings. Example: 'public-domain-risk-authority-check' becomes 'public-domain-risk-check', breaking downstream parsing. Pattern: sanitize structured data field-by-field with domain knowledge, never globally.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
