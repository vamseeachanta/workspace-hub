# Phase 2: Accelerate worldenergydata pipelines - Research

**Researched:** 2026-03-25
**Domain:** Data pipeline engineering (Python / scheduler / API ingestion / Parquet)
**Confidence:** HIGH

## Summary

Phase 2 transforms the worldenergydata project from stub job adapters into working data pipelines. The scheduler infrastructure (`DataScheduler`, `AbstractJob`, `RetryManager`, `StatusReporter`, `JobLogger`) is already solid and tested -- the work is wiring real data fetching into the stub adapters for EIA, BSEE, and SODIR (Tier 1), then adding email alerting for freshness/failure. A secondary track curates manufacturer and standards data as CSV + Pydantic models following the existing `drilling_riser_components.csv` pattern.

The codebase already has: a working EIA API v2 client with pagination and incremental state tracking (`EIAIngestionSync`), a BSEE web scraper with download URLs for 8 dataset types, and a SODIR API client with rate limiting and caching. The gap is that none of these are connected to their scheduler job stubs -- all three job files return `records_updated=0` with "stub" log messages. Additionally, there is a critical dependency issue: the `schedule` library is imported and used but not declared in `pyproject.toml`.

**Primary recommendation:** Wire existing clients/scrapers into stub adapters one at a time (EIA first, then BSEE, then SODIR), adding Parquet output and staleness tracking to `status.json`. Add email alerting via `smtplib`. Curate manufacturer data CSVs as a parallel track.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** All 7 configured sources are active (BSEE, EIA US, SODIR, Metocean, Brazil ANP, UKCS, LNG Terminals). Tier 1 priority: EIA first (most complete existing code), then BSEE, then SODIR. Remaining 4 are tier 2 (best-effort this phase).
- **D-02:** EIA uses public endpoints only -- no API key required.
- **D-03:** SODIR is a stub -- needs building from scratch against factpages.sodir.no.
- **D-04:** Symlink `worldenergydata/data/modules/` -> `/mnt/ace/worldenergydata/data/modules/`. Single source of truth for large datasets. Remove in-repo data, replace with symlink.
- **D-05:** New pipelines write Parquet output. Existing .bin (pickle) data stays as-is until loaders are updated. No full migration this phase.
- **D-06:** Curated manufacturer/standards data uses CSV with Pydantic validation, stored in-repo under `data/modules/` (small files stay in git).
- **D-07:** Tier 1 -- Public API feeds (BSEE, EIA, SODIR, etc.) auto-refreshed via scheduler.
- **D-08:** Tier 2 -- Curated manufacturer data (riser specs, rigid jumper catalogs, mooring components, subsea structure inventories) as CSV + Pydantic models.
- **D-09:** Tier 3 -- Standards-extracted data (tables, coefficients, design factors from DNV, API, ASME, ISO codes). Ingested as-encountered.
- **D-10:** BSEE platform structures (SS type code), pipeline permits/locations, and deepwater structures feed into digitalmodel for analysis. Wire existing scrapers into scheduler for auto-refresh.
- **D-11:** Curate manufacturer data for: risers, rigid jumpers, umbilicals, manifolds, subsea templates, mooring components. Follow existing `drilling_riser_components.csv` pattern.
- **D-12:** BSEE does NOT provide component-level subsea specs -- only installation-level data. Component specs come from manufacturer catalogs and standards bodies.
- **D-13:** Staleness defined per source cadence: SODIR daily, BSEE weekly, EIA monthly. Not a universal 24hr window.
- **D-14:** Measured by last successful run timestamp in status.json. Stale = last_success older than expected interval + buffer.
- **D-15:** Email alerts via SMTP configured in .env (SMTP_HOST, SMTP_USER, SMTP_PASS).
- **D-16:** Alert triggers: (1) job failure after all retry attempts, (2) staleness threshold breached. Partial success (0 records) does NOT trigger alerts.
- **D-17:** Common adapter pattern for all sources: download -> validate -> write Parquet -> update state. Reuse existing `AbstractJob` base class and `JobResult` dataclass.
- **D-18:** EIA adapter first (most complete existing code -- client, ingestion, state tracking). Proves the pattern, then replicate for BSEE and SODIR.

### Claude's Discretion
- Failure handling strategy for missed cadence (retry policy, escalation thresholds)
- Curated data freshness tracking (whether to surface reports for stale CSVs)
- Deployment sequencing (code-first vs full systemd deployment)
- Tier-2 source implementation depth (full working adapters vs pattern scaffolding)
- Output format per source (Parquet vs JSONL for EIA migration)
- Dashboard/status page approach

