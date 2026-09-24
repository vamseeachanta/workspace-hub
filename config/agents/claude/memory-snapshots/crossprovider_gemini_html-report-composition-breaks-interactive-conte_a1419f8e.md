---
name: crossprovider gemini html-report-composition-breaks-interactive-conte
description: HTML report composition breaks interactive content
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [html-composition, interactive-charts, report-generation]
---

Naively splitting HTML reports at `<body>` and discarding `<head>` sections strips all CSS and JavaScript dependencies. Plotly charts and other interactive elements become non-functional in merged reports. Collect all `<head>` sections separately, deduplicate/merge CSS and script tags, then recombine with merged body content.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
