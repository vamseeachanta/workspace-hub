## Parent: #1668 (retroactive review)

## Problem
Codex adversarial review (2026-04-02) found race condition:
- `watch-results.sh` has no inter-process locking
- Two watcher instances can both observe "no marker", both run post-process-hook.py,
  and both append the same result to JSONL before either touches the marker
- Creates duplicate post-processing and corrupted downstream data

## Severity: HIGH (S3)

## Fix Options
1. Use `flock` on a lockfile before processing each result
2. Use atomic marker rename (mv is atomic on same filesystem)
3. Add PID file check to prevent concurrent watcher instances

## Acceptance Criteria
- [ ] Only one watcher instance can process a given result at a time
- [ ] Concurrent watcher starts are detected and one exits gracefully
- [ ] No duplicate entries in solver-results-log.jsonl from concurrent processing
- [ ] Tests verify locking behavior

## Source
Review: `scripts/review/results/2026-04-02T132222Z-retroactive-review-codex.md`