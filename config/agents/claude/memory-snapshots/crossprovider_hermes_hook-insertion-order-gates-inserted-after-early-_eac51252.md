---
name: crossprovider hermes hook-insertion-order-gates-inserted-after-early-
description: Hook insertion order: gates inserted after early exits won't run for those paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hooks, shell, control-flow]
---

When modifying shell scripts with multiple exit points, inserting new gates after `OVERALL_EXIT=0` means they won't run for paths that early-exit before reaching that assignment. Anchor insertions before early-exit conditions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
