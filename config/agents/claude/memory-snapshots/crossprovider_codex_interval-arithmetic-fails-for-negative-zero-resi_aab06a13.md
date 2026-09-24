---
name: crossprovider codex interval-arithmetic-fails-for-negative-zero-resi
description: Interval arithmetic fails for negative/zero residuals
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [algorithm, math, cost-analysis]
---

The formula `[Rlo/Thi, Rhi/Tlo]` is invalid when residuals cross zero. For `T=[100,200]`, `R=[-200,-50]`, actual range is `[-2,-0.25]` but naive formula produces `[-1,-0.5]`. Case analysis required; materializes in cost overrun calculations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
