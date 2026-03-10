# WRK-1067 Acceptance Criteria Test Matrix

| AC | Description | Test | Result |
|----|-------------|------|--------|
| AC-1 | `run-all-tests.sh --coverage` generates per-repo coverage report | `test_report_file_written` + smoke run | PASS |
| AC-2 | `coverage-baseline.yaml` populated with current coverage per repo | Baseline created; 4 repos | PASS |
| AC-3 | Pre-push hook blocks if repo drops >2% below baseline | `test_fail_when_below_ratchet_floor` | PASS |
| AC-4 | Exemptions supported with required reason field | `test_skip_exempt_repo` + `test_exempt_requires_reason` | PASS |
| AC-5 | Coverage reports stored with WRK reference for audit trail | `test_report_file_written` + `coverage-reports/` dir | PASS |
| AC-6 | Cross-review (Codex) passes | Codex REQUEST_CHANGES resolved in revised plan | PASS |

All 6 ACs verified. 14 TDD tests PASS, 0 FAIL.
