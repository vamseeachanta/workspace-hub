---
name: crossprovider codex monetary-unit-semantics-musd-vs-mm-vs-usd-create
description: Monetary unit semantics (MUSD vs MM vs USD) create 1000x correctness risks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monetary-calculations, unit-clarity, correctness-critical]
---

Inconsistent naming or handling of monetary units (thousand USD, million USD, plain dollars) across pseudocode, tests, and implementations can silently produce cost/revenue figures off by orders of magnitude. Unit normalization and explicit test fixtures with known outputs are load-bearing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
