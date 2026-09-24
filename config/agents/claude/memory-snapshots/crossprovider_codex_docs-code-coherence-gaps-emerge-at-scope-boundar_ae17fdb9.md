---
name: crossprovider codex docs-code-coherence-gaps-emerge-at-scope-boundar
description: Docs-code coherence gaps emerge at scope boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [coherence, documentation, code-review, verification]
---

When documentation changes scope (e.g., narrows report evidence to charts only), code may have overlapping logic that wasn't updated together. Coherence verification must check both documented claims AND actual executable behavior simultaneously; checking either alone misses gaps where one layer drifted.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
