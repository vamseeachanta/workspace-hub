# Plan for #2315: cadence(monthly) coverage drift report

> **Status:** plan-review
> **Complexity:** T1 (thin variant of shared cadence-cron design)
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2315
> **Base design:** `docs/plans/2026-04-17-cadence-cron-infrastructure.md`
> **Companion:** vamseeachanta/assethold#31 (enforce coverage gates)

## What this cadence does

Each month, computes line-coverage delta per tier-1 repo vs. 30 days ago. PR-level
gates only catch drops per PR; slow erosion across many small PRs is invisible
without a trend report.

## Data sources

- Current month: `coverage.xml` artifacts from `scripts/testing/run-all-tests.sh` per repo
- Baseline: previous month's `docs/reports/coverage-drift-YYYY-MM.md`

## Headline metric

**Maximum per-repo coverage drop (percentage points).** Thresholds:
- WARN_PP = 1 (−1pp over a month is notable)
- BLOCK_PP = 5 (−5pp is a regression)

## Report shape

```
# coverage-drift — 2026-04
**Status:** GREEN — all repos within 1pp of prior month.
## Per-repo coverage
| Repo | This month | Last month | Δ (pp) | Flag |
## Files with largest drops
| Repo | File | This month | Last month | Δ (lines) |
## Source
```

## Files to Change

| Action | Path |
|---|---|
| Create | `scripts/cron/coverage-drift-report.sh` |
| Create | `tests/cron/test_coverage_drift_report.py` |
| Create | `docs/reports/coverage-drift-2026-04.md` (first sample) |
| Append | `scripts/cron/crontab-template.sh` (entry `0 8 1 * *`) |
| Update | `docs/reports/cadence-schedule.md` |

## Tests

| Test | Verifies |
|------|----------|
| test_coverage_drift_green_when_stable | all repos Δ ≤ 1pp → GREEN |
| test_coverage_drift_yellow_when_warn | some repo Δ 1-5pp → YELLOW |
| test_coverage_drift_red_when_block | any repo Δ >5pp → RED |
| test_coverage_drift_parses_coverage_xml | reads `<coverage line-rate=...>` correctly |
| test_coverage_drift_handles_missing_baseline | first run → all rows show "—" for last month |
| test_coverage_drift_handles_missing_coverage_xml | repo without coverage.xml → row flagged "no data" |

## Acceptance Criteria

- [ ] 6/6 tests pass.
- [ ] First sample report committed.
- [ ] Cron `0 8 1 * *` in template.

## Risks & Open Questions

- **Open:** Should we also report *branch* coverage (not just line)? Current plan: line-only for v1; branch coverage as follow-up.
- **Risk:** `coverage.xml` format drift between pytest-cov versions — pin the parser to the specific schema and log parse errors.
