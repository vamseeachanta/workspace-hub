---
name: crossprovider codex pattern-match-validation-gates-miss-case-variant
description: Pattern-match validation gates miss case variants and URI families
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [validation, regex-gates, security, completeness]
---

A gate claiming "zero network dependencies" by checking only lowercase `<script`, `http`, `@import` will miss `<SCRIPT>`, `<LINK>`, `<IFRAME>`, `<OBJECT>`, meta refresh, and uppercase `URL(...)`. Any regex-based security or network-isolation gate must be case-insensitive and enumerate all vector families (script, link, img, iframe, object, meta-refresh, url-css, data-uri). Incomplete patterns create false confidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
