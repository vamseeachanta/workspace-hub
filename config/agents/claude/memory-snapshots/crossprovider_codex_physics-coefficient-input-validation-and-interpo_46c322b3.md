---
name: crossprovider codex physics-coefficient-input-validation-and-interpo
description: Physics-coefficient input validation and interpolation bounds enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [physics-modeling, input-validation, viv-fatigue, numerical-stability]
---

Interpolated physics coefficients (e.g., added-mass Ca(e/D)) must validate inputs against their stated interpolation domain and clamp outputs. Negative seabed gaps or other out-of-range inputs silently produce values outside stated ranges, causing model errors downstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
