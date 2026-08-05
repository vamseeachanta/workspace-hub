---
name: crossprovider codex non-finite-values-leak-as-json-nan-instead-of-nu
description: Non-finite values leak as JSON NaN instead of null if not classified unavailable
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [json-serialization, numerics, data-quality, edge-cases]
---

NaN or Inf response data that is not explicitly classified as unavailable propagates into statistics and serializes as non-standard JSON `NaN` instead of `null`. Always check for non-finite values early and classify them as unavailable before they reach aggregation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
