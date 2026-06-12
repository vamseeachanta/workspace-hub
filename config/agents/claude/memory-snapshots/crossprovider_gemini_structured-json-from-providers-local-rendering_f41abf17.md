---
name: crossprovider gemini structured-json-from-providers-local-rendering
description: Structured JSON from providers + local rendering
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [provider-interop, reliability, review-transport]
---

Request provider-specific structured JSON output (via --json-schema and --output-format json), then parse and render locally to standard schema using render-structured-review.py. More reliable than expecting providers to output final format directly. Pattern in WRK-640.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