### Deferred Ideas (OUT OF SCOPE)
- Full pickle-to-Parquet migration for existing BSEE .bin data
- BSEE pipeline inspection data -- not available from public portal
- Structural condition/assessment data -- BSEE only tracks permits, not condition
- Nightly research automation -- Phase 5
</user_constraints>

## Standard Stack

### Core (Already in Project)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| schedule | 1.2.2 | Job scheduling in DataScheduler | Already imported and used; simple cron-like scheduling |
| requests | (installed) | HTTP client for EIA, BSEE, SODIR | Already used throughout all data clients |
| pyarrow | 23.0.0 | Parquet read/write | Already in pyproject.toml; D-05 requires Parquet output |
| pandas | >=2.0.0 | DataFrame operations, Parquet I/O via pyarrow | Already a dependency; `df.to_parquet()` with pyarrow engine |
| pydantic | >=2.5.0 | Validation for curated CSV data | Already used for config; D-06 requires Pydantic validation |
| pydantic-settings | >=2.1.0 | Environment-based config (Settings class) | Already powers `common/config.py` |
| loguru | >=0.7.0 | Structured logging in BSEE scraper | Already used; mix with stdlib logging in scheduler |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| smtplib | stdlib | Email alerts (D-15) | Send SMTP email on failure/staleness |
| email.mime | stdlib | Email message construction | Build HTML/text alert emails |
| zipfile | stdlib | Extract BSEE zip downloads | Process BSEE scraper output |
| io.BytesIO | stdlib | In-memory zip processing | BSEE downloads to memory, not disk |

### Missing Dependency (Must Fix)
| Library | Issue | Action |
|---------|-------|--------|
| schedule | Used in `scheduler.py` but NOT in `pyproject.toml` | Add `"schedule>=1.2.0"` to dependencies |

**Installation:** No new packages needed. Fix `schedule` declaration in `pyproject.toml`.

## Architecture Patterns

### Existing Project Structure (Relevant Paths)
```
worldenergydata/
  config/scheduler/scheduler_config.yml     # Job definitions, intervals
  src/worldenergydata/
    scheduler/
      scheduler.py       # DataScheduler (working)
      config.py          # YAML loader (working)
      monitor.py         # JobLogger, RetryManager, StatusReporter (working)
      jobs/
        base.py          # AbstractJob + JobResult (working)
        eia_us_refresh.py    # STUB -- needs wiring to EIA client
        bsee_refresh.py      # STUB -- needs wiring to BSEE scraper
        sodir_refresh.py     # STUB -- needs building from scratch
        metocean_refresh.py  # Tier 2
        brazil_anp_refresh.py # Tier 2
        ukcs_refresh.py      # Tier 2
        lng_terminals_refresh.py # Tier 2
    eia/
      client.py          # EIAFeedClient (working, paginated)
      ingestion.py       # EIAIngestionSync + EIAIngestionState (working)
    bsee/data/scrapers/
      bsee_web.py        # BSEEWebScraper (working, 8 download URLs)
    bsee/data/loaders/infrastructure/
      platform_loader.py # Platform structure loader (working)
      pipeline_loader.py # Pipeline data loader (working)
    sodir/
      api_client.py      # SodirAPIClient (working, rate-limited, cached)
      endpoints.py       # SODIR endpoint definitions (working)
    common/
      config.py          # Settings with WED_ prefix (working)
  data/modules/vessel_fleet/curated/
    drilling_riser_components.csv  # Template for curated data
  systemd/
    worldenergydata-scheduler.service  # systemd unit (template)
```

### Pattern 1: Adapter Wiring (EIA Example)
**What:** Connect existing client/ingestion code to the stub job adapter
**When to use:** Every Tier 1 source follows this pattern
**Example:**
```python
# eia_us_refresh.py -- wire EIAIngestionSync into the AbstractJob adapter
from worldenergydata.eia.ingestion import EIAIngestionSync
from worldenergydata.scheduler.jobs.base import AbstractJob, JobResult

class EiaUsRefreshJob(AbstractJob):
    name = "eia_us_refresh"

    def run(self, config: dict) -> JobResult:
        start = datetime.now()
        try:
            sync = EIAIngestionSync(
                api_key=config.get("api_key"),
                output_dir=Path(config.get("output_dir", "data/eia")),
            )
            results = sync.run_all()
            total_records = sum(r["records_written"] for r in results)
            return JobResult(
                job_name=self.name, start_time=start,
                end_time=datetime.now(), status="success",
                records_updated=total_records, error_msg=None,
            )
        except Exception as exc:
            return JobResult(
                job_name=self.name, start_time=start,
                end_time=datetime.now(), status="failure",
                records_updated=0, error_msg=str(exc),
            )
```

