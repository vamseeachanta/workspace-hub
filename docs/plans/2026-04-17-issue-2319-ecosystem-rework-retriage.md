# Plan for #2319: cadence(quarterly) ecosystem rework re-triage

> **Status:** plan-review
> **Complexity:** T1 (thin variant of shared cadence-cron design)
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2319
> **Base design:** `docs/plans/2026-04-17-cadence-cron-infrastructure.md`
> **Companion:** self (this report itself — `docs/reports/2026-04-16-ecosystem-rework-candidates.md`)

## What this cadence does

Each quarter, re-runs the ecosystem-wide issue triage that produced the
2026-04-16 top-20 rework candidates report. Emits a delta report showing:
which Tier-1 items shipped, which are still pending, what new candidates
emerged, and what fell off (closed, obviated, deprioritized).

## Data sources

- GitHub issues across 6 repos (open + closed, last 90 days of activity)
- Previous quarter's triage: latest `docs/reports/ecosystem-rework-*.md`
- Parallel sub-agents per repo (same pattern used on 2026-04-16)

## Headline metric

**Count of Tier-1 candidates that remained pending across a full quarter.**
Thresholds:
- WARN_COUNT = 3 (backlog not moving)
- BLOCK_COUNT = 7 (stall across most Tier-1 items)

## Report shape

```
# ecosystem-rework — 2026-Q2
**Status:** GREEN — 8/10 Tier-1 from last quarter shipped; 2 in progress.
## Delta vs last quarter
| # | Last Q rank | Issue | Status | Commits |
## New Tier-1 candidates
| # | Issue | Why now |
## Dropped from Tier-1 (obviated / deprioritized)
| Issue | Reason |
## Source
```

## Files to Change

| Action | Path |
|---|---|
| Create | `scripts/cron/ecosystem-rework-retriage.sh` |
| Create | `tests/cron/test_ecosystem_rework_retriage.py` |
| Create | `docs/reports/ecosystem-rework-2026-Q2.md` (first sample) |
| Append | `scripts/cron/crontab-template.sh` (entry `0 12 1 1,4,7,10 *`) |
| Update | `docs/reports/cadence-schedule.md` |

## Tests

| Test | Verifies |
|------|----------|
| test_retriage_finds_last_quarter_report | picks the most recent `ecosystem-rework-*.md` by mtime + name |
| test_retriage_marks_shipped | an issue that closed with commits tagged `Refs #N` → "shipped" |
| test_retriage_marks_in_progress | issue with recent commits but still open → "in progress" |
| test_retriage_marks_stalled | open issue with no activity in 90 days → counts toward WARN |
| test_retriage_detects_new_candidate | newly-opened issue matching selection criteria → New Tier-1 |
| test_retriage_handles_first_run | no previous report → baseline mode, marks all as new |

## Acceptance Criteria

- [ ] 6/6 tests pass.
- [ ] First sample report committed for 2026-Q2 (can use 2026-04-16 report as Q1 baseline).
- [ ] Cron `0 12 1 1,4,7,10 *` in template.

## Risks & Open Questions

- **Risk:** Issue selection criteria are partly judgmental; the cron should *surface* candidates, not self-approve Tier-1 membership. Implemented as a signal-scoring heuristic + a "candidates for human review" section.
- **Open:** Should this cadence spawn sub-agents (as the original 2026-04-16 triage did) or use rules-based scoring only? Current plan: rules-based scoring in v1 (deterministic, reproducible); sub-agent mode as `--deep` flag for manual runs.
