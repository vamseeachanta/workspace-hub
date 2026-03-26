# Phase 2: Accelerate worldenergydata pipelines - Context

**Gathered:** 2026-03-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Reliable, current energy data feeds — EIA, BSEE, global production. Audit current pipeline reliability, fix or rebuild flaky data ingestion, add monitoring/alerting for data freshness. Also: curate manufacturer and standards data for subsea components to feed into digitalmodel analysis. UAT: All active data sources updating on schedule with staleness matching each source's publication cadence.

</domain>

<decisions>
## Implementation Decisions

### Data Source Scope & Priority
- **D-01:** All 7 configured sources are active (BSEE, EIA US, SODIR, Metocean, Brazil ANP, UKCS, LNG Terminals). Tier 1 priority: EIA first (most complete existing code), then BSEE, then SODIR. Remaining 4 are tier 2 (best-effort this phase).
- **D-02:** EIA uses public endpoints only — no API key required.
- **D-03:** SODIR is a stub — needs building from scratch against factpages.sodir.no.

### Data Storage & Format
- **D-04:** Symlink `worldenergydata/data/modules/` → `/mnt/ace/worldenergydata/data/modules/`. Single source of truth for large datasets. Remove in-repo data, replace with symlink.
- **D-05:** New pipelines write Parquet output. Existing .bin (pickle) data stays as-is until loaders are updated. No full migration this phase.
- **D-06:** Curated manufacturer/standards data uses CSV with Pydantic validation, stored in-repo under `data/modules/` (small files stay in git).

### Three Data Tiers
- **D-07:** Tier 1 — Public API feeds (BSEE, EIA, SODIR, etc.) auto-refreshed via scheduler.
- **D-08:** Tier 2 — Curated manufacturer data (riser specs, rigid jumper catalogs, mooring components, subsea structure inventories) as CSV + Pydantic models. Sources: Cameron, NOV, Hydril catalogs, industry references.
- **D-09:** Tier 3 — Standards-extracted data (tables, coefficients, design factors from DNV, API, ASME, ISO codes). Ingested as-encountered — not a dedicated sweep, but a pipeline-ready pattern so useful tables can be added when found.

### Subsea Data for digitalmodel
- **D-10:** BSEE platform structures (SS type code), pipeline permits/locations, and deepwater structures feed into digitalmodel for analysis. Wire existing scrapers (`bsee/data/scrapers/bsee_web.py`) into scheduler for auto-refresh.
- **D-11:** Curate manufacturer data for: risers, rigid jumpers, umbilicals, manifolds, subsea templates, mooring components. Follow existing `drilling_riser_components.csv` pattern.
- **D-12:** BSEE does NOT provide component-level subsea specs — only installation-level data. Component specs come from manufacturer catalogs and standards bodies.

### Freshness & Staleness
- **D-13:** Staleness defined per source cadence: SODIR daily, BSEE weekly, EIA monthly. Not a universal 24hr window.
- **D-14:** Measured by last successful run timestamp in status.json. Stale = last_success older than expected interval + buffer.

### Alerting & Monitoring
- **D-15:** Email alerts via SMTP configured in .env (SMTP_HOST, SMTP_USER, SMTP_PASS).
- **D-16:** Alert triggers: (1) job failure after all retry attempts, (2) staleness threshold breached. Partial success (0 records) does NOT trigger alerts.

### Pipeline Rebuild Strategy
- **D-17:** Common adapter pattern for all sources: download → validate → write Parquet → update state. Reuse existing `AbstractJob` base class and `JobResult` dataclass.
- **D-18:** EIA adapter first (most complete existing code — client, ingestion, state tracking). Proves the pattern, then replicate for BSEE and SODIR.

### Claude's Discretion
- Failure handling strategy for missed cadence (retry policy, escalation thresholds)
- Curated data freshness tracking (whether to surface reports for stale CSVs)
- Deployment sequencing (code-first vs full systemd deployment)
- Tier-2 source implementation depth (full working adapters vs pattern scaffolding)
- Output format per source (Parquet vs JSONL for EIA migration)
- Dashboard/status page approach

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scheduler infrastructure
- `worldenergydata/src/worldenergydata/scheduler/scheduler.py` — DataScheduler class, job registration, run loop
- `worldenergydata/src/worldenergydata/scheduler/config.py` — YAML config loader, SchedulerConfig dataclass
- `worldenergydata/src/worldenergydata/scheduler/monitor.py` — JobLogger, RetryManager, StatusReporter
- `worldenergydata/src/worldenergydata/scheduler/jobs/base.py` — AbstractJob interface, JobResult dataclass
- `worldenergydata/config/scheduler/scheduler_config.yml` — Job definitions, intervals, monitoring config