### Pattern 2: Download-Validate-Parquet (BSEE Example)
**What:** Download zip -> extract -> validate with pandas -> write Parquet
**When to use:** BSEE and similar bulk-download sources
**Example:**
```python
# Within BseeRefreshJob.run():
scraper = BSEEWebScraper()
zip_bytes = scraper.download_platform_data()
if zip_bytes is None:
    raise RuntimeError("BSEE platform download failed")
with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
    csv_name = zf.namelist()[0]
    df = pd.read_csv(zf.open(csv_name))
# Validate, clean, write Parquet
output_path = data_dir / "bsee_platform_structures.parquet"
df.to_parquet(output_path, engine="pyarrow", index=False)
```

### Pattern 3: Staleness Check
**What:** Compare last_success timestamp against source cadence + buffer
**When to use:** Monitoring/alerting checks
**Example:**
```python
STALENESS_THRESHOLDS = {
    "sodir_refresh": timedelta(hours=36),   # daily + 12h buffer
    "bsee_refresh": timedelta(days=10),     # weekly + 3d buffer
    "eia_us_refresh": timedelta(days=45),   # monthly + 15d buffer
}

def check_staleness(status: dict) -> list[str]:
    stale = []
    now = datetime.now()
    for job_name, threshold in STALENESS_THRESHOLDS.items():
        job_status = status["jobs"].get(job_name, {})
        last_run = job_status.get("last_run")
        if last_run is None or (now - datetime.fromisoformat(last_run)) > threshold:
            stale.append(job_name)
    return stale
```

### Pattern 4: Curated CSV + Pydantic Validation
**What:** CSV file with Pydantic model validation at load time
**When to use:** Manufacturer data, standards tables (D-06, D-08, D-09)
**Example:**
```python
# Follow existing drilling_riser.py pattern
from pydantic import BaseModel, field_validator

class RigidJumperSpec(BaseModel):
    component_id: str
    manufacturer: str
    od_in: float
    wall_thickness_in: float
    length_ft: float
    material_grade: str
    pressure_rating_psi: float
    data_source: str

def load_rigid_jumpers(csv_path: Path) -> list[RigidJumperSpec]:
    df = pd.read_csv(csv_path)
    return [RigidJumperSpec(**row) for _, row in df.iterrows()]
```

### Anti-Patterns to Avoid
- **Monolithic adapter:** Do not put all BSEE dataset downloads in one `run()` call. Download each dataset type (platform, pipeline, deepwater) independently so partial failures do not block everything.
- **Hardcoded paths:** Use `Settings.data_dir` and `get_module_data_dir()` -- never hardcode `/mnt/ace/` in source code.
- **Blocking retries in job.run():** The scheduler's `RetryManager` already handles retries with exponential backoff. Do not add a second retry layer inside the adapter.
- **Mixing loguru and stdlib logging:** BSEE scraper uses `loguru`; scheduler uses stdlib `logging`. Keep adapter code on stdlib logging to match scheduler patterns. Do not mix.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Job scheduling | Custom cron loop | `schedule` library (already used) | Tested, handles edge cases around DST/missed ticks |
| Retry with backoff | Custom retry loop | `RetryManager` (already exists) | Exponential backoff already implemented |
| Parquet I/O | Custom binary serialization | `pandas.DataFrame.to_parquet()` + pyarrow | Columnar, compressed, schema-preserving |
| SMTP email | Custom socket-level SMTP | `smtplib.SMTP` + `email.mime` | Stdlib, handles auth, TLS, MIME correctly |
| ZIP extraction | Streaming decompression | `zipfile.ZipFile(io.BytesIO(...))` | Stdlib, handles in-memory extraction |
| HTTP pagination | Manual offset loop | `EIAFeedClient._get()` (already exists) | Pagination, rate-limit handling already coded |
| Config management | Custom env parsing | `pydantic-settings` (already used) | Existing `Settings` class, `.env` support |

**Key insight:** Almost all infrastructure exists. The work is wiring, not building.

## Common Pitfalls

