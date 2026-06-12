---
name: crossprovider codex edition-divergence-requires-enum-based-routing-n
description: Edition divergence requires enum-based routing, not numeric-field defaults
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [standards, multi-version, routing, safety-factors, digitalmodel]
---

Multiple standards editions (DNV-RP-B401 2017/2021, API, ASTM, ISO) have incompatible splash-zone constants (0.0 vs 0.1/0.20 A/m²), anode ratios (McCoy ~1.8702 vs Dwight, geometry-dependent), and coating schemas (9 vs 4 categories). Use enum routing (MooringCondition strings) + dict lookup rather than single float defaults to bind numeric to edition without silent divergence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
