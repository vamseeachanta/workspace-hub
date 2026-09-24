---
name: crossprovider gemini fragile-regex-ordering-for-overlapping-identifie
description: Fragile regex ordering for overlapping identifiers — use anchoring
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pattern-matching, regex, edge-cases]
---

Detecting code families via regex order (BS before ISO to avoid ISO matching BS_EN_ISO_*.pdf) fails as patterns grow. Use word boundaries (\b), prefix matching, or explicit alternation order in regex to handle overlaps robustly.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
