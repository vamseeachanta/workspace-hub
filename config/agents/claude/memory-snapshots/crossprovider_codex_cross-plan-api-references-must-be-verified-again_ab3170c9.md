---
name: crossprovider codex cross-plan-api-references-must-be-verified-again
description: Cross-plan API references must be verified against pseudocode, not assumed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, interdependency, api-contract, verification]
---

When plan A references APIs from plan B (e.g., resolver hooks, field additions), verify plan B's pseudocode and TDD actually define those APIs with matching signatures. Multiple reviews caught invented hooks and fields that dependent plans assumed but upstream plans never specified, leading to unimplementable designs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
