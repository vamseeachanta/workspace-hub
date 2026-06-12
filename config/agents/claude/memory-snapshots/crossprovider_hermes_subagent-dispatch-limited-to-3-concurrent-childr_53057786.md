---
name: crossprovider hermes subagent-dispatch-limited-to-3-concurrent-childr
description: Subagent dispatch limited to 3 concurrent children—batch in waves
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [subagent, parallelism, task-dispatch]
---

Hermes delegates support max 3 concurrent subagents. To fix >3 repos in parallel, split dispatch into batches of 3 and wait for completion before launching the next batch. Tool error: `Too many tasks: 7 provided, but max_concurrent_children is 3`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
