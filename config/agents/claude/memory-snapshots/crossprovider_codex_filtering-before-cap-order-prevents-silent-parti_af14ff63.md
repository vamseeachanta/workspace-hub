---
name: crossprovider codex filtering-before-cap-order-prevents-silent-parti
description: Filtering-before-cap order prevents silent partial collection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [correctness, filtering, fail-closed, scope]
---

When bounded work lists apply both cap limits and filtering, apply filters BEFORE the cap, not after. Filtering after cap silently drops work outside the capped range while reporting success (`complete: true`), violating fail-closed semantics. Applies to any queue/list collection system with scope constraints.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
