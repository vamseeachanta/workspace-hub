# Oil & Gas Well Data Sources Research & Integration Plan

> **Title**: Multi-Regional Oil & Gas Well Data Integration
> **Version**: 1.0.0
> **Module**: data-sources
> **Created**: 2026-01-26
> **Status**: Planning

---

## Executive Summary

This plan outlines the research findings and implementation strategy for integrating oil and gas well data from five target regions: Texas (RRC), Canada (AER/BCER), Mexico (CNH), Norway (SODIR), and Landman data providers.

**Key Finding**: Norway SODIR integration already exists in `tests/modules/sodir-integration/` and needs promotion to production.

---

## 1. Research Findings Summary

### Data Source Comparison Matrix

| Source | Auth | API Type | Format | Update Freq | Coverage | Complexity |
|--------|------|----------|--------|-------------|----------|------------|
| **Texas RRC** | None | Web/CSV | CSV, PDF | Monthly | Complete | Medium |
| **Canada AER** | None | REST/CSV | CSV, JSON | Daily | Complete | Medium |
| **Canada BCER** | None | WFS/REST | GeoJSON | Regular | Surface only | Low |
| **Mexico CNH** | None | Dashboard | Excel, PDF | Varies | 35k+ wells | High |
| **Norway SODIR** | None | REST API | JSON, CSV | Daily | Excellent | Low |
| **Landman** | API Key | REST | JSON | Varies | Title/ownership | High |

### Existing Codebase Patterns

The worldenergydata codebase uses:
- **Protocol-based interfaces**: `DataSourceProtocol`, `ProcessorProtocol`, `ValidatorProtocol`
- **Router pattern**: Configuration-driven data orchestration
- **Module structure**: `data/`, `processors/`, `analysis/`, `validators.py`
- **Error hierarchy**: Module-specific exception classes

---

## 2. Implementation Plan

### Phase 1: Promote SODIR Module (1-2 days)

**Status**: Already implemented in tests, needs promotion

**Tasks**:
1. Move `tests/modules/sodir-integration/sodir_module/` to `src/worldenergydata/modules/sodir/`
2. Update import paths throughout
3. Add routing in `engine.py`
4. Move config from `tests/modules/sodir-integration/configs/sodir.yml` to `config/sodir.yml`
5. Add CLI commands in `src/worldenergydata/cli/commands/sodir.py`

**Files to modify**:
- `src/worldenergydata/engine.py` - Add SODIR routing
- `src/worldenergydata/common/exceptions.py` - Verify SODIRError exists
- `config/sodir.yml` - Move configuration

---

### Phase 2: Texas Railroad Commission (3-5 days)

**Data Portal**: https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/

**Integration Strategy**: CSV Download + Web Scraping Hybrid

**Module Structure**:
```
src/worldenergydata/modules/texas_rrc/
├── __init__.py
├── texas_rrc.py           # Main router
├── api_client.py          # HTTP client for downloads/scraping
├── data/
│   ├── loaders/
│   │   ├── production/    # Monthly CSV downloads
│   │   ├── wells/         # Well records
│   │   └── surveys/       # Directional surveys (web scrape)
├── processors/
│   ├── production_processor.py
│   ├── well_processor.py
│   └── survey_processor.py
├── validators.py
└── errors.py
```

**Data Model**:
- API Number format: `42-XXX-XXXXX-XX-XX` (Texas state code 42)
- Units: Imperial (feet, barrels, mcf)
- Districts: 01-12 (including 7B, 7C, 8, 8A)

