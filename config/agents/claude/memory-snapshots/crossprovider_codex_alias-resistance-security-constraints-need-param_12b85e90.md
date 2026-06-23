---
name: crossprovider codex alias-resistance-security-constraints-need-param
description: Alias resistance: security constraints need parametrized exhaustive tests, not narrow field lists
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [security-testing, test-coverage, denylist-pattern]
---

Rejecting raw-source fields by name (e.g. source_body only) is bypassable via aliases (source_text, raw_source_text, source_content, source_excerpt, full_text, ocr_text, page_text). Use parametrized tests proving each variant fails before any write, and prefer pattern-based guards (e.g. reject keys matching `source|raw|pdf.*text|body|content|excerpt`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
