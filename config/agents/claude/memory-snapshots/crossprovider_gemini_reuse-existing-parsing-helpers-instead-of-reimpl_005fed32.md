---
name: crossprovider gemini reuse-existing-parsing-helpers-instead-of-reimpl
description: Reuse existing parsing helpers instead of reimplementing grep/awk chains
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [code-reuse, parsing, bash, maintainability]
---

Fragile one-liners like `grep 'key:' | tr -d '"' | awk '{print $2}'` break on formatting variations (missing spaces, quotes). When the project provides a helper (e.g., `get_field`), use it. Saves debugging sessions on quote/spacing edge cases.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