**Existing Tools to Leverage**:
- [rrc-scraper](https://github.com/derrickturk/rrc-scraper) - Production data scraper
- [TXRRC_data_harvest](https://github.com/mlbelobraydi/TXRRC_data_harvest) - Well data scripts

**Configuration** (`config/texas_rrc.yml`):
```yaml
module: texas_rrc
api:
  base_url: https://www.rrc.texas.gov
  rate_limit: 5
  cache_ttl: 86400
data_types:
  production: { enabled: true, source: csv_download }
  wells: { enabled: true, source: csv_download }
  directional_surveys: { enabled: true, source: web_scrape }
```

---

### Phase 3: Canada Integration (4-6 days)

#### 3A. Alberta Energy Regulator (AER/Petrinex)

**Data Portal**: https://www.aer.ca/ | https://www.petrinex.ca/PD/Pages/APD.aspx

**Integration Strategy**: CSV bulk downloads + Open Data API

**Module Structure**:
```
src/worldenergydata/modules/canada/
├── __init__.py
├── canada.py              # Main router (orchestrates both provinces)
├── aer/                   # Alberta
│   ├── api_client.py      # Petrinex/Open Data access
│   ├── data/loaders/
│   └── processors/
├── bcer/                  # British Columbia
│   ├── api_client.py      # WFS/REST client
│   ├── data/loaders/
│   └── processors/
└── common/
    ├── uwi_parser.py      # Unique Well Identifier parsing
    └── coordinate_systems.py
```

**Data Model**:
- UWI Format: `AA/BB-CC-DDD-EEFFGG/W`
- Units: Metric (meters, cubic meters)
- Coordinate System: NAD83(CSRS) - EPSG:4617

#### 3B. BC Energy Regulator (BCER)

**Data Portal**: https://data-bc-er.opendata.arcgis.com/

**APIs Available**:
- GeoServices REST API
- WFS (Web Feature Service)
- WMS (Web Mapping Service)

---

### Phase 4: Mexico CNH (5-7 days)

**Data Portal**: https://sih.hidrocarburos.gob.mx/

**Integration Strategy**: Selenium-based dashboard scraping + Excel/PDF parsing

**Challenges**:
- No official API - requires browser automation
- Spanish-language interface
- Dashboard can be slow/unreliable

**Module Structure**:
```
src/worldenergydata/modules/mexico_cnh/
├── __init__.py
├── mexico_cnh.py          # Main router
├── api_client.py          # Selenium-based client
├── data/
│   ├── loaders/
│   │   ├── sih_loader.py      # Dashboard scraper
│   │   ├── excel_loader.py    # Excel downloads
│   │   └── pdf_parser.py      # Report extraction
├── processors/
└── errors.py
```

**Data Model**:
- Identifier: Clave del Pozo (well key)
- Units: Metric (meters, barrels for oil, mmscf for gas)
- Coordinates: UTM Zone 14/15

**Dependencies to Add**:
- `selenium` - Browser automation
- Chrome/Chromium driver

---

### Phase 5: Landman Data (3-5 days)

**Primary Providers**:
- Landman.ai - https://landman.ai/
- TaxNetUSA - https://www.taxnetusa.com/
- County records (free, limited)

**Integration Strategy**: Provider abstraction pattern with subscription support

**Module Structure**:
```
src/worldenergydata/modules/landman/
├── __init__.py
├── landman.py             # Main router
├── providers/
│   ├── base_provider.py   # Abstract interface
│   ├── landman_ai.py      # Landman.ai integration
│   ├── taxnetusa.py       # TaxNetUSA integration
│   └── county_records.py  # Free public records
├── data/loaders/
├── processors/
└── auth/
    └── api_key_manager.py
```

**Security Requirements**:
- API keys from environment variables only
- Encrypted cache for proprietary data
- Audit logging for data access

**Data Model**:
- Mineral ownership records
- Lease records (royalty rates, terms)
- Title chain documents

---

## 3. Cross-Regional Analysis Framework

Add unified comparison capabilities:

```
src/worldenergydata/analysis/cross_regional.py
├── compare_drilling_metrics()    # Depth, duration, cost
├── benchmark_production()        # Production rates across regions
├── normalize_identifiers()       # API, UWI, Clave del Pozo mapping
└── convert_units()               # Imperial/Metric standardization
```

---

## 4. Configuration Changes

### New Exception Classes

Add to `src/worldenergydata/common/exceptions.py`:
- `TexasRRCError`
- `CanadaAERError`
- `CanadaBCERError`
- `MexicoCNHError`
- `LandmanError`

### API Settings Extension

Add to `src/worldenergydata/common/config.py`:
```python
# Texas RRC
texas_rrc_base_url: str = "https://www.rrc.texas.gov"

# Canada
aer_base_url: str = "https://www.aer.ca"
bcer_base_url: str = "https://www.bc-er.ca"

# Mexico
cnh_base_url: str = "https://sih.hidrocarburos.gob.mx"
```

---

## 5. Testing Strategy

### Unit Tests
- Data model validation (API numbers, UWI, Clave del Pozo)
- Unit conversions (feet↔meters, barrels↔cubic meters)
- Coordinate transformations (UTM, NAD83, WGS84)

### Integration Tests
- API connectivity (with mocked responses for CI)
- Data parsing accuracy
- Cross-regional identifier mapping

### Slow/Optional Tests
- Full scraping tests (Selenium for CNH)
- Live API tests (require credentials for Landman)

---

## 6. Verification Plan

### Per-Module Verification

1. **SODIR Promotion**:
   ```bash
   uv run pytest tests/modules/sodir/ -v
   uv run python -m worldenergydata.cli sodir collect --data-types wellbores
   ```

2. **Texas RRC**:
   ```bash
   uv run pytest tests/modules/texas_rrc/ -v
   # Verify CSV download and parsing
   ```

3. **Canada**:
   ```bash
   uv run pytest tests/modules/canada/ -v
   # Test UWI parsing and API connectivity
   ```

4. **Mexico CNH**:
   ```bash
   uv run pytest tests/modules/mexico_cnh/ -v --slow
   # Selenium tests marked as slow
   ```

5. **Landman**:
   ```bash
   uv run pytest tests/modules/landman/ -v
   # Skip integration tests without API keys
   ```

### End-to-End Verification

```bash
# Cross-regional comparison test
uv run python -c "
from worldenergydata.analysis.cross_regional import CrossRegionalAnalysis
analysis = CrossRegionalAnalysis()
result = analysis.compare_drilling_metrics(['bsee', 'sodir', 'texas_rrc'])
print(result.head())
"
```

---

## 7. Dependencies

### Required (Already Installed)
- `pandas`, `numpy` - Data processing
- `httpx` or `requests` - HTTP clients
- `pydantic` - Configuration validation
- `pdfplumber` - PDF parsing (for CNH/RRC)

### To Add
- `selenium` - For Mexico CNH dashboard scraping
- `webdriver-manager` - Chrome driver management

---

## 8. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Website rate limiting | High | Medium | Conservative limits, exponential backoff |
| Dashboard changes (CNH) | High | High | Page object pattern, version detection |
| API key exposure | Medium | Critical | Environment variables only, audit logging |
| Large dataset memory | Medium | High | Chunked processing, streaming |
| Data format changes | Medium | High | Schema validation, graceful degradation |

---

## 9. Implementation Priority

**Confirmed Order** (per user decision):

1. **Phase 1**: SODIR promotion (already implemented, quick win)
2. **Phase 2**: Texas RRC (highest value, public data)
3. **Phase 3**: Canada AER/BCER (public APIs, good documentation)
4. **Phase 4**: Mexico CNH (full Selenium integration confirmed)
5. **Phase 5**: Landman (free county records only - no subscriptions available)

**Landman Scope**: Focus on free public county records (TX, NM, OK, ND, CO) until subscriptions are acquired.

---

## 10. Critical Files

| File | Purpose |
|------|---------|
| `src/worldenergydata/common/types.py` | Core protocols to implement |
| `src/worldenergydata/common/exceptions.py` | Add new module errors |
| `src/worldenergydata/engine.py` | Register new module routing |
| `tests/modules/sodir-integration/` | Reference implementation |
| `config/*.yml` | Module configurations |
