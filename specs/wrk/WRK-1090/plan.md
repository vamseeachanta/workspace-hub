# WRK-1090 — Dependency Health: uv.lock Freshness, CVE Advisories, Outdated Deps

## Goal

Build `scripts/quality/dep-health.sh` to check dependency health across 5 tier-1 Python repos
(assetutilities, digitalmodel, worldenergydata, assethold, OGManufacturing).

## Acceptance Criteria

- AC1: `scripts/quality/dep-health.sh` exists and runs
- AC2: Exit code 0 = healthy, 1 = CVEs/stale
- AC3: YAML report at `logs/quality/dep-health-{datetime}.yaml`
- AC4: CVE findings → auto-WRK item in pending/
- AC5: Nightly cron entry in `crontab-template.sh`
- AC6: ≥5 TDD tests
- AC7: Passes `check-all.sh` (bash only, no Python src)

## Implementation Plan

### Phase 1: TDD (Red)
Write `tests/quality/test_dep_health.sh` with ≥5 failing tests:
- T1: stale lock → exit 1
- T2: fresh lock → exit 0
- T3: outdated → exit 0 (warn only)
- T4: CVE vuln → exit 1
- T5: clean CVE → exit 0
- T6: auto-WRK created on CVE
- T7: YAML report written

### Phase 2: Implementation (Green)
Write `scripts/quality/dep-health.sh`:
- Freshness: `uv lock --check --offline`
- Outdated: `uv run pip list --outdated --format=json`
- CVE: `uvx pip-audit --format=json -r /dev/stdin`
- Report: `logs/quality/dep-health-$(date +%Y-%m-%dT%H%M).yaml`
- Auto-WRK: `flock --timeout 10` + `next-id.sh` + `WRK-${NEXT_NUM}.md`

### Phase 3: Cron
Add nightly entry (01:00) to `scripts/cron/crontab-template.sh`.

### Phase 4: Cross-Review
Opus/Codex/Gemini review; fix critical findings.
