---
name: stage-03-triage
description: "Stage 03: Triage"
version: 1.0.0
category: workspace-hub
type: skill
stage_order: 3
invocation: chained_agent
weight: light
human_gate: False
---

Stage 3 · Triage | chained_agent | light | single-thread
Entry: evidence/resource-intelligence.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Read resource-intelligence.yaml
2. Confirm route (A/B/C), workstations, orchestrator
3. Surface open questions; update WRK frontmatter
Exit: pending/WRK-NNN.md (route/workstations set)
