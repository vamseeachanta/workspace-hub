---
name: crossprovider codex partial-fillage-br-detection-uses-wrong-physical
description: Partial-fillage BR detection uses wrong physical model
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [algorithm-correctness, physics-model-mismatch, partial-fillage]
---

Convex-hull BR selection finds envelope extremum (minimum load in right-position quartile), but physical BR on partial-fillage is a temporal load-drop event occurring mid-downstroke where plunger meets fluid. Algorithm returns 99.6% fillage vs vendor 54% because it selects position-based extremum instead of load-transition inflection. Vendor card validation confirms ≤1% error on near-full-fillage; ≥4% error on partial.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
