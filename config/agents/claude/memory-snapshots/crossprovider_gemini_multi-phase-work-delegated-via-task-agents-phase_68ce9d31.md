---
name: crossprovider gemini multi-phase-work-delegated-via-task-agents-phase
description: Multi-phase work delegated via task_agents.<phase>: <provider> frontmatter
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [agents, workflows, delegation]
---

Routing checks task_agents.<phase> first, falls back to static provider field. Enables per-phase agent assignment without workflow refactoring.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
