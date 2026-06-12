---
name: crossprovider codex regex-over-constraints-exact-case-extension-whit
description: Regex over-constraints (exact case, extension, whitespace) fail on valid input variants
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [regex-brittle, string-matching, case-sensitivity]
---

Regexes matching exact text like 'Technical Sheet' and `.pdf` (lowercase) fail on `.PDF` or `.pdf?download=1`. Use case-insensitive matching (re.IGNORECASE) and allow query parameters or variant extensions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
