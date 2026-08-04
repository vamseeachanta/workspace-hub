---
name: crossprovider codex multiple-solver-implementations-divergence-risk
description: Multiple solver implementations divergence risk
metadata:
  type: reference
  source: codex
  bridged: 2026-08-02
  tags: [data-quality, verification, client-work]
---

Two lazy-wave solvers in one repo (subsea/catenary_riser/ and marine_ops/marine_analysis/catenary/) with no verification of numerical agreement is a pre-client data-integrity hazard. Requires independent verification before any client-facing deliverable uses either one.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