### Pitfall 1: EIA API Key Contradiction
**What goes wrong:** D-02 states "EIA uses public endpoints only -- no API key required." However, the existing `EIAFeedClient` raises `EIAKeyError` if no key is provided, and EIA's official documentation confirms API keys are mandatory for all v2 API requests.
**Why it happens:** D-02 likely refers to the intent to use free/public data (not private/premium feeds), not that authentication is skipped.
**How to avoid:** Register for a free EIA API key (instant, automated). Store in `.env` as `EIA_API_KEY`. The adapter must handle this gracefully.
**Warning signs:** `EIAKeyError` raised on first run attempt.

### Pitfall 2: SODIR API URL Migration
**What goes wrong:** The existing `SodirAPIClient` uses `factpages.sodir.no` as base URL. SODIR migrated services to `factmaps.sodir.no/api/rest/` in 2025, with old URLs removed May 2025.
**Why it happens:** The endpoint definitions in `endpoints.py` reference old API paths.
**How to avoid:** Verify the SODIR API base URL against current documentation. The new data service is at `https://factmaps.sodir.no/api/rest/services/DataService/data`. Update `Settings.api.sodir_base_url` and `endpoints.py` accordingly.
**Warning signs:** HTTP 404 or connection errors on SODIR requests.

### Pitfall 3: BSEE Download Size and Timeouts
**What goes wrong:** BSEE production data can be 50+ MB, WAR data 100+ MB. Downloads time out.
**Why it happens:** Default HTTP timeout insufficient for large files.
**How to avoid:** The `BSEEWebScraper` already handles this with adaptive timeouts (up to 2400s for WAR data) and streaming downloads. Use the existing scraper, do not bypass it.
**Warning signs:** `requests.exceptions.Timeout` in scheduler logs.

### Pitfall 4: Symlink Before Data Exists
**What goes wrong:** Creating symlink `data/modules/ -> /mnt/ace/worldenergydata/data/modules/` fails if the target directory does not exist or if there is already data at the source path.
**Why it happens:** Order of operations -- must create target dir, move data, then create symlink.
**How to avoid:** (1) Create `/mnt/ace/worldenergydata/data/modules/` if missing. (2) Move existing in-repo data to that location. (3) Remove `data/modules/` dir. (4) Create symlink. (5) Add `data/modules` to `.gitignore`.
**Warning signs:** `FileExistsError` or broken symlink.

### Pitfall 5: schedule Library Not in pyproject.toml
**What goes wrong:** Fresh `uv sync` or CI install misses the `schedule` package; scheduler import fails.
**Why it happens:** `schedule` is used in `scheduler.py` but never declared as a dependency.
**How to avoid:** Add `"schedule>=1.2.0"` to `pyproject.toml` dependencies immediately.
**Warning signs:** `ModuleNotFoundError: No module named 'schedule'` on clean install.

### Pitfall 6: Dual EIA Client Implementations
**What goes wrong:** There are two separate EIA client implementations: `eia/client.py` (EIAFeedClient) and `eia_us/client/eia_api.py` (EIAApiClient). Tests reference the latter; ingestion uses the former.
**Why it happens:** Organic codebase growth with two separate development efforts.
**How to avoid:** Use `eia/client.py` + `eia/ingestion.py` for the scheduler adapter (D-18 says this is the most complete). Do not introduce a third implementation.
**Warning signs:** Confusion about which client to import.

## Code Examples

### Email Alert Sender (D-15, D-16)
```python
# Source: stdlib smtplib pattern
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertSender:
    def __init__(self, smtp_host: str, smtp_user: str, smtp_pass: str,
                 smtp_port: int = 587, recipients: list[str] = None):
        self.smtp_host = smtp_host
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.smtp_port = smtp_port
        self.recipients = recipients or [smtp_user]

    def send_alert(self, subject: str, body: str) -> None:
        msg = MIMEMultipart()
        msg["From"] = self.smtp_user
        msg["To"] = ", ".join(self.recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
```

### Staleness-Aware StatusReporter Extension
```python
# Extend existing StatusReporter to include staleness checks
def check_and_alert(self, results: list[JobResult], alert_sender: AlertSender):
    self.write_status(results)
    # Check for failures after all retries
    failures = [r for r in results if r.status == "failure"]
    for f in failures:
        alert_sender.send_alert(
            f"[WED] Job FAILED: {f.job_name}",
            f"Job {f.job_name} failed at {f.end_time}.\nError: {f.error_msg}"
        )
    # Check staleness against thresholds
    stale_jobs = check_staleness(self._read_status())
    for job_name in stale_jobs:
        alert_sender.send_alert(
            f"[WED] Data STALE: {job_name}",
            f"Job {job_name} has not completed within expected cadence."
        )
```

