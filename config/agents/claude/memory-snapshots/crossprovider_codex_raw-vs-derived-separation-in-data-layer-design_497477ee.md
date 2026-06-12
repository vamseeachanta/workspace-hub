---
name: crossprovider codex raw-vs-derived-separation-in-data-layer-design
description: Raw-vs-derived separation in data layer design
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-design, schema, architecture]
---

When adding derived/normalized data (e.g. currency conversion, comparability adjustments), preserve original as-reported values unchanged in separate fields. Derivation should be additive and auditable, not destructive.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