### Existing job adapters (mostly stubs)
- `worldenergydata/src/worldenergydata/scheduler/jobs/eia_us_refresh.py` — EIA stub adapter
- `worldenergydata/src/worldenergydata/scheduler/jobs/bsee_refresh.py` — BSEE stub adapter
- `worldenergydata/src/worldenergydata/scheduler/jobs/sodir_refresh.py` — SODIR stub adapter

### EIA ingestion (most complete pipeline)
- `worldenergydata/src/worldenergydata/eia/ingestion.py` — Incremental JSONL ingestion with state tracking
- `worldenergydata/src/worldenergydata/eia/client.py` — EIA API client

### BSEE data infrastructure
- `worldenergydata/src/worldenergydata/bsee/data/scrapers/bsee_web.py` — Download URLs for all BSEE datasets
- `worldenergydata/src/worldenergydata/bsee/data/loaders/infrastructure/platform_loader.py` — Platform structure loader
- `worldenergydata/src/worldenergydata/bsee/data/loaders/infrastructure/pipeline_loader.py` — Pipeline data loader
- `worldenergydata/docs/data/LOCAL_DATA_PATTERN.md` — Local data pattern for large binary datasets

### Configuration
- `worldenergydata/src/worldenergydata/common/config.py` — Settings class with WED_DATA_DIR, API configs
- `worldenergydata/systemd/worldenergydata-scheduler.service` — systemd service for daemon deployment

### Curated data reference pattern
- `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv` — Existing curated CSV pattern (37 riser components)
- `worldenergydata/src/worldenergydata/vessel_fleet/models/drilling_riser.py` — Pydantic models for riser data

### digitalmodel data needs
- `digitalmodel/specs/data-needs.yaml` — 30 data needs (26 needed), includes subsea/structural requirements

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `DataScheduler` class with full job lifecycle: register, schedule, run loop, status reporting
- `AbstractJob` base class with `run()` → `JobResult` pattern and `is_due()` cadence check
- `RetryManager` with configurable max retries and exponential backoff
- `StatusReporter` with status.json output and webhook stub
- `JobLogger` with structured JSON logs and retention-based rotation
- `EIAIngestionState` for incremental ingestion with state persistence
- `bsee_web.py` scraper with download URLs for all BSEE datasets (platform, pipeline, deepwater, wells)
- Platform and pipeline loaders with Pydantic validation
- `drilling_riser_components.csv` as the template for curated manufacturer data

### Established Patterns
- YAML-driven scheduler configuration (`scheduler_config.yml`)
- Pydantic-settings for env-based config (`WED_` prefix, `.env` file support)
- Job adapters as separate files inheriting `AbstractJob`
- Binary data on `/mnt/ace/`, small curated data in git
- `assetutilities` as shared infrastructure dependency

### Integration Points
- Scheduler → job adapters → data scrapers/clients → output files
- `Settings.data_dir` controls base data path (configurable via `WED_DATA_DIR`)
- `status.json` for monitoring, `logs/scheduler/` for structured logs
- systemd service for daemon deployment
- digitalmodel `data-needs.yaml` defines what analysis modules need from these pipelines

</code_context>

<specifics>
## Specific Ideas

- Data moved to `/mnt/ace/worldenergydata/data/` — symlink from repo, single source of truth
- BSEE has structural data (platform structures with SS type code) and pipeline data (permits + locations) that should feed into digitalmodel analysis
- Subsea component data (risers, rigid jumpers, manifolds, umbilicals) needs curation from manufacturer catalogs — not available from BSEE
- Standards data (tables, coefficients from DNV/API/ASME/ISO) should flow in as encountered — opportunistic extraction, not a dedicated sweep

</specifics>

<deferred>
## Deferred Ideas

- Full pickle-to-Parquet migration for existing BSEE .bin data — separate effort when loaders are updated
- BSEE pipeline inspection data — not available from public portal (only permit/installation records)
- Structural condition/assessment data — BSEE only tracks permits, not condition
- Nightly research automation — Phase 5

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-accelerate-worldenergydata-pipelines*
*Context gathered: 2026-03-25*
