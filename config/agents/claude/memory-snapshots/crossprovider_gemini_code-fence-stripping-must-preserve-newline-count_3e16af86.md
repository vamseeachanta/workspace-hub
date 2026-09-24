---
name: crossprovider gemini code-fence-stripping-must-preserve-newline-count
description: Code fence stripping must preserve newline count for accurate line numbers
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [python, regex, parsing, line-numbers, verified-bug]
---

When extracting prose patterns or other line-number-aware processing, stripping code fences via `re.sub(..., '', text)` deletes all newlines in the block, corrupting subsequent line number assignments. Fix: preserve newline count with `lambda m: '\n' * m.group(0).count('\n')` so line mapping stays accurate.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
