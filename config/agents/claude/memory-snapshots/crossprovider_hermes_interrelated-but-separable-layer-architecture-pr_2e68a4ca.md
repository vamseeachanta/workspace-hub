---
name: crossprovider hermes interrelated-but-separable-layer-architecture-pr
description: "Interrelated but separable" layer architecture principle: parent/child contracts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, layering, contracts]
---

Parent plan (#2726 data/execution/report architecture) defines cross-layer lifecycle contract. Child plans (#2727 data, #2728 execution, #2729 report) independently dispatchable only if they consume parent contract without redefining upstream/downstream interfaces. Separation prevents tight coupling and interface redefinition.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
