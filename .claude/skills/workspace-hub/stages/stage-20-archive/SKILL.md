---
name: stage-20-archive
description: "Stage 20: Archive"
version: 1.0.0
category: workspace-hub
type: skill
stage_order: 20
invocation: task_agent
weight: light
human_gate: False
---

Stage 20 · Archive | task_agent | light | single-thread
Entry: done/WRK-NNN.md
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run: bash scripts/work-queue/archive-item.sh WRK-NNN
2. Verify archive/WRK-NNN.md exists
3. Regenerate INDEX.md
4. Clear active-wrk: bash scripts/work-queue/clear-active-wrk.sh
Git:
- Archive commit format: `chore(WRK-NNN): archive WRK-NNN <title>`
- Commit to main + push immediately
Exit: archive/WRK-NNN.md + updated INDEX.md + active-wrk cleared
