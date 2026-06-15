---
name: crossprovider codex mooring-catenary-pretension-solver-doesn-t-prese
description: Mooring catenary pretension solver doesn't preserve input constraint
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [digitalmodel, orcaflex, mooring, testing]
---

digitalmodel mooring_design.py bisection returns top_tension materially different from requested pretension input. Tests only verify grounded_length > 0, missing the invariant that solver output must match constraint.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
