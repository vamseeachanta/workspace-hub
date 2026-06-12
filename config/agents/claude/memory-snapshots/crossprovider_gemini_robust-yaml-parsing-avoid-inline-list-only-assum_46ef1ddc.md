---
name: crossprovider gemini robust-yaml-parsing-avoid-inline-list-only-assum
description: Robust YAML parsing: avoid inline-list-only assumptions
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [yaml, parsing, robustness]
---

Children lists in frontmatter appear as inline `[A, B]` or block-list `- A\n- B`. Code that assumes one format breaks. Use proper YAML parser (yaml lib, yq) not ad-hoc regex. Python one-liner normaliser: parse both formats, return consistent list.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
