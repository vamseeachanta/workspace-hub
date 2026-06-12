---
name: crossprovider gemini subagent-handoff-rich-checkpoint-metadata-not-st
description: Subagent handoff: rich checkpoint metadata, not stdout signaling
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [subagents, orchestration, context-management]
---

Handoff from one stage to next requires checkpoint.yaml with context_summary, entry_reads, next_stage, human_gate. STAGE_GATE is signaling block. Human gates (stages 5, 7, 17) should be data-driven in stage contracts, not hardcoded in orchestrator. Stdout parsing is fragile; file-based metadata is reliable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
