---
name: crossprovider codex combined-field-factors-must-prevent-per-componen
description: Combined-field factors must prevent per-component aliases from resolving to the blend
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [registry-design, aliases, fail-closed-behavior]
---

When combining per-field API values via reserves-weighting, label explicitly as 'derived recoverable-reserves-weighted proxy'. Individual component aliases (e.g., 'Montanazo' alone) must not resolve to the combined factor in the loader; test both component and combined keys separately to catch alias-based fail-closed regressions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
