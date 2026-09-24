---
name: crossprovider gemini stage-isolated-wrk-lifecycle-prevents-context-ro
description: Stage-isolated WRK lifecycle prevents context rot in long pipelines
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [orchestration, context-management, multi-agent]
---

Fresh task_agent spawns with zero prior context per stage eliminate compaction and quality drift. Each stage starts from previous stage's exit artifacts only, enforcing clean context boundaries. Use when designing multi-stage orchestrated work with >5 stages.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
