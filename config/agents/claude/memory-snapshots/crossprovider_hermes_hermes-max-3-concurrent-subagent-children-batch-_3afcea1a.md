---
name: crossprovider hermes hermes-max-3-concurrent-subagent-children-batch-
description: Hermes max 3 concurrent subagent children; batch multi-repo dispatches
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-concurrency, multi-agent-orchestration]
---

Hermes queue enforces max 3 concurrent child agents. Multi-repo orchestration (e.g., workspace-hub tier-1 repos) requires batching; initial 7-task dispatch failed, 3+2+2 batches succeeded. Plan concurrency limits before designing parallel workflows.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
