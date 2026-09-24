---
name: crossprovider codex npm-list-g-json-for-exact-package-lookup
description: npm list -g --json for exact package lookup
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [npm, version-extraction, json-parsing]
---

Use `npm list -g --json` and parse exact package keys from JSON dict rather than grepping output, to avoid substring ambiguity (e.g., `@anthropic-ai/claude-code` vs other `claude` packages). Falls back cleanly to empty string on missing packages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
