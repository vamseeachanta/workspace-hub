---
name: crossprovider codex tests-with-zero-neutral-parameter-values-hide-de
description: Tests with zero/neutral parameter values hide defects in dependent calculations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, physics-modeling, verification]
---

Curvature friction tests with gravity=0 cannot detect sign errors in normal-force equations. Unit tests that set parameters to zero to isolate one code path can mask interactions with other parameters. Phase-invariant testing (comparing per-stage intermediate metrics, not just final results) is needed to detect which activation breaks what.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
