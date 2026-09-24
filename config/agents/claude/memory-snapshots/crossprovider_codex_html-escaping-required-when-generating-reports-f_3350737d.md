---
name: crossprovider codex html-escaping-required-when-generating-reports-f
description: HTML escaping required when generating reports from dataset values
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, html-generation, xss, report-generation]
---

Generated HTML reports that interpolate dataset values (timestamps, product names, rig names, block numbers) without HTML escaping create XSS vulnerabilities. Use `html.escape()` or a templating engine with auto-escaping before inserting any untrusted string into HTML.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
