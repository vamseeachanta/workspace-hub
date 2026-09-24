---
name: crossprovider gemini pchip-for-monotone-preserving-interpolation-in-h
description: PCHIP for monotone-preserving interpolation in hull geometry
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [numerical-methods, interpolation, hull-modeling]
---

Hull section profiles require non-negative half-breadths; cubic splines produce spurious oscillations and negative values near discontinuities (transom, chine). PCHIP (Piecewise Cubic Hermite) enforces monotonicity in monotone regions. Apply per-station before B-spline along-x interpolation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
