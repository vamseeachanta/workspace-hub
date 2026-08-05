---
name: crossprovider codex fail-closed-defaults-for-synthesized-filled-data
description: Fail-closed defaults for synthesized/filled data
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [provenance, data-fills, defaults]
---

Data-filling converters (XLSX zero-fill, interpolation fallbacks) should default provenance to `unknown` rather than assuming input source. Synthetic/fabricated data must not inherit real-data provenance labels; conservative defaults prevent misattribution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
