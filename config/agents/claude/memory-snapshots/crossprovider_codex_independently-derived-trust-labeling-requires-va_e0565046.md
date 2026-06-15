---
name: crossprovider codex independently-derived-trust-labeling-requires-va
description: Independently-derived trust labeling requires validated inputs only
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [trust-labeling, engineering-vocabulary, metadata-correctness]
---

Mark calculated values as 'independently-derived' ONLY if produced from validated inputs (standard formulas, validated constants like pipe geometry + E=29e6 psi). Values recomputed from third-party unverified inputs (Roy/Chuck dimensions, assumed ODs, unverified areas) must stay 'third-party-unverified' with derivation_status: re-derived-arithmetic. This distinction affects engineering correctness, audit trails, and merge safety.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
