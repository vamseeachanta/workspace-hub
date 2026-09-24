---
name: crossprovider codex simulate-vs-reference-validation-requires-both-s
description: Simulate-vs-reference validation requires both sign and magnitude checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, physics-simulation, regression-testing]
---

When comparing physical model outputs to regression/reference data, verify both sign convention (to catch rotation/frame-of-reference bugs) and magnitude ratios (by resolving them to known scaling factors like Cr, unit conversions, or integration schemes). Magnitude divergences that don't cleanly reduce to known factors suggest physics coupling bugs rather than just notation differences.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
