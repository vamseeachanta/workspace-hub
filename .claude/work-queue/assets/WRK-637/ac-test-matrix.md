# WRK-637 AC Test Matrix

| Acceptance Criterion | Test | Result |
|---------------------|------|--------|
| `compact-memory.py --dry-run` runs cleanly, no writes | `test_dry_run_writes_no_files` | PASS |
| Done-WRK eviction moves refs to archive/done-wrk.md | `test_done_wrk_eviction` | PASS |
| Path staleness flags ≥1 stale path (--check-paths) | `test_path_staleness_flagged` | PASS |
| Path staleness NOT flagged without --check-paths | `test_path_staleness_skipped_without_flag` | PASS |
| Compaction frees ≥10 lines from oversized file | `test_lines_freed_from_oversized_file` | PASS |
| `# keep` exempts age eviction | `test_keep_marker_survives_eviction` | PASS |
| `# keep` does NOT exempt done-WRK eviction | `test_keep_does_not_exempt_done_wrk` | PASS |
| Idempotency: second run → no-op on topic files | `test_idempotency` | PASS |
| `compact-log.jsonl` written with required fields | `test_compact_log_written` | PASS |
| Zero-change apply writes zero-change log entry | `test_zero_change_idempotency_log` | PASS |
| Missing memory-root fails with clear error | `test_missing_memory_root_fails` | PASS |
| Malformed date degrades gracefully (no crash) | `test_malformed_date_no_crash` | PASS |
| Atomic write: files valid after run | `test_atomic_write_files_valid` | PASS |
| curate-memory.py runs cleanly | `test_curate_runs_cleanly` | PASS |
| Promotion candidates file written | `test_promotion_candidates_written` | PASS |
| Legal rule classified memory-keep (not in candidates) | `test_legal_rule_classified_memory_keep` | PASS |
| Refactor candidate classified domain-doc | `test_refactor_candidate_classified` | PASS |
| curate-memory.py does not modify memory files | `test_curate_does_not_modify_memory` | PASS |
| `# keep` bullet classified memory-keep (not in candidates) | `test_keep_marker_classified_memory_keep` | PASS |
| Done-WRK bullet classified archive | `test_done_wrk_classified_archive` | PASS |
| curate-memory.py missing root exits non-zero | `test_missing_memory_root_fails (curate)` | PASS |

**Total: 21 PASS, 0 FAIL**

## Deferred ACs (out of scope per plan)
- MEMORY.md ≤180 lines after WRK-635 bulk scan → depends on WRK-635 implementation
- `scan-sessions.py` headroom check → WRK-635 integration
- comprehensive-learning Phase 3b updated → see Stage 14/integration notes
