---
name: crossprovider hermes subagent-parallel-dispatch-limited-to-3-concurre
description: Subagent parallel dispatch limited to 3 concurrent children
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [agents, parallelization, dispatch, concurrency]
---

Max concurrent `delegate_task` children is 3. Larger batches fail immediately; must partition into batches of ≤3 and wait for completion before next batch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
