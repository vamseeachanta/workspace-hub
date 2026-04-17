# Plan for #2313: cadence(weekly) memory health report

> **Status:** plan-review
> **Complexity:** T1 (thin variant of shared cadence-cron design)
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2313
> **Base design:** `docs/plans/2026-04-17-cadence-cron-infrastructure.md`
> **Companion:** #1902 (memory quality gate before bridge commit)

## What this cadence does

Emits a weekly report on the health of `~/.hermes/memories/` and `/home/*/.claude/projects/*/memory/`
before the Hermes cross-machine bridge (cron `8c797470`) propagates them to 5 machines.

## Data sources

- Live memory dirs on the current machine:
  - `~/.hermes/memories/` (if present)
  - `~/.claude/projects/*/memory/` (all claude-code projects)
- Previous week's report at `docs/reports/memory-health-YYYY-WW.md` (for deltas)

## Headline metric

**Total memory bytes across all tracked memory dirs.** Thresholds:
- `STATE_SIZE_WARN_MB` = 5 (stale memory piles up)
- `STATE_SIZE_BLOCK_MB` = 20 (too large to load on every session)

## Report shape

```
# memory-health — 2026-W16
**Status:** GREEN — total memory is 2 MB across 12 files.
## Top 10 largest memory files
| Size (KB) | Path | Flag |
## Stale entries (last modified > 90 days)
| Path | Last modified |
## Duplicate topics (by filename prefix) across machines
| Topic | Machines |
## Source
```

## Files to Change

| Action | Path |
|---|---|
| Create | `scripts/cron/memory-health-report.sh` |
| Create | `tests/cron/test_memory_health_report.py` |
| Create | `docs/reports/memory-health-2026-W16.md` (first sample) |
| Append | `scripts/cron/crontab-template.sh` (entry `0 6 * * 1`) |
| Update | `docs/reports/cadence-schedule.md` (row for this cadence) |

## Tests

| Test | Verifies |
|------|----------|
| test_memory_health_green_when_small | <5 MB total → GREEN |
| test_memory_health_yellow_when_warn | 5–20 MB → YELLOW |
| test_memory_health_red_when_block | >20 MB → RED |
| test_memory_health_lists_top_10_by_size | top-10 table populated |
| test_memory_health_flags_stale_entries | files with mtime >90d appear in Stale section |
| test_memory_health_deduplicates_topics | files with same stem across machine dirs flagged |
| test_memory_health_handles_missing_dirs | no memory dirs → empty report, exit 0, GREEN |

## Acceptance Criteria

- [ ] 7/7 tests pass.
- [ ] First sample report committed; `Status: GREEN|YELLOW|RED` accurate for this machine's memory snapshot.
- [ ] Cron entry added to template.
- [ ] Linked from `docs/reports/cadence-schedule.md`.

## Risks & Open Questions

- **Open:** Should report run on all 5 machines and aggregate, or per-machine only? Current plan: per-machine; cross-machine aggregation deferred (requires Hermes bridge integration).
- **Risk:** `~/.hermes/` may not exist on fresh installs — hook exits 0 with GREEN status.
