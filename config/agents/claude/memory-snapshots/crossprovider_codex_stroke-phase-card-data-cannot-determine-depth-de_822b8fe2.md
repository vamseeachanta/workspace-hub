---
name: crossprovider codex stroke-phase-card-data-cannot-determine-depth-de
description: Stroke-phase card data cannot determine depth-dependent properties
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [cardanalysis, modeling-constraints, survey-data]
---

Current rod-buckling code intentionally avoids deriving neutral-point depth or compression length from pump cards because card sample indices represent stroke phase, not well depth. Attempting to invert this (e.g., via Poisson corrections or assumed rod geometry) reintroduces the defect fixed in issue #1871. Depth-dependent calculations require explicit inclination/survey profiles; this should remain an API boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
