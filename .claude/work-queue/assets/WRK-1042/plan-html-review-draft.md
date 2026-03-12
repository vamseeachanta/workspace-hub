# WRK-1042 — Plan Final Review

## Plan: tidy-agent-teams sentinel file support

1. `tidy-agent-teams.sh`: Change glob from `wrk-*` to `*`; add sentinel read in else-branch
2. `spawn-team.sh`: Add `.wrk-id` write line to recipe printout
3. `test-tidy-agent-teams.sh`: Init `ARCHIVED_WRK=""`; fix T11/T12 fixture; extend T11; add T13/T13b/T14

## Gate Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-11T18:46:00Z
decision: passed
