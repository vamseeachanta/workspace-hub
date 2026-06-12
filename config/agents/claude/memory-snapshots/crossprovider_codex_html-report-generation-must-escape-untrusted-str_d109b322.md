---
name: crossprovider codex html-report-generation-must-escape-untrusted-str
description: HTML report generation must escape untrusted strings consistently
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security, xss, html-output]
---

Sessions 17–18 found stored XSS vulnerabilities in multiple reports (Buckskin, forecasting) where dataset field values (well names, API numbers, activity codes) were interpolated directly into HTML without escaping. Use `html.escape()` or switch to a templating engine with auto-escaping.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
