# WRK-1036 Test Summary

**Suite**: scripts/hooks/tests/test-tidy-agent-teams.sh
**Run date**: 2026-03-08
**Result**: 13/13 PASS

| Test | Description | Result |
|------|-------------|--------|
| T1 | dry-run clean state → deleted=0 tasks_purged=0 | PASS |
| T2 | live run clean state exits 0 | PASS |
| T3 | archived WRK team detected in dry-run | PASS |
| T4 | archived WRK team deleted in live run | PASS |
| T5 | non-conforming team name preserved | PASS |
| T6 | fresh empty UUID dir preserved (<7 days) | PASS |
| T7 | stale empty UUID dir flagged in dry-run (>7 days) | PASS |
| T7b | stale empty UUID dir purged in live run | PASS |
| T8 | spawn-team.sh no-args exits non-zero | PASS |
| T9 | spawn-team.sh bad WRK_ID rejected | PASS |
| T10 | spawn-team.sh bad slug rejected | PASS |
| T11 | spawn-team.sh valid input prints recipe | PASS |
| T12 | spawn-team.sh already-exists exits 0 with message | PASS |

**Coverage**: tidy happy path, all rejection paths, dry-run vs live-run, stale detection,
spawn validation, idempotency
