---
name: crossprovider gemini per-phase-agent-routing-in-work-items
description: Per-phase agent routing in work items
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [workflow, routing, work-queue]
---

Work items can assign different providers per phase via `task_agents: {phase_1: gemini, phase_2: claude}` frontmatter. Priority: task_agents:<phase> > provider: field > --provider flag. Enables domain-specific provider selection within one item.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
