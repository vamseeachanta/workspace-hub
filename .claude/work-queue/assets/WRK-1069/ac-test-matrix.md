# WRK-1069 AC Test Matrix

| # | AC | Test | Type | Result |
|---|-----|------|------|--------|
| T1 | load_records returns all valid lines | test_load_records_returns_all_lines | happy | PASS |
| T2 | malformed JSONL lines skipped, count returned | test_load_records_skips_malformed_lines | edge | PASS |
| T3 | skip count = 0 for clean file | test_load_records_returns_skip_count | happy | PASS |
| T4 | aggregate sums tokens+cost per WRK | test_aggregate_by_wrk_sums_tokens_and_cost | happy | PASS |
| T5 | aggregate handles empty input | test_aggregate_by_wrk_handles_empty | edge | PASS |
| T6 | filter by WRK-ID returns only matching | test_filter_by_wrk_returns_only_matching | happy | PASS |
| T7 | missing wrk field → unattributed bucket | test_missing_wrk_field_goes_to_unattributed | edge | PASS |
| T8 | format_cost_table includes WRK-ID/INPUT/COST_USD headers | test_format_cost_table_includes_headers | happy | PASS |
| T9 | format_cost_table shows skipped record count | test_format_cost_table_shows_skipped_count | edge | PASS |
| T10 | missing data file returns empty, not exception | test_load_records_missing_file_returns_empty | error | PASS |

**10 PASS / 0 FAIL**
Command: `uv run --no-project python -m pytest scripts/ai/tests/test_wrk_cost_report.py -v`
