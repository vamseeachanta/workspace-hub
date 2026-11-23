# Plan for #2314: cadence(monthly) broken-windows test sweep

> **Status:** plan-review
> **Complexity:** T1 (thin variant of shared cadence-cron design)
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2314
> **Base design:** `docs/plans/2026-04-17-cadence-cron-infrastructure.md`
> **Companion:** vamseeachanta/digitalmodel#510 (20 pre-existing OrcaFlex failures)

## What this cadence does

Re-runs every pytest suite across tier-1 repos once a month. Flags *newly-failing*
tests vs. the previous month's baseline. Emits a diff so reviewers see only the
delta, not a noisy full report.

## Data sources

- Tier-1 repos: `assetutilities`, `digitalmodel`, `worldenergydata`, `assethold`, `OGManufacturing`
- Previous run: `docs/reports/broken-windows-YYYY-MM.md` (for baseline)

## Headline metric

**Count of newly-failing tests (this run vs previous).** Thresholds:
- WARN_COUNT = 1 (any new failure is suspicious)
- BLOCK_COUNT = 5 (multiple new failures = regression wave)

## Report shape

```
# broken-windows — 2026-04
**Status:** YELLOW — 2 newly-failing tests across digitalmodel.
## New failures (first time in this month)
| Repo | Test | Error summary |
## Resolved failures (now passing; were failing last month)
| Repo | Test |
## Persistent failures (still failing — pre-existing)
| Repo | Test | First seen |
## Source
```

## Files to Change

| Action | Path |
|---|---|
| Create | `scripts/cron/broken-windows-sweep.sh` |
| Create | `tests/cron/test_broken_windows_sweep.py` |
| Create | `docs/reports/broken-windows-2026-04.md` (first sample) |
| Append | `scripts/cron/crontab-template.sh` (entry `0 7 1 * *`) |
| Update | `docs/reports/cadence-schedule.md` |

## Tests

| Test | Verifies |
|------|----------|
| test_sweep_detects_new_failure | one test failing this run, not last → "New" section |
| test_sweep_detects_resolved | one test that was failing, now passing → "Resolved" section |
| test_sweep_detects_persistent | failing both runs → "Persistent" with first-seen date |
| test_sweep_baseline_parsing | reads previous report correctly |
| test_sweep_status_bands | GREEN/YELLOW/RED on new-failure count |
| test_sweep_handles_first_run | no previous report → all failures are "New" |
| test_sweep_handles_missing_repo | tier-1 repo absent → skip with note, don't fail |

## Acceptance Criteria

- [ ] 7/7 tests pass.
- [ ] First sample report committed with accurate delta against last month (or "first run" marker).
- [ ] Cron entry `0 7 1 * *` in template.

## Risks & Open Questions

- **Risk:** Full suite re-run takes time. Mitigation: script runs `pytest --collect-only` + parses cached test-health.jsonl rather than actually executing (defer execution to an opt-in `--run` flag).
- **Open:** Tier-1 list may drift — should the script read it from a config file? Current plan: hard-coded list matching `scripts/hooks/pre-push.sh:TIER1_REPOS` to stay in sync.
