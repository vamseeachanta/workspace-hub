# WRK-5038 AC Test Matrix

| AC | Description | Test(s) | Status |
|----|-------------|---------|--------|
| AC1 | build-doc-intelligence.py scans manifests and builds all 8 indexes | test_returns_build_stats, test_creates_* (6 content types) | PASS |
| AC2 | constants/equations/procedures/requirements/definitions/worked_examples JSONL | test_creates_constants_jsonl through test_creates_worked_examples_jsonl | PASS |
| AC3 | tables/ with per-table CSV + tables-index.jsonl | test_tables_csv_created, test_tables_index_created, test_table_csv_content | PASS |
| AC4 | curves/ with curves-index.jsonl | test_curves_dir_created, test_curves_index_fields | PASS |
| AC5 | manifest-index.jsonl master index | test_creates_manifest_index, test_manifest_index_has_checksum, test_manifest_index_has_counts | PASS |
| AC6 | Incremental rebuild skips unchanged | test_second_run_skips_unchanged, test_modified_manifest_detected, test_content_survives_incremental | PASS |
| AC7 | Summary statistics printed | test_returns_build_stats + CLI --verbose output verified | PASS |
