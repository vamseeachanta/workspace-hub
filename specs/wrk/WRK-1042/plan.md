# WRK-1042 Plan

Route A inline plan.

## Changes

1. `scripts/hooks/tidy-agent-teams.sh`: expand glob from `wrk-*` to `*`; add sentinel
   read in non-conforming else-branch — read `.wrk-id`, check if WRK is archived, delete if so
2. `scripts/work-queue/spawn-team.sh`: add `echo "${WRK_ID}" > .../.wrk-id` line to recipe
3. `scripts/hooks/tests/test-tidy-agent-teams.sh`: init ARCHIVED_WRK=""; fix T11/T12 with
   synthetic WRK-9998 fixture; add T11b, T13, T13b, T14

## Acceptance Criteria
- AC1: tidy reads .wrk-id sentinel when dir name does not match wrk-NNN-slug
- AC2: spawn-team.sh recipe includes sentinel write command
- AC3: existing tests still pass
- AC4: new test: non-conforming dir + sentinel + archived WRK → deleted
