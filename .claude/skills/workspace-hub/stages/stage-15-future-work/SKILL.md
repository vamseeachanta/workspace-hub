---
name: stage-15-future-work
description: "Stage 15: Future Work Synthesis"
version: 1.0.0
category: workspace-hub
type: skill
stage_order: 15
invocation: task_agent
weight: medium
human_gate: False
---

Stage 15 · Future Work Synthesis | task_agent | medium | single-thread
Entry: evidence/execute.yaml, review.md
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Review execution notes and review.md for deferred ideas
2. Capture each as WRK item if not already in queue (use /work add)
3. Write evidence/future-work.yaml (recommendations[] with disposition/status/captured)
4. All spun-off-new items must have captured: true
Exit: evidence/future-work.yaml (all spun-off-new items captured: true)
