---
name: crossprovider codex domain-algorithms-must-model-physics-not-just-en
description: Domain algorithms must model physics, not just envelope properties
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [algorithms, physics-modeling, dynacard, artificial-lift]
---

The bottom-right corner detector uses convex hull + position percentile to find a minimum-load vertex, but this finds an envelope extremum, not the physical fluid-transfer event on partial-fillage cards. The algorithm returns 99.6% fillage where vendors measure 54%, even on the vendor's own card. Temporal load-drop detection is the correct primary rule; fallback methods should not bypass domain semantics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
