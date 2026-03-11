# WRK-1087 AC Test Matrix

| # | Acceptance Criterion | Test | Result |
|---|---------------------|------|--------|
| 1 | `log-action.sh` appends valid JSONL to monthly audit file | test_audit_trail.sh: "log file created", "has action/target/wrk_id/session_id/ts/prev_hash" | PASS |
| 2 | SHA256 chain: each entry hashes the previous entry's content | test_audit_trail.sh: "chain links to prev", "genesis hash" | PASS |
| 3 | Cross-file chain continuity via audit-chain-state.json | test_audit_trail.sh: "chain-state created", "chain-state has terminal_hash", "cross-file chain uses prev terminal" | PASS |
| 4 | flock prevents concurrent write races | log-action.sh uses `flock -w 5 9` on per-file lock | PASS |
| 5 | errors.log sentinel on failure | log-action.sh writes to errors.log when flock fails | PASS |
| 6 | Session-start calls log-action.sh | session.sh init: log_action session_start | PASS |
| 7 | Stop hook calls log-action.sh | settings.json Stop: log_action session_end | PASS |
| 8 | exit_stage.py calls log-action.sh | exit_stage.py: subprocess call stage_exit | PASS |
| 9 | close-item.sh calls log-action.sh | close-item.sh: wrk_close action | PASS |
| 10 | post-commit hook calls log-action.sh | .git/hooks/post-commit: commit action | PASS |
| 11 | `audit-query.sh --wrk WRK-NNN` returns all actions for that item | test_audit_trail.sh: "query by wrk returns match", "query excludes other wrk" | PASS |
| 12 | `audit-query.sh --session` filters by session | test_audit_trail.sh: "query by session" | PASS |
| 13 | `verify-chain.sh` detects any entry modification | test_audit_trail.sh: "tampered chain exit 1", "tampered chain detected" | PASS |
| 14 | Clean chain verifies OK | test_audit_trail.sh: "clean chain exit 0", "clean chain says OK" | PASS |
| 15 | Monthly rotation with 6-month compression | log-action.sh: find -mtime +180 gzip | PASS |
| 16 | Cross-review (Codex) passes | Codex cross-review: all P1s resolved | PASS |

**Total: 16 PASS, 0 FAIL**

Run: `bash tests/quality/test_audit_trail.sh`
