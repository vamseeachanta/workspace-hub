# WRK-1124 Plan

Route A inline plan.

## Mission
`whats-next.sh` must surface all WRK items that are actively in-progress via checkpoint.yaml,
and display Stage/Status/PID columns across all rows.

## Changes
1. Add `get_checkpoint_stage()`, `get_session_pid()`, `derive_status()` helpers
2. Extend row format: `id|pri|sub|cpu|ttl|stage|status|pid`
3. Checkpoint routing: pending item with non-empty cp_stage → UNCLAIMED_ACTIVE
4. `print_section()`: add `show_pid` param; update headers and row printing
5. SKILL.md: add session-lock.yaml write instruction to session-resume path

## Tests
| Test | Type | Expected |
|------|------|----------|
| Pending item with checkpoint in UNCLAIMED | happy | WRK-1123/1109 appear |
| Hard gate stage → WAITING status | happy | Stage 1 → WAITING |
| Non-gate stage → START status | happy | Stage 3 → START |
| No checkpoint → READY | happy | MEDIUM items show READY |
| WORKING rows show PID | happy | WRK-1069 PID visible |
