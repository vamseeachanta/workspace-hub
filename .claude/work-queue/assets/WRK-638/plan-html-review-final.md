# WRK-638 Plan — Final Review

## Plan Summary

Implement `scripts/memory/eval-memory-quality.py` — read-only quality reporter with 6 metrics:
- pct_done_wrk, pct_stale_paths, signal_density, memory_md_headroom, topic_file_headroom, dedup_candidates

CLI: `--memory-root`, `--format json|md`, `--check-paths`, `--compare before.json after.json`

10 TDD tests in `tests/memory/test_eval_memory_quality.py`.

## Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-09T10:12:00Z
decision: passed
