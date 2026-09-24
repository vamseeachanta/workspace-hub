---
name: crossprovider codex bash-string-interpolation-into-grep-e-risks-meta
description: Bash string interpolation into grep -E risks metacharacter injection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, regex, security]
---

Using `grep -E "...${var}..."` with variables can fail silently if var contains regex metacharacters like `()`, `.`, `+`, or `[]`. Fix: escape variables or use fixed patterns. Test with metacharacter-containing fixtures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
