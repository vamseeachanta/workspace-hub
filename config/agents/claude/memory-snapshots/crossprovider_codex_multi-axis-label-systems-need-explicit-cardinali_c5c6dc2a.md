---
name: crossprovider codex multi-axis-label-systems-need-explicit-cardinali
description: Multi-axis label systems need explicit cardinality and precedence rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [labeling-systems, routing, correctness]
---

When multiple label axes coexist (lane:, agent:, ai:, model:), require explicit rules for: precedence order, ambiguous state handling (multiple labels on single axis), and whether absence means gap or default. Without cardinality tests, ambiguous states masquerade as healthy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
