---
name: stage-18-reclaim
description: "Stage 18: Reclaim"
version: 1.0.0
category: workspace-hub
type: skill
stage_order: 18
invocation: task_agent
weight: light
human_gate: False
---

Stage 18 · Reclaim | task_agent | light | single-thread
Entry: evidence/user-review-close.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Check for assets/WRK-NNN/checkpoint.yaml
2. If no checkpoint: write evidence/reclaim.yaml (status: n/a) via Write tool
3. If checkpoint found: re-orient from checkpoint; write reclaim.yaml (status: reclaimed)
Exit: evidence/reclaim.yaml (status: n/a | reclaimed)
