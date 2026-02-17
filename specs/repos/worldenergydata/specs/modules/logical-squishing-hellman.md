# Enhance Incident Data Collection from Public Sources

> **Module**: marine_safety, hse
> **Version**: 1.0.0
> **Status**: Planning
> **Created**: 2026-01-26

## Overview

Enhance the incident data collection infrastructure to integrate additional public data sources beyond the current marine casualty data. The goal is to provide comprehensive global incident coverage from multiple maritime safety authorities.

## Current State

### Implemented Data Sources (Production-Ready)
| Source | Importer | Status |
|--------|----------|--------|
| USCG MISLE | `misle_importer.py` | Production |
| USCG BARD | `boating_importer.py` | Production |
| TSB (Canada) | `tsb_importer.py` | Production |
| MAIB (UK) | `maib_importer.py` | Production |
| NOAA OR&R | `noaa_importer.py` | Production |

### Configured but Not Implemented
| Source | Enum Defined | Importer | CLI |
|--------|--------------|----------|-----|
| NTSB | Yes | No | Stub only |
| ATSB (Australia) | Yes | No | No |
| EMSA (EU) | Yes | No | No |
| IMO GISIS | Yes | No | No |
| BSEE | Yes | No | Stub only |

### Infrastructure Strengths
- `BaseImporter` abstract class with batch processing, duplicate detection
- `BaseScraper` with retry logic, rate limiting, checkpointing
- Pydantic validation models
- 17 incident types, 5 severity levels in `constants.py`
- SQLAlchemy ORM with Incident, Vessel, Location, Company models

## Enhancement Plan

### Phase 1: Complete NTSB Integration (Priority: HIGH)

**Rationale**: CLI stub exists, high-value US federal data source

**Tasks**:
1. Create `ntsb_scraper.py` extending `BaseScraper`
   - Target: https://data.ntsb.gov/carol-main-public (CAROL query system)
   - Features: PDF report extraction, checkpointing, rate limiting
2. Create `ntsb_importer.py` extending `BaseImporter`
   - Field mapping from NTSB format to Incident model
3. Wire to CLI `scrape ntsb` command
4. Add unit and integration tests

**Files to Create**:
- `src/worldenergydata/modules/marine_safety/scrapers/ntsb_scraper.py`
- `src/worldenergydata/modules/marine_safety/importers/ntsb_importer.py`
- `tests/modules/marine_safety/test_ntsb_importer.py`

**Files to Modify**:
- `src/worldenergydata/modules/marine_safety/cli.py` (wire scraper)

---

### Phase 2: IMO GISIS Integration (Priority: HIGH)

**Rationale**: Global incident data, structured format available

**Tasks**:
1. Create `imo_importer.py` extending `BaseImporter`
   - Handle IMO GISIS casualty data format
   - Map flag states, vessel types to existing enums
2. Create `imo_scraper.py` if web scraping needed
3. Add CLI command `scrape imo` / `import imo`
4. Add tests

**Files to Create**:
- `src/worldenergydata/modules/marine_safety/importers/imo_importer.py`
- `tests/modules/marine_safety/test_imo_importer.py`

---

### Phase 3: Australian ATSB Integration (Priority: MEDIUM)

**Rationale**: Southern hemisphere coverage, English-language reports

**Tasks**:
1. Create `atsb_scraper.py` extending `BaseScraper`
   - Target: https://www.atsb.gov.au/publications/investigation_reports/marine
   - PDF report extraction
2. Create `atsb_importer.py` extending `BaseImporter`
3. Add CLI command and tests

**Files to Create**:
- `src/worldenergydata/modules/marine_safety/scrapers/atsb_scraper.py`
- `src/worldenergydata/modules/marine_safety/importers/atsb_importer.py`
- `tests/modules/marine_safety/test_atsb_importer.py`

---

### Phase 4: Cross-Source Correlation Engine (Priority: HIGH)

**Rationale**: Enable linking incidents across data sources by vessel/date/location

**Tasks**:
1. Create `IncidentLink` database model for cross-references
2. Create correlation module with:
   - IMO number matching
   - Vessel name fuzzy matching (Levenshtein distance)
   - Date + location proximity matching
3. Add `correlate` CLI command
4. Add correlation quality metrics

**Files to Create**:
- `src/worldenergydata/modules/marine_safety/analysis/correlation/matcher.py`
- `src/worldenergydata/modules/marine_safety/analysis/correlation/deduplicator.py`
- `tests/modules/marine_safety/test_correlation.py`

