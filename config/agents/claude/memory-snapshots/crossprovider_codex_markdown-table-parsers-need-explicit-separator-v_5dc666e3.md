---
name: crossprovider codex markdown-table-parsers-need-explicit-separator-v
description: Markdown table parsers need explicit separator validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, parsing, technical-debt]
---

Regex-based table parsers that skip separator rows without validation and split blindly on pipe characters are fragile. Future content with escaped pipes or malformed tables will silently evade validation rules. Add explicit separator-row matching and proper escape-character handling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
