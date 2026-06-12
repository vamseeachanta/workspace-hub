---
name: crossprovider codex decomposition-plans-must-explicitly-assign-final
description: Decomposition plans must explicitly assign final success criterion
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [decomposition-planning, ownership-clarity]
---

Umbrella/decomposition plans cannot distribute the final success criterion across child issues or leave it implicit. Must explicitly name the single issue that owns the canonical final proof (e.g., #2469 owns exact `flake8 src/ ...` green on main for #2452 parent).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