### Parquet Output Helper
```python
# Standardized Parquet output for all adapters
import pandas as pd
from pathlib import Path

def write_parquet(df: pd.DataFrame, output_dir: Path, filename: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    df.to_parquet(output_path, engine="pyarrow", index=False,
                  compression="snappy")
    return output_path
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SODIR at factpages.sodir.no | SODIR at factmaps.sodir.no/api/rest/ | May 2025 | Old endpoints removed; update base URL |
| EIA API v1 | EIA API v2.1.0 | March 2023 | Client already uses v2; no change needed |
| Pickle (.bin) for BSEE | Parquet for new pipelines (D-05) | This phase | New adapters write Parquet; old .bin stays |

**Deprecated/outdated:**
- SODIR `factpages.sodir.no` API paths: removed May 2025, use `factmaps.sodir.no`
- EIA API v1: fully deprecated

## Open Questions

1. **EIA API Key vs D-02 "no API key"**
   - What we know: EIA API v2 requires a free API key for all requests. The existing client enforces this.
   - What's unclear: Whether D-02 means "no paid/premium key" or literally "no key at all."
   - Recommendation: Register for free EIA API key. Add to `.env`. The adapter should read from `EIA_API_KEY` env var. This is compatible with "public endpoints only" intent. Flag to user if there's a mismatch with their expectation.

2. **SODIR New API Schema**
   - What we know: New base URL is `factmaps.sodir.no/api/rest/`. Metadata endpoint exists.
   - What's unclear: Whether the endpoint IDs in `endpoints.py` (1001, 5000, 7100, etc.) map to the new API or need updating.
   - Recommendation: Hit the metadata endpoint first to discover available tables, then map to existing endpoint definitions.

3. **EIA Output Format: JSONL vs Parquet**
   - What we know: Existing ingestion writes JSONL. D-05 says new pipelines write Parquet.
   - What's unclear: Whether EIA should continue JSONL (working) or migrate to Parquet.
   - Recommendation (Claude's discretion): Keep JSONL for incremental append (its natural format), add a Parquet export step for downstream consumption. Both formats serve different purposes.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All code | Yes | 3.13.12 | -- |
| uv | Package management | Yes | 0.10.0 | -- |
| pytest | Testing | Yes | 9.0.2 | -- |
| pyarrow | Parquet output (D-05) | Yes | 23.0.0 | -- |
| schedule | Scheduler | Yes (installed) | 1.2.2 | -- (but must add to pyproject.toml) |
| /mnt/ace/ | Data storage (D-04) | Needs verification at runtime | -- | Use local data dir |
| SMTP server | Email alerts (D-15) | Needs .env config | -- | Log-only alerts as fallback |
| EIA API key | EIA ingestion | Needs .env config | -- | Bulk download fallback |

**Missing dependencies with no fallback:**
- None blocking. EIA API key is free to obtain.

**Missing dependencies with fallback:**
- `/mnt/ace/` availability: if not mounted, fall back to local `data/modules/` without symlink
- SMTP config: if not configured, log alerts to file instead of sending email

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | `worldenergydata/pyproject.toml` (pytest section assumed) |
| Quick run command | `cd worldenergydata && uv run pytest tests/unit/scheduler/ -x -q` |
| Full suite command | `cd worldenergydata && uv run pytest tests/unit/scheduler/ tests/unit/eia_us/ -x -q` |

### Existing Test Coverage
| Area | Tests Exist? | File |
|------|-------------|------|
| DataScheduler registration/run_once/status/start-stop | Yes | `tests/unit/scheduler/test_scheduler.py` (12 tests) |
| EIA API client (cache, rate limit) | Yes | `tests/unit/eia_us/test_eia_api_client.py` |
| SODIR processors and API client | Yes | `tests/unit/sodir/` (20+ test files) |
| BSEE analysis | Yes | `tests/unit/bsee/` (many test files) |
| Job adapters (eia_us_refresh, bsee_refresh, sodir_refresh) | No | -- |
| Email alerting | No | -- |
| Staleness checking | No | -- |
| Parquet output | No | -- |
| Curated CSV validation | No | -- |

### Phase Requirements -> Test Map
| Behavior | Test Type | Automated Command | File Exists? |
|----------|-----------|-------------------|-------------|
| EIA adapter fetches data and writes output | unit (mock HTTP) | `uv run pytest tests/unit/scheduler/test_eia_adapter.py -x` | No -- Wave 0 |
| BSEE adapter downloads and writes Parquet | unit (mock scraper) | `uv run pytest tests/unit/scheduler/test_bsee_adapter.py -x` | No -- Wave 0 |
| SODIR adapter fetches from new API | unit (mock HTTP) | `uv run pytest tests/unit/scheduler/test_sodir_adapter.py -x` | No -- Wave 0 |
| Staleness check detects stale sources | unit | `uv run pytest tests/unit/scheduler/test_staleness.py -x` | No -- Wave 0 |
| Email alerts fire on failure/staleness | unit (mock SMTP) | `uv run pytest tests/unit/scheduler/test_alerts.py -x` | No -- Wave 0 |
| Curated CSV validates against Pydantic model | unit | `uv run pytest tests/unit/curated/test_csv_validation.py -x` | No -- Wave 0 |
| Parquet output is valid and readable | unit | `uv run pytest tests/unit/scheduler/test_parquet_output.py -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `cd worldenergydata && uv run pytest tests/unit/scheduler/ -x -q`
- **Per wave merge:** `cd worldenergydata && uv run pytest tests/unit/scheduler/ tests/unit/eia_us/ tests/unit/sodir/ -x -q`
- **Phase gate:** Full scheduler + adapter + alert test suite green

