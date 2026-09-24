---
name: crossprovider gemini whole-word-grep-misses-symbols-with-punctuation-
description: Whole-word grep misses symbols with punctuation in documentation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [regex, symbol-matching, documentation, edge-cases]
---

The regex `\b` word-boundary anchor stops at punctuation, so it will not match `Class.method()` or `function_name()` as written in documentation. Symbol matching for drift detection needs to account for how symbols are formatted in docs (backticks, parentheses, namespace separators).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
