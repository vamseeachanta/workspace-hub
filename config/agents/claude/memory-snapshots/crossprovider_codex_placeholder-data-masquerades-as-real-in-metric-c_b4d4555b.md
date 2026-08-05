---
name: crossprovider codex placeholder-data-masquerades-as-real-in-metric-c
description: Placeholder data masquerades as real in metric comparisons
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [architecture, data-provenance, testing]
---

When unavailable or absent data is replaced with dummy values (e.g., identity matrices for missing coefficients), metrics compare them as perfect agreement instead of marking them unavailable. This hides the true data provenance. Requires explicit tracking of input source and refusal reason.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