### Wave 0 Gaps
- [ ] `tests/unit/scheduler/test_eia_adapter.py` -- EIA adapter wiring
- [ ] `tests/unit/scheduler/test_bsee_adapter.py` -- BSEE adapter wiring
- [ ] `tests/unit/scheduler/test_sodir_adapter.py` -- SODIR adapter wiring
- [ ] `tests/unit/scheduler/test_staleness.py` -- staleness check logic
- [ ] `tests/unit/scheduler/test_alerts.py` -- email alert sending
- [ ] `tests/unit/scheduler/test_parquet_output.py` -- Parquet write/read roundtrip
- [ ] Fix `schedule` missing from `pyproject.toml`

## Discretion Recommendations

Based on research, here are recommendations for areas marked as Claude's discretion:

1. **Failure handling:** Use existing `RetryManager` (3 retries, 60s backoff). Escalation: after all retries exhausted, fire email alert. No further escalation needed for v1.
2. **Curated data freshness:** Do not track staleness for curated CSVs -- they are manually authored and have no expected cadence. Only track Tier 1 API sources.
3. **Deployment sequencing:** Code-first. Get adapters working and tested before touching systemd. Systemd deployment is a final task.
4. **Tier-2 sources:** Scaffolding only. Create the adapter file with proper structure and clear TODO comments, but do not implement full data fetching for metocean/ANP/UKCS/LNG this phase.
5. **EIA output format:** Dual output. Keep JSONL for incremental ingestion (append-friendly), add Parquet snapshot for downstream consumers.
6. **Dashboard/status page:** No dashboard this phase. `status.json` + email alerts is sufficient. A status page can be added in a later phase with the existing `dash` dependency.

## Sources

### Primary (HIGH confidence)
- Codebase inspection: all files listed in CONTEXT.md canonical references were read directly
- `pyproject.toml`: dependency list verified
- Installed package versions: `schedule 1.2.2`, `pyarrow 23.0.0` verified via pip

### Secondary (MEDIUM confidence)
- [EIA API documentation](https://www.eia.gov/opendata/documentation.php) -- API key required for all v2 requests
- [SODIR FactPages technical info](https://www.sodir.no/en/facts/data-and-analyses/open-data/factpages-and-factmaps-technical-information/) -- new API URLs
- [SODIR new URLs announcement](https://www.sodir.no/en/facts/data-and-analyses/open-data/factpages-and-factmaps-technical-information/2026/new-urls-for-map-applications/) -- migration from factpages to factmaps

### Tertiary (LOW confidence)
- SODIR new API endpoint structure -- could not fully verify endpoint ID mappings against new URL; needs runtime validation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already in project, versions verified
- Architecture: HIGH -- patterns derived from reading actual codebase, not speculation
- Pitfalls: HIGH -- found by comparing CONTEXT.md claims against actual code and official docs
- SODIR API migration: MEDIUM -- confirmed URL change, but endpoint mapping needs verification

**Research date:** 2026-03-25
**Valid until:** 2026-04-25 (stable domain, no fast-moving dependencies)
