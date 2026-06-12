---
name: crossprovider hermes audit-markdown-reporting-must-mirror-json-findin
description: Audit Markdown reporting must mirror JSON findings structure
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit-reporting, markdown-consistency, operator-visibility]
---

Scheduled audit scripts can persist v2 findings in JSON output while Markdown renders only legacy findings, creating operator-facing inconsistency. Solution: extend `_write_markdown_artifact()` with dedicated v2 sections (grouping drift, content quality, size, usage) and update summary counts to include all families, not just legacy.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
