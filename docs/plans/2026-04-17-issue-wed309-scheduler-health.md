# Plan for worldenergydata#309: cadence(weekly) scheduler health report

> **Status:** plan-review
> **Complexity:** T1 (thin variant of shared cadence-cron design)
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/309
> **Base design:** `docs/plans/2026-04-17-cadence-cron-infrastructure.md` (in workspace-hub)
> **Companion:** worldenergydata#266 (operationalize EIA scheduler)

## What this cadence does

Each week, reports fresh-data age for every scheduler job (EIA, BSEE, SODIR,
Brazil ANP, UKCS, etc.) so silent failures surface before downstream analyses
consume stale inputs.

## Data sources

- Scheduler output dirs (per `output_dir` config per job — see wed#271)
- Job manifests: `worldenergydata/data/<source>/manifest.json` (expected last-write ts)
- Previous report: `docs/reports/scheduler-health-YYYY-WW.md`

## Headline metric

**Count of scheduler jobs with data older than their refresh interval.**
Thresholds:
- WARN_COUNT = 1 (one stale source)
- BLOCK_COUNT = 3 (pipeline broadly failing)

## Report shape

```
# scheduler-health — 2026-W16
**Status:** YELLOW — BSEE data 9 days old (refresh interval 7 days).
## Per-job fresh-data age
| Job | Last successful write | Refresh interval | Age vs interval | Flag |
## Recent failures (from logs/, if any)
| Job | Timestamp | Error summary |
## Source
```

## Files to Change

(Lives in `worldenergydata/` repo, not workspace-hub.)

| Action | Path |
|---|---|
| Create | `worldenergydata/scripts/cron/scheduler-health.sh` |
| Create | `worldenergydata/tests/cron/test_scheduler_health.py` |
| Create | `worldenergydata/docs/reports/scheduler-health-2026-W16.md` |
| Add | `worldenergydata/scripts/cron/crontab-template.sh` (entry `0 6 * * 1`) |

## Tests

| Test | Verifies |
|------|----------|
| test_scheduler_green_when_all_fresh | all jobs within interval → GREEN |
| test_scheduler_yellow_on_one_stale | one job stale → YELLOW, job row flagged |
| test_scheduler_red_on_multiple_stale | ≥3 stale → RED |
| test_scheduler_parses_manifest | reads each job's manifest.json correctly |
| test_scheduler_handles_missing_manifest | manifest absent → "never ran" row |
| test_scheduler_handles_first_run | no baseline → fresh report, exit 0 |

## Acceptance Criteria

- [ ] 6/6 tests pass.
- [ ] First sample report committed in worldenergydata repo.
- [ ] Cron entry in template.
- [ ] Depends on wed#266/267/271 landing manifest format — until then, cadence reports with a placeholder row per known job.

## Risks & Open Questions

- **Risk:** Manifest format isn't standardized yet across jobs. Mitigation: cadence script defines the required fields (`last_success_ts`, `refresh_interval_days`); wed#266/267 enforce writing them.
- **Open:** Should staleness thresholds be per-job (different refresh rates) or global? Current plan: per-job in each manifest, global fallback of 7 days if missing.
