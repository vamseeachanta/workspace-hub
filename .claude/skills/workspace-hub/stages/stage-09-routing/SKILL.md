---
name: stage-09-routing
description: "Stage 09: Work-Queue Routing"
version: 1.0.0
category: workspace-hub
type: skill
stage_order: 9
invocation: chained_agent
weight: light
human_gate: False
---

Stage 9 · Work-Queue Routing | chained_agent | light | single-thread
Entry: evidence/activation.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Load all required skills (work-queue-workflow, workflow-gatepass, domain skills)
2. Confirm delivery order (P1→P2→P3→P4 or as planned)
3. Write routing.yaml (skills_loaded, stage_sequence_from_here)
Exit: routing.yaml (work_queue_skill: loaded, work_wrapper_complete: true)
