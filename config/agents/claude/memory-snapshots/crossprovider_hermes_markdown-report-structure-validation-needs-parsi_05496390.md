---
name: crossprovider hermes markdown-report-structure-validation-needs-parsi
description: Markdown report structure validation needs parsing, not substring search
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [markdown, report-validation, parsing]
---

Reports with structured content (markdown sections, code-block lists, nested data) require section-aware parsing and code-block value extraction via regex, not substring matching. Validation must understand the markdown structure to reliably extract and validate sections like `##` headings and `` `value` `` lists.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
