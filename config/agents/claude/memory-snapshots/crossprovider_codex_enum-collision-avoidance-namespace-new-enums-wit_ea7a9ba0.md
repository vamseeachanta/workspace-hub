---
name: crossprovider codex enum-collision-avoidance-namespace-new-enums-wit
description: Enum collision avoidance: namespace new enums with standards-derived prefix (F106CoatingType, not CoatingType)
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-design, naming, collision, backwards-compat]
---

When adding standards-specific enums to a codebase with existing domain enums (fuel-system CoatingType), use a prefixed namespace (F106CoatingType). Re-export with F106* aliases from the package level to avoid name clashes and make origin clear to callers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
