---
name: crossprovider codex non-finite-edge-cases-require-systematic-validat
description: Non-finite edge cases require systematic validation at entry points
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, numerics, edge-cases]
---

NaN, Inf, and overflow-to-infinity cases must be rejected at function entry (e.g., load_datum, profile angles, vendor metadata). Allowing them through internal checks masks errors in callers and produces plausible-looking wrong results.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
