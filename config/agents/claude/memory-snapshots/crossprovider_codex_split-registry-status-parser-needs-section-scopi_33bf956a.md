---
name: crossprovider codex split-registry-status-parser-needs-section-scopi
description: Split-registry status parser needs section scoping
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [parsing, validation, markdown]
---

Markdown table parsers that scan 'every table line containing an issue link' can match the wrong table if not section-scoped. Status precedence checks must target the Wave 0 Split Registry table explicitly, not rely on content order to prevent accidental matches in other tables.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
