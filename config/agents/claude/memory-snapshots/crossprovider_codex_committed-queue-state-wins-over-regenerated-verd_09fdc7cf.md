---
name: crossprovider codex committed-queue-state-wins-over-regenerated-verd
description: Committed queue state wins over regenerated verdict artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-consistency, queue-semantics]
---

When verification tools generate `verdicts-*.tsv` files that contradict committed `_verification-queue.csv`, the committed queues are durable and stale verdicts silently fail to persist. Always trust committed queue state as the ground truth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
