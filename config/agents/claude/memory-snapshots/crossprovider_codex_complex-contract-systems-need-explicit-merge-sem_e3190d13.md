---
name: crossprovider codex complex-contract-systems-need-explicit-merge-sem
description: Complex contract systems need explicit merge semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contracts, data-modeling, composition]
---

When handoff contracts reference base contracts, redeclare values, and define unions, the merge strategy (append vs. replace, conflict resolution, uniqueness constraints) must be explicit. Otherwise composition can weaken the base or create ambiguity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
