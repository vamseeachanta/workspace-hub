---
name: stage-16-resource-intelligence-update
description: "Stage 16: Resource Intelligence Update"
version: 1.0.0
category: workspace-hub
type: skill
stage_order: 16
invocation: task_agent
weight: medium
human_gate: False
---

Stage 16 · Resource Intelligence Update | task_agent | medium | single-thread
Entry: evidence/future-work.yaml, evidence/execute.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Identify ≥3 lessons learned from this WRK execution
2. Note new tools, patterns, or constraints discovered
3. Write evidence/resource-intelligence-update.yaml (lessons[], additions[])
Exit: evidence/resource-intelligence-update.yaml (lessons[] ≥3 entries)
