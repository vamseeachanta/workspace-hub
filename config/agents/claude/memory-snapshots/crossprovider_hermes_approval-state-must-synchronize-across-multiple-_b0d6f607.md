---
name: crossprovider hermes approval-state-must-synchronize-across-multiple-
description: Approval state must synchronize across multiple surfaces
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, approval-gating, multi-surface-sync]
---

Contract approval requires consistency between GitHub labels, local approval markers, plan text, and child acceptance criteria. Drift silently blocks downstream execution; verify all four surfaces before treating a parent as approved. (#2460)

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
