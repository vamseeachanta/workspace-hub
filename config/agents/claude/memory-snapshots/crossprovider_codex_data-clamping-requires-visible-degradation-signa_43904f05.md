---
name: crossprovider codex data-clamping-requires-visible-degradation-signa
description: Data clamping requires visible degradation signals, not just flags
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-quality, user-transparency, economic-calculations]
---

Flagging clamped/missing historical data as a boolean is insufficient for user-facing calculations (e.g., cost estimates, payback ratios). Economics comparisons using clamped rates need degraded-confidence framing and ratio suppression logic, not just a silent `clamped` flag in the underlying data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
