---
name: crossprovider codex html-sanitization-in-generated-reports
description: HTML sanitization in generated reports
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, html-generation]
---

Defensive regex-based removal of script tags, event handlers (on*= attributes), and javascript: URLs when markdown renders to HTML for browser display. Prevents XSS in artifacts opened directly in browser.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
