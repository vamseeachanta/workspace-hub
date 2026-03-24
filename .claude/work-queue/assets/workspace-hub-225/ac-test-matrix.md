| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC1 | _update_stage_ev wired into exit_stage.py before HTML regen | PASS | exit_stage.py lines 225-236, test_update_stage_ev_noop_when_script_missing |
| AC2 | _update_stage_ev wired into start_stage.py before HTML regen | PASS | start_stage.py lines 453-463, test_update_stage_ev_noop_when_script_missing |
| AC3 | Stage 1 guard accepts pending/ or working/ | PASS | test_pending_or_working_guard_accepts_pending, _accepts_working, _blocks_missing |
| AC4 | Stage progression guard blocks when prev stage not done | PASS | test_progression_guard_blocks_when_prev_in_progress, _blocks_when_prev_pending |
| AC5 | Stage progression guard allows done and n/a | PASS | test_progression_guard_allows_when_prev_done, _allows_when_prev_na |
| AC6 | Backcompat: no evidence file = no blocking | PASS | test_progression_guard_allows_when_no_evidence_file, _allows_when_prev_stage_not_in_evidence |
| AC7 | Existing guard tests still pass (no regression) | PASS | test_start_stage_guards.py: 7/7 pass |
