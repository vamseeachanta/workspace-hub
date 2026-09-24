---
name: crossprovider gemini three-state-result-enums-prevent-silent-fallback
description: Three-state result enums prevent silent fallback logic
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-modeling, correctness, ambiguity-handling]
---

Use three canonical states (LINKED, UNLINKED, AMBIGUOUS) instead of two-state enums to prevent helpers from silently picking one candidate when multiple exact matches exist. Ambiguous status forces caller to handle the case explicitly.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
