---
name: crossprovider hermes massive-orphan-node-artifacts-signal-scope-too-b
description: Massive orphan-node artifacts signal scope too-broad or conflated diagnostics
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [scope, diagnostics, v1-design]
---

When >90% of graph nodes are orphans (19,178 of 20,018), diagnostic signal is swamped by noise. Symptom of either over-inclusive source scope or diagnostics conflating signal. Consider bounded source selection or partitioned artifact structure for v1.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
