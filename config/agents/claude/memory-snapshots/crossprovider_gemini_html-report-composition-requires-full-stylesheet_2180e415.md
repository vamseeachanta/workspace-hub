---
name: crossprovider gemini html-report-composition-requires-full-stylesheet
description: HTML report composition requires full stylesheet/script preservation
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [html-composition, report-generation]
---

Combining HTML reports from multiple engines via `split('<body>')` discards the `<head>` section, losing all embedded CSS and JavaScript libraries (e.g., Plotly). Charts become non-interactive and styling is lost. Preserve stylesheets by merging `<style>` blocks or use iframe sandboxing instead.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
