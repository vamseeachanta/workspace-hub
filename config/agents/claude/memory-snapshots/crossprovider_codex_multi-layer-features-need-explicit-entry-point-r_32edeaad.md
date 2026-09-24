---
name: crossprovider codex multi-layer-features-need-explicit-entry-point-r
description: Multi-layer features need explicit entry-point routing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, plan-design, feature-scope]
---

When a feature spans multiple modules (CLI, core logic, result containers), assign each layer explicit responsibility in the plan. Ambiguous routing (e.g., 'export policy decided somewhere') creates implementation confusion and mismatched expectations between layers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
