---
name: crossprovider gemini code-fence-stripping-required-before-pattern-mat
description: Code-fence stripping required before pattern matching in validators
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [validator-robustness, regex-patterns, markdown-handling]
---

Markdown code blocks containing WRK-IDs or keywords (e.g., ````# WRK-123`````) cause false positives in validators. Apply regex `r"```[^\n]*\n.*?```"` with `re.DOTALL` to strip before searching for WRK references or confirmation keywords.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
