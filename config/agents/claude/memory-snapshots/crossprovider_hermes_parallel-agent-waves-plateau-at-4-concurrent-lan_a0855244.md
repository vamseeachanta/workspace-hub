---
name: crossprovider hermes parallel-agent-waves-plateau-at-4-concurrent-lan
description: Parallel-agent waves plateau at ~4 concurrent lanes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallelization, concurrency, resource-limits]
---

Dispatching 10+ parallel subagents to assess/review issues on the same queue hits environment failures (broken cron, paused automation). Beyond ~4 parallel lanes, coordination overhead and resource contention become the bottleneck.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
