---
name: work-queue-checkpoint-resume
description: 'Sub-skill of work-queue: Checkpoint & Resume.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Checkpoint & Resume

## Checkpoint & Resume


`checkpoint.sh WRK-NNN` writes `.claude/work-queue/assets/WRK-NNN/checkpoint.yaml`.

`/work run` auto-loads checkpoint.yaml via `start_stage.py` — no manual `/wrk-resume` needed.
Use `/wrk-resume WRK-NNN` only for diagnostic inspection of checkpoint state.

Checkpoint required fields: `wrk_id`, `stage`, `next_action`, `context_summary`, `updated_at`
(validated non-blocking by `exit_stage.py` after each stage exit).
