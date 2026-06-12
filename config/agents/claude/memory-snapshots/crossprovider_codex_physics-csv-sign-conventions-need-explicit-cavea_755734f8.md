---
name: crossprovider codex physics-csv-sign-conventions-need-explicit-cavea
description: Physics CSV sign conventions need explicit caveats in provenance
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [domain-specific, data-validation, documentation]
---

CSV columns with negative lever_arm while force is positive will produce flipped-sign yaw moments. This is often intentional cross-reference notation, not a bug. Requires explicit caveat in markdown report + provenance.json documenting the convention. Silent sign flip in unvetted data looks like a defect.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
