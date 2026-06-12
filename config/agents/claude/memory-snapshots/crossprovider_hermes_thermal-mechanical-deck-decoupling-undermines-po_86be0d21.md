---
name: crossprovider hermes thermal-mechanical-deck-decoupling-undermines-po
description: Thermal/mechanical deck decoupling undermines portfolio FEM benchmarks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [fem-design, portfolio-risk, solver-coupling]
---

Presenting solver decks that apply different load paths (thermal: DFLUX power; mechanical: fixed 85C boundary) but claim coupled physics is materially weaker than actual coupled results. #2511 iterations showed power-based analytical profiles disconnected from solver output—acceptable only if report explicitly documents this limitation, not as a benchmark.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
