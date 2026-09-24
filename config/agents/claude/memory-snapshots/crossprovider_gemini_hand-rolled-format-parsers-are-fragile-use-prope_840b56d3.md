---
name: crossprovider gemini hand-rolled-format-parsers-are-fragile-use-prope
description: Hand-rolled format parsers are fragile — use proper libraries
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [parsing, data-structures, code-quality]
---

Custom YAML parsing assumes inline-list-only format or fixed key ordering. Standards-compliant block-list YAML breaks the parser. Use yq, yaml module, or equivalent libraries to handle all standard formats robustly without edge-case failures.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
