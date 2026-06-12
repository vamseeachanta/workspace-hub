---
name: crossprovider hermes wave-based-parallel-subagent-batching-for-featur
description: Wave-based parallel subagent batching for feature execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [orchestration, parallel, execution, git]
---

For multi-workstream features, partition work into waves (2-3 parallel subagents per wave) based on dependency DAG, not all-parallel. Balances parallelism against git contention and resource limits. Validated on 6-workstream feature execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
