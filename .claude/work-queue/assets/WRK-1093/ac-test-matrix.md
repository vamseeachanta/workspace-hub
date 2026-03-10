# WRK-1093 AC Test Matrix

| AC | Test | Result |
|----|------|--------|
| check_doc_drift.py exists | ls scripts/quality/check_doc_drift.py | PASS |
| Reads symbol index | test_load_symbol_index_reads_jsonl | PASS |
| Graceful on missing index | test_load_symbol_index_missing_file_exits_cleanly | PASS |
| Whole-word grep only | test_build_doc_mention_set_whole_word_only | PASS |
| Drift score 0.0 = all documented | test_compute_drift_score_all_documented | PASS |
| Drift score 1.0 = none documented | test_compute_drift_score_none_documented | PASS |
| Batched git log (not per-file) | test_batch_git_modified_files_returns_set | PASS |
| Staleness uses batch set | test_detect_staleness_uses_batch_not_per_file | PASS |
| Human-review strings (no auto-capture) | test_format_drift_candidates_returns_strings_not_auto_capture | PASS |
| doc-drift-baseline.yaml created | ls config/quality/doc-drift-baseline.yaml | PASS |
| check-all.sh --drift flag | grep OPT_DRIFT scripts/quality/check-all.sh | PASS |
| Nightly cron entry | grep "check_doc_drift" scripts/cron/crontab-template.sh | PASS |
| Ruff clean | uv tool run ruff check scripts/quality/check_doc_drift.py | PASS |

Total: 13 PASS, 0 FAIL
