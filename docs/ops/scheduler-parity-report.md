# Offline scheduler parity report

The report compares caller-normalized scheduler snapshots without collecting or
changing scheduler state.

## Plan-lite

- Normalized input contract: each snapshot contains exactly `available` (Boolean)
  and `jobs` (array). Each job contains exactly the nonempty strings `logical_id`,
  `surface`, `schedule` and `runtime`. Identity mappings and runtime classes are
  supplied by the caller; records in an actual snapshot must match its surface.
- Pure comparison API: `build_report(canonical, actuals, observed_at=...)` compares
  identities within each surface, then compares schedule and runtime strings
  exactly for unique pairs. It returns deterministically ordered findings without
  mutating inputs.
- Local JSON command: the command below reads normalized files and writes JSON to
  standard output. The observation timestamp is supplied explicitly.
- Focused tests: `tests/analysis/test_scheduler_parity_report.py` uses synthetic
  inputs and hand-authored expected findings, including duplicate identities,
  unavailable observations, stable ordering, invalid inputs and collection guards.
- Excluded live adapters: raw cron and gateway parsing, live collection, freshness,
  last-run evidence, installation, migration and publication remain outside this
  comparison contract.

## Local command

```bash
python scripts/analysis/scheduler_parity_report.py \
  --canonical canonical.json \
  --actual system-cron=system.json \
  --actual gateway=gateway.json \
  --observed-at 2026-10-15T12:00:00Z
```

The timestamp and file names are synthetic examples. Actual snapshots are keyed
by surface; repeat `--actual` for each relevant surface, including empty ones.
Unavailable snapshots must contain no jobs.

## Interpretation and limits

Missing or unavailable observations are unknown. An available empty snapshot can
establish missing jobs. Duplicate identities remain ambiguous; no record is chosen
for schedule or runtime comparison. Supplied observation time does not establish
freshness, and undisclosed surfaces cannot be discovered. Leap seconds are
unsupported.

Exit status `0` means valid input, including reports with findings or unknown
states. Inspect `findings` and `surfaces` in the JSON for the comparison result.
Invalid input returns `2` without emitting a partial report.
