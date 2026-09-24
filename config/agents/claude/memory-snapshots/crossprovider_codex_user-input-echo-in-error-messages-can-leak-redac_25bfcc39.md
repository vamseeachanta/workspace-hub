---
name: crossprovider codex user-input-echo-in-error-messages-can-leak-redac
description: User input echo in error messages can leak redacted content
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, error-handling, input-validation]
---

Validation errors that emit raw user input (via f-strings with `!r` or `repr()`) can leak paths, tokens, or sensitive data the validation itself was meant to redact. Applies especially to user-supplied arguments; `_parse_blocked_by()` exceptions show raw input when validation fails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
