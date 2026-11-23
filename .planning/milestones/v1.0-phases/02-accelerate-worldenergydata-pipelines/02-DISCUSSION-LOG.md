# Phase 2: Accelerate worldenergydata pipelines - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-25
**Phase:** 02-accelerate-worldenergydata-pipelines
**Areas discussed:** Data source scope & priority, Freshness & staleness definition, Alerting & monitoring, Pipeline rebuild strategy

---

## Data Source Scope & Priority

### Active sources

| Option | Description | Selected |
|--------|-------------|----------|
| BSEE (weekly) | US offshore production, wells, incidents | |
| EIA US (monthly) | US energy production/consumption | |
| SODIR (daily) | Norwegian continental shelf data | |
| All 7 sources | BSEE + EIA + SODIR + Metocean + Brazil ANP + UKCS + LNG Terminals | ✓ |

**User's choice:** All 7 sources
**Notes:** All are active but tiered — EIA/BSEE/SODIR are priority tier 1.

### Priority order

| Option | Description | Selected |
|--------|-------------|----------|
| EIA first (Recommended) | Most complete code already exists | ✓ |
| BSEE first | Has pipeline adapters, faster feedback loop | |
| Parallel — all at once | Fix all simultaneously | |

**User's choice:** EIA first

### Remaining source priority

| Option | Description | Selected |
|--------|-------------|----------|
| All equal priority | Every source must be reliable | |
| Tier the remaining 4 | Some are more client-facing | |
| EIA+BSEE+SODIR first | Get those 3 solid first, best-effort rest | ✓ |

**User's choice:** EIA+BSEE+SODIR first

### Data access — /mnt/ace

| Option | Description | Selected |
|--------|-------------|----------|
| Symlink data/modules (Recommended) | Symlink to /mnt/ace, zero code changes | ✓ |
| Set WED_DATA_DIR env var | Point env var to /mnt/ace | |
| Both — symlink + env var | Belt-and-suspenders | |

**User's choice:** Symlink data/modules

### In-repo data cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Replace with symlink | Remove in-repo data, symlink to /mnt/ace | ✓ |
| Keep both | In-repo has smaller subset for quick tests | |

**User's choice:** Replace with symlink

### EIA API key

| Option | Description | Selected |
|--------|-------------|----------|
| I have an API key | Set API_EIA_API_KEY in .env | |
| Public endpoints only | No API key needed | ✓ |

**User's choice:** Public endpoints only

### BSEE data format

| Option | Description | Selected |
|--------|-------------|----------|
| Keep pickle .bin | Existing loaders expect pickle | |
| Migrate to Parquet | More portable, schema-enforced | ✓ |

**User's choice:** Migrate to Parquet (for new pipelines only, existing .bin stays)

### SODIR status

| Option | Description | Selected |
|--------|-------------|----------|
| SODIR is a stub | Needs building from scratch | ✓ |
| SODIR partially works | Some download logic exists | |

**User's choice:** SODIR is a stub

### Curated data format

| Option | Description | Selected |
|--------|-------------|----------|
| CSV with Pydantic validation | Follows existing drilling riser pattern | ✓ |
| Parquet | Matches new pipeline output format | |

**User's choice:** CSV with Pydantic validation

### Curated data location

| Option | Description | Selected |
|--------|-------------|----------|
| /mnt/ace/worldenergydata/data/ | Alongside BSEE data on shared storage | |
| In-repo data/modules/ | Keep curated CSVs in git (small files) | ✓ |

**User's choice:** In-repo data/modules/

### Subsea data scope

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-refresh what BSEE has | Wire platform/pipeline data into scheduler | |
| Also curate manufacturer data | Beyond BSEE: build curated datasets for subsea components | ✓ |

**User's choice:** Also curate manufacturer data — risers, rigid jumpers, umbilicals, manifolds, subsea templates, mooring components

### Additional data tiers (user-initiated)
- User noted: "we need more similar data to feed into digitalmodel for analysis" — expanded scope beyond just API feeds
- User noted: "riser, rigid jumpers; any subsea structures etc." — specific subsea component categories
- User noted: "there will also be data in codes and standards we can bring in as we see it" — opportunistic standards extraction

---

## Freshness & Staleness Definition

### Staleness definition

| Option | Description | Selected |
|--------|-------------|----------|
| Within 24hr of publication | Pipeline picks up new data within 24 hours | |
| All pipelines run daily | Every source checked daily | |
| Match source cadence | SODIR daily, BSEE weekly, EIA monthly | ✓ |

**User's choice:** Match source cadence

### Measurement approach

| Option | Description | Selected |
|--------|-------------|----------|
| Last successful run timestamp | Track when each job last succeeded | ✓ |
| Data recency in output | Check actual data dates in output files | |
| Both | Job run time AND data recency | |

**User's choice:** Last successful run timestamp

---

## Alerting & Monitoring

### Notification method

| Option | Description | Selected |
|--------|-------------|----------|
| Log file only | Check logs manually or via script | |
| Email alerts | Send email on failure/staleness | ✓ |
| Webhook (Slack/Discord) | StatusReporter webhook stub | |

**User's choice:** Email alerts

### Email configuration

| Option | Description | Selected |
|--------|-------------|----------|
| SMTP via .env config | SMTP_HOST, SMTP_USER, SMTP_PASS in .env | ✓ |
| System mail (sendmail) | Local mail system | |

**User's choice:** SMTP via .env config

### Alert triggers

| Option | Description | Selected |
|--------|-------------|----------|
| Job failure after retries | Alert when job fails all retry attempts | ✓ |
| Staleness threshold breached | Alert when last_success exceeds expected interval | ✓ |
| Partial success | Alert on 0 records updated | |

**User's choice:** Job failure after retries + Staleness threshold breached

### Dashboard

**User's choice:** You decide (Claude's discretion)

---

## Pipeline Rebuild Strategy

### Adapter pattern

| Option | Description | Selected |
|--------|-------------|----------|
| Common adapter pattern (Recommended) | download → validate → write Parquet → update state | ✓ |
| Source-specific approaches | Each adapter does what works | |

**User's choice:** Common adapter pattern

### Deployment sequencing

**User's choice:** You decide (Claude's discretion)

### Tier-2 source implementation

**User's choice:** You decide (Claude's discretion)

### Output format consistency

**User's choice:** You decide (Claude's discretion)

---

## Claude's Discretion

- Failure handling for missed cadence
- Curated data freshness tracking
- Deployment sequencing (code-first vs systemd)
- Tier-2 adapter implementation depth
- Output format per source (Parquet vs JSONL migration)
- Dashboard/status page approach

## Deferred Ideas

- Full pickle-to-Parquet migration for existing .bin data
- BSEE inspection/condition data (not available from public portal)
- Nightly research automation (Phase 5)
