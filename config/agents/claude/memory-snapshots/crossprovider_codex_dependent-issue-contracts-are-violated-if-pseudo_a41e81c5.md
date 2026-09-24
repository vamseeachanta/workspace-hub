---
name: crossprovider codex dependent-issue-contracts-are-violated-if-pseudo
description: Dependent issue contracts are violated if pseudocode isn't cross-checked
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, pseudocode-verification, contract-violation]
---

When plan A depends on plan B's API (e.g., 'stage_dir=None means validate-only, no copy'), the pseudocode can silently violate B's contract by creating a dual copy path. Requires reading both plans' pseudocode and verifying compliance. A seam violation creates redundant or broken behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
