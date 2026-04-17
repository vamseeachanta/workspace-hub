# Plan for #2318: cadence(quarterly) external doc re-ingest

> **Status:** plan-review
> **Complexity:** T1 (thin variant of shared cadence-cron design)
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2318
> **Base design:** `docs/plans/2026-04-17-cadence-cron-infrastructure.md`
> **Companion:** vamseeachanta/digitalmodel#503 (ingest Orcina/OrcaWave webhelp)

## What this cadence does

Each quarter, re-pulls vendor documentation (Orcina webhelp, OpenFOAM, etc.)
into the LLM doc-index used by digitalmodel. Reports what changed since last
ingest so consumers of the index know a refresh happened.

## Data sources

- Vendor URLs: `data/document-index/online-resource-registry.yaml`
- Last ingest: `docs/reports/external-doc-reingest-YYYY-Q.md` + ingest manifest timestamps
- Current index: `data/document-index/standards-transfer-ledger.yaml`

## Headline metric

**Count of vendor sources that changed since last ingest.** Thresholds:
- WARN_COUNT = 1 (any change is interesting for AI-assisted authoring)
- BLOCK_COUNT = 5 (many vendors moved — signals major ecosystem shift)

## Report shape

```
# external-doc-reingest — 2026-Q2
**Status:** YELLOW — 2 vendor sources changed since 2026-Q1.
## Per-vendor change log
| Vendor | Source URL | Last modified | Δ since last ingest | Re-ingested |
## Consumer impact (issues that might benefit from the refresh)
| Issue | Reason |
## Source
```

## Files to Change

| Action | Path |
|---|---|
| Create | `scripts/cron/external-doc-reingest.sh` |
| Create | `tests/cron/test_external_doc_reingest.py` |
| Create | `docs/reports/external-doc-reingest-2026-Q2.md` (first sample) |
| Append | `scripts/cron/crontab-template.sh` (entry `0 11 1 1,4,7,10 *`) |
| Update | `docs/reports/cadence-schedule.md` |

## Tests

| Test | Verifies |
|------|----------|
| test_reingest_green_when_no_changes | all vendor sources unchanged → GREEN, no ingestion |
| test_reingest_yellow_on_change | 1 vendor changed → YELLOW, re-ingested |
| test_reingest_handles_vendor_down | vendor URL 5xx → row flagged "vendor unreachable" |
| test_reingest_respects_robots | fetches respect robots.txt |
| test_reingest_handles_first_run | no baseline → all vendors marked "initial ingest" |
| test_reingest_logs_consumer_impact | issues in dm#503 backlog flagged when Orcina changes |

## Acceptance Criteria

- [ ] 6/6 tests pass.
- [ ] First sample report committed.
- [ ] Depends on dm#503 landing the doc-index pipeline — until then, cadence reports "index not yet initialized".

## Risks & Open Questions

- **Risk:** Vendor sites may rate-limit or block automated re-ingest. Mitigation: respect robots, use firecrawl/exa where authorized, cache ETags.
- **Open:** Should re-ingest auto-commit the refreshed index, or raise a PR? Current plan: PR (via `gh pr create`) so review fires.
