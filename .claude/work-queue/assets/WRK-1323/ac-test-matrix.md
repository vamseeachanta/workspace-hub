# WRK-1323 AC-Test Matrix

| AC | Test(s) | Status |
|----|---------|--------|
| AC-1: --dry-run flag accepted | test_dry_run_*, test_cli_dry_run_exit_code_zero | PASS |
| AC-2: prints items without evidence check | test_dry_run_returns_correct_item_ids, test_cli_dry_run_shows_item_count | PASS |
| AC-3: exit 0 regardless of evidence | test_cli_dry_run_exit_code_zero, test_dry_run_ignores_missing_evidence | PASS |
| AC-4: normal mode unchanged | test_normal_mode_* (3 tests) | PASS |
