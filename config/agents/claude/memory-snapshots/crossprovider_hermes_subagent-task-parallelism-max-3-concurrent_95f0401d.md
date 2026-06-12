---
name: crossprovider hermes subagent-task-parallelism-max-3-concurrent
description: Subagent task parallelism: max 3 concurrent
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tooling, subagent-limits, parallelism, task-dispatch]
---

delegate_task maximum concurrent = 3; user-requested 4 parallel tasks require batching (3+1 sequential or background fallback). Subagent output may compress under verbosity constraints; prefer direct plan/issue inspection for high-confidence verdicts on complex items.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
