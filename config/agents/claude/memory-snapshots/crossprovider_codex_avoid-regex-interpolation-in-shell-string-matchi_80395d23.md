---
name: crossprovider codex avoid-regex-interpolation-in-shell-string-matchi
description: Avoid regex interpolation in shell string matching — hardcode safe patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-patterns, regex-safety, security]
---

Unescaped variables in `grep -E` patterns cause false positives/negatives if the variable contains regex metacharacters. For configuration-driven matching (e.g., section names, headings), either hardcode literal patterns or use non-regex matching that treats input as literal strings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
