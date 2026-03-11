# WRK-1092 AC Test Matrix

| AC | Test | Result |
|----|------|--------|
| `config/quality/mypy-baseline.yaml` created with error counts | `test_init_mode_writes_baseline` | PASS |
| Parse "Found N errors in M files" → N | `test_parse_found_n_errors_output` | PASS |
| Parse "Success: no issues found" → 0 | `test_parse_success_no_issues` | PASS |
| Ratchet FAIL when count increases | `test_ratchet_fail_count_increased` | PASS |
| Ratchet PASS when count equals | `test_ratchet_pass_count_equal` | PASS |
| Ratchet PASS + auto-update when count decreases | `test_ratchet_pass_count_decreased` | PASS |
| `SKIP_MYPY_REASON` bypass works | `test_skip_mypy_reason_bypass` | PASS |
| Missing baseline → clear error | `test_missing_baseline_file_exits_with_error` | PASS |
| Schema validation valid | `test_schema_validation_valid` | PASS |
| Schema validation invalid | `test_schema_validation_invalid_missing_repos` | PASS |
| Exempt repo skipped | `test_exempt_repo_is_skipped` | PASS |
| `check-all.sh --mypy-ratchet` flag added | Manual inspect check-all.sh | PASS |
| Pre-push hook has `MYPY_RATCHET_GATE=1` opt-in | Manual inspect pre-push.sh | PASS |
| All 14 TDD tests pass | `uv run --no-project python -m pytest tests/quality/test_check_mypy_ratchet.py` | PASS |

**Result: 14 PASS, 0 FAIL**
