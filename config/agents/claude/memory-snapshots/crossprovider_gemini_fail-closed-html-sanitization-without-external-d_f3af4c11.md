---
name: crossprovider gemini fail-closed-html-sanitization-without-external-d
description: Fail-closed HTML sanitization without external dependencies
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [security, html-rendering, dependencies, browser-safety]
---

HTML generation for browser-rendered reports is evolving toward self-contained sanitization (regex + escape) rather than bleach-reliant, with explicit fallbacks when dependencies unavailable (render error message or escaped text). Reflects tension between defense-in-depth and deployment simplicity.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
