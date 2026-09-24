---
name: crossprovider codex plan-scope-boundaries-require-explicit-parent-is
description: Plan scope boundaries require explicit parent-issue anchoring
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope-boundaries, plan-decomposition, correctness]
---

Multi-issue plans must name the parent issue's contract being built on, explicitly exclude parent implementation work, and mark files as 'regression-only' or 'verify only'. When MAJOR scope-creep findings occur, re-anchor to the correct boundary (e.g., disclosure-layer vs sanction-point) rather than widening scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
