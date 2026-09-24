---
name: crossprovider gemini per-phase-provider-routing-in-wrk-task-execution
description: Per-phase provider routing in WRK task execution
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [task-execution, provider-routing, workflow]
---

WRK tasks can assign different providers per execution phase via `task_agents:` block in frontmatter (YAML-like, indented). Priority: phase-specific assignment > WRK-level provider field > CLI --provider flag. Enables fine-grained multi-provider workflows.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
