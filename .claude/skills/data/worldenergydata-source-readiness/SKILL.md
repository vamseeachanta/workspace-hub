---
name: worldenergydata-source-readiness
description: Route agents to the canonical worldenergydata source-readiness skill and summary script. Use when asked for worldenergydata data completeness, data locations, latest known data dates, scheduler freshness, source-readiness status, or acceptance-criteria inputs across the repo ecosystem.
---

# WorldEnergyData Source Readiness

## Quick Start

Use the canonical skill and script in the `worldenergydata` checkout:

```bash
WED_REPO="${WED_REPO:-../worldenergydata}"
cd "$WED_REPO"
git fetch origin main
python .claude/skills/worldenergydata-source-readiness/scripts/source_readiness_summary.py
```

JSON output:

```bash
WED_REPO="${WED_REPO:-../worldenergydata}"
cd "$WED_REPO"
git fetch origin main
python .claude/skills/worldenergydata-source-readiness/scripts/source_readiness_summary.py --format json
```

If the script is missing, update the `worldenergydata` checkout to a revision at or after PR #461.

## What This Returns

The summary includes:

- data group / module
- catalog status and freshness status
- latest known date and whether it came from metadata, file timestamps, or scheduler success
- repo-local data location
- external data root, if metadata records one
- configured scheduler output directory
- dataset count, record count, file count, and size

## Interpretation Rule

Do not treat `latest_known_date` as source-data vintage unless the row says the basis is an inspected dataset field. Most current rows use metadata refresh, newest file modified date, or scheduler success.

For acceptance criteria, require each Tier-A source to expose:

- `source_data_latest_date`
- `last_successful_refresh`
- `data_location`
- `record_count`
- `freshness_status`
- `refresh_cadence`
- `blocker_issue` or `none`

## Canonical Files

In `worldenergydata`:

- `.claude/skills/worldenergydata-source-readiness/SKILL.md`
- `.claude/skills/worldenergydata-source-readiness/scripts/source_readiness_summary.py`
- `data/freshness-scorecard.json`
- `data/modules/<module>/_metadata.json`
- `data/modules/<module>/manifest.json`
- `config/scheduler/scheduler_config.yml`