**Database Changes**:
```python
class IncidentLink(Base):
    link_id: int  # PK
    incident_id_1: int  # FK -> incidents
    incident_id_2: int  # FK -> incidents
    confidence_score: Decimal(3, 2)  # 0.00 - 1.00
    match_type: str  # 'imo', 'name', 'location', 'date'
    verified: bool
```

---

### Phase 5: Enhanced CLI & Data Quality (Priority: MEDIUM)

**Tasks**:
1. Wire all existing importers to CLI:
   - `import tsb`, `import maib`, `import noaa`, `import misle`
2. Update `stats` command to show actual database counts
3. Create data quality dashboard:
   - Coverage by source/year
   - Completeness metrics
   - Duplicate detection report

**Files to Modify**:
- `src/worldenergydata/modules/marine_safety/cli.py`

**Files to Create**:
- `src/worldenergydata/modules/marine_safety/reports/quality_dashboard.py`

---

### Phase 6: EMSA European Integration (Priority: LOW)

**Rationale**: EU coverage, may require institutional access

**Tasks**:
1. Research EMSA EMCIP database access requirements
2. Create `emsa_importer.py` if data available
3. Alternative: Use EMSA annual reports for statistics

---

## Technical Approach

### Importer Pattern (Follow Existing)
```python
class NewSourceImporter(BaseImporter):
    def read_source(self) -> Iterator[Dict]:
        """Yield raw records from source"""

    def parse_record(self, raw: Dict) -> Dict:
        """Normalize field names and types"""

    def map_to_model(self, parsed: Dict, session) -> Incident:
        """Create database model with relationships"""
```

### Scraper Pattern (Follow Existing)
```python
class NewSourceScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://...",
            rate_limit_delay=2.0,
            max_retries=3
        )

    def scrape(self, start_year, end_year) -> List[Dict]:
        """Main scrape method with checkpointing"""
```

### Validation Requirements
- IMO number: 7-digit checksum validation
- Coordinates: -90 to +90 lat, -180 to +180 lon
- Dates: No future dates, no pre-1900 dates
- Severity: Derive from casualties if not provided

## Verification Plan

### Unit Tests (Per Importer)
1. `test_read_source()` - Generator yields valid records
2. `test_parse_record()` - Field mapping correctness
3. `test_map_to_model()` - Database model creation
4. `test_is_duplicate()` - Duplicate detection

### Integration Tests
1. Database round-trip with test fixtures
2. CLI command execution end-to-end
3. Cross-source correlation accuracy

### Manual Verification
```bash
# Run importer
uv run python -m worldenergydata.marine_safety.cli import ntsb --limit 100

# Check statistics
uv run python -m worldenergydata.marine_safety.cli stats --verbose

# Export and validate
uv run python -m worldenergydata.marine_safety.cli export csv --output test.csv
```

## Critical Files Reference

| File | Purpose |
|------|---------|
| `modules/marine_safety/importers/base_importer.py` | Abstract base class pattern |
| `modules/marine_safety/importers/tsb_importer.py` | Best example of multi-file CSV importer |
| `modules/marine_safety/scrapers/uscg_scraper.py` | Best example of web scraper |
| `modules/marine_safety/database/models.py` | ORM models (add IncidentLink) |
| `modules/marine_safety/constants.py` | Enums and DATA_SOURCE_URLS |
| `modules/marine_safety/cli.py` | CLI framework to wire |

## Dependencies

No new external dependencies required. Existing stack:
- `httpx` - HTTP requests
- `pdfplumber` - PDF extraction
- `pydantic` - Validation
- `sqlalchemy` - ORM
- `click` / `rich` - CLI

## Out of Scope

- Japanese Maritime Accident Database (language barrier)
- Historical data digitization
- Real-time incident alerting
- Machine learning incident prediction

## Estimated Effort

| Phase | Effort |
|-------|--------|
| Phase 1: NTSB | 5 days |
| Phase 2: IMO GISIS | 3 days |
| Phase 3: ATSB | 5 days |
| Phase 4: Correlation | 5 days |
| Phase 5: CLI/Quality | 3 days |
| Phase 6: EMSA | 3 days |
| **Total** | **~24 days** |

## Success Criteria

1. NTSB data imported and queryable via CLI
2. IMO GISIS data integrated with existing models
3. Cross-source correlation identifies matching incidents with >80% accuracy
4. All importers have >80% test coverage
5. CLI provides unified interface for all data sources
