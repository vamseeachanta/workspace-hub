---
name: crossprovider codex web-scraper-regex-patterns-silently-drop-valid-d
description: Web scraper regex patterns silently drop valid data when format varies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [regex, web-scraping, brittleness]
---

Regex patterns designed to parse real-world web content often fail silently on format variations (case sensitivity, token-count mismatch, delimiter variants). Patterns should be case-insensitive, use character classes for delimiters, and include fallback matching for common variants to avoid silently dropping valid rows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
