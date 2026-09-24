---
name: crossprovider codex fixture-token-grammars-need-parse-context-limits
description: Fixture token grammars need parse-context limits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [fixtures, token-generation, placeholder-safety]
---

Design fixture grammars with context-limited request markers (e.g., JSON values like {"public_source_token_request": {...}}), not concrete tokens. Prevent placeholder shape from making private-field keys "acceptable" in public artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
