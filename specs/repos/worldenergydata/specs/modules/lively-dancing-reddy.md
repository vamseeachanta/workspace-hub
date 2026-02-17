# Metocean Skills Creation Plan

> **Module**: metocean-skills
> **Created**: 2026-01-27
> **Status**: Planning
> **Session ID**: lively-dancing-reddy

## Overview

Create Claude Code skills for metocean (meteorological + oceanographic) data extraction, analysis, statistics, and visualization. These skills will document the existing metocean module capabilities and enable intelligent AI assistance for common metocean workflows.

### Objectives
1. Document existing metocean module for AI skill activation
2. Incorporate external tool patterns (metocean-api, metocean-stats, noaa_coops)
3. Enable advanced statistical analysis and visualization workflows
4. Create intuitive YAML-based configuration patterns

---

## Skills to Create

### Skill 1: `metocean-data-fetcher`
**Purpose**: Fetch real-time and historical metocean data from multiple sources

**Triggers**:
- "Fetch buoy data", "Get wave data", "Download NDBC observations"
- "Get tidal data", "Fetch currents from CO-OPS"
- "Get marine forecast", "Download metocean time series"

**Data Sources**:
| Source | Data Types | API |
|--------|-----------|-----|
| NOAA NDBC | Waves, wind, SST, currents | Text/HTTP |
| NOAA CO-OPS | Tides, currents, water levels | REST JSON |
| Open-Meteo Marine | Wave/wind forecasts | REST JSON |
| IOOS ERDDAP | Buoy, glider, HF radar | ERDDAP |
| MET Norway | Ocean forecasts, NORA3 | REST JSON |

**Key Patterns**:
- Station discovery by region/bbox
- Time series extraction with date ranges
- Multi-source data fusion
- Cache management for efficiency

### Skill 2: `metocean-statistics`
**Purpose**: Statistical analysis of metocean data (extremes, distributions, return periods)

**Triggers**:
- "Calculate extreme wave heights", "Return period analysis"
- "Joint probability distribution", "Fatigue analysis"
- "Monthly statistics", "Seasonal trends"

**Analysis Types**:
- Extreme value analysis (GEV, GPD fitting)
- Return periods (1yr, 10yr, 50yr, 100yr, 500yr)
- Joint probability distributions (wave-wind, Hs-Tp)
- Directional analysis (wave roses, wind roses)
- Temporal statistics (monthly, seasonal, annual)

**Reference Tools**:
- `metocean-stats` (MET-OM) - 95 stars
- `seastats` - Ocean modeling metrics
- NREL floating wind site conditions

### Skill 3: `metocean-visualizer`
**Purpose**: Interactive visualization of metocean data and statistics

**Triggers**:
- "Plot wave data", "Create metocean dashboard"
- "Visualize buoy observations", "Generate wave rose"
- "Time series chart", "Scatter plot Hs vs Tp"

**Visualization Types**:
- Time series plots (multi-parameter)
- Geographic maps (station locations, data overlays)
- Statistical charts (histograms, CDFs, QQ plots)
- Joint distributions (scatter, contour, 2D histograms)
- Directional roses (wave, wind, current)
- Interactive dashboards (Plotly)

**Output Formats**:
- Interactive HTML reports
- Standalone Plotly charts
- Multi-panel dashboards

---

## External Resources Reviewed

### metocean-api (MET Norway)
- Extracts time series from NORA3, ERA5, GTSM, ECHOWAVE
- CSV/NetCDF output, CLI interface
- Key classes: `TimeSeries`, `import_data()`, `combine_data()`

### MET-OM Organization
| Repository | Stars | Purpose |
|-----------|-------|---------|
| metocean-stats | 95 | Statistical analysis |
| dnora | 25 | Wave hindcast downscaling |
| metocean-api | 19 | Data extraction |
| metocean-ml | 3 | Machine learning |

### NREL Site Conditions Dataset
- 4 US floating wind sites (Humboldt, Morro Bay, Gulf of Maine, GOM)
- Metocean time series: wind, waves, currents, temperature
- Summary statistics: extremes up to 500yr return periods
- Joint probability distributions for fatigue

### MetOceanViewer
- Desktop app for ADCIRC model visualization
- NOAA/USGS/NDBC station access
- Map-based visualization with MapBox

---

## User Decisions
- **Organization**: 3 Separate Skills (modular and focused)
- **External Tools**: Full external integration (document how to use alongside module)

---

## Detailed Skill Specifications

### Skill 1: `metocean-data-fetcher` (~350 lines)

**YAML Frontmatter**:
```yaml
name: metocean-data-fetcher
description: Fetch real-time and historical metocean data from NDBC, CO-OPS, Open-Meteo, ERDDAP, and MET Norway. Use for buoy data retrieval, tidal observations, marine forecasts, and multi-source data fusion.
```

**Sections to Include**:
1. When to Use (trigger phrases)
2. Data Sources Table (internal + external)
3. YAML Configuration Templates
   - Single station fetch
   - Regional station discovery
   - Historical time series
   - Multi-source fusion
4. Python API Examples
   - NDBCClient usage
   - COOPSClient for tides
   - OpenMeteoClient for forecasts
   - Data harmonization
5. External Tool Integration
   - `metocean-api` (MET Norway) - NORA3, ERA5, GTSM
   - `noaa_coops` package - Alternative CO-OPS wrapper
   - `erddapy` - Direct ERDDAP access
6. CLI Commands
7. Output Formats (CSV, JSON, NetCDF)
8. Best Practices (caching, rate limits)

### Skill 2: `metocean-statistics` (~400 lines)

**YAML Frontmatter**:
```yaml
name: metocean-statistics
description: Statistical analysis of metocean data including extreme value analysis, return periods, joint probability distributions, and directional statistics. Use for design criteria, fatigue analysis, and operational limits.
```

**Sections to Include**:
1. When to Use (statistical triggers)
2. Analysis Types
   - Temporal statistics (monthly, seasonal, annual)
   - Extreme value analysis (GEV, GPD)
   - Return periods (1-500 years)
   - Joint probability (Hs-Tp, wind-wave)
   - Directional analysis
3. External Tool Integration
   - `metocean-stats` (MET-OM) - Full integration
     - Extreme value fitting
     - Return period tables
     - Contour methods (IFORM, direct sampling)
   - `scipy.stats` - Distribution fitting
   - NREL methodology reference
4. Python API Examples
   - Load data from module
   - Fit extreme distributions
   - Calculate return periods
   - Generate joint distributions
5. YAML Configuration Templates
6. Output Formats
   - Summary statistics CSV
   - Return period tables
   - Design criteria JSON
7. Best Practices

### Skill 3: `metocean-visualizer` (~300 lines)

**YAML Frontmatter**:
```yaml
name: metocean-visualizer
description: Create interactive metocean visualizations including time series plots, wave roses, scatter plots, geographic maps, and dashboards. Use for data exploration, reporting, and operational monitoring.
```

**Sections to Include**:
1. When to Use (visualization triggers)
2. Visualization Types
   - Time series (single/multi-parameter)
   - Directional roses (wave, wind, current)
   - Scatter plots (Hs vs Tp, wind vs wave)
   - Geographic maps (station locations)
   - Joint distribution contours
   - Histograms and CDFs
3. External Tool Integration
   - MetOceanViewer patterns (desktop reference)
   - `windrose` package - Rose diagrams
   - `plotly.express` - Quick charts
   - `plotly.graph_objects` - Custom layouts
4. Python API Examples (Plotly-based)
5. Dashboard Templates
6. HTML Report Generation
7. Best Practices (interactive, relative paths)

---

## Files to Create

```
.claude/skills/
├── metocean-data-fetcher/
│   └── SKILL.md          # ~350 lines
├── metocean-statistics/
│   └── SKILL.md          # ~400 lines
└── metocean-visualizer/
    └── SKILL.md          # ~300 lines
```

**Total**: ~1050 lines across 3 skill files

---

## Critical Module References

```
src/worldenergydata/modules/metocean/
├── clients/
│   ├── ndbc_client.py      # NDBCClient, NDBCStation, NDBCObservation
│   ├── coops_client.py     # COOPSClient, COOPSWaterLevel, COOPSCurrent
│   ├── open_meteo_client.py # OpenMeteoClient, OpenMeteoForecast
│   ├── erddap_client.py    # ERDDAPClient
│   └── met_norway_client.py # METNorwayClient
├── processors/
│   ├── data_harmonizer.py  # DataHarmonizer, HarmonizedObservation
│   ├── unit_converter.py   # UnitConverter
│   ├── quality_filter.py   # QualityFilter
│   └── data_fusion.py      # DataFusion, FusedObservation
├── cache/
│   └── cache_manager.py    # CacheManager, CacheKey
└── exporters/
    ├── csv_exporter.py     # CSVExporter
    ├── json_exporter.py    # JSONExporter
    └── netcdf_exporter.py  # NetCDFExporter
```

---

## External Dependencies to Document

| Package | Purpose | Install |
|---------|---------|---------|
| `metocean-api` | NORA3/ERA5 extraction | `pip install metocean-api` |
| `metocean-stats` | Statistical analysis | `pip install metocean-stats` |
| `noaa_coops` | CO-OPS wrapper | `pip install noaa_coops` |
| `erddapy` | ERDDAP client | `pip install erddapy` |
| `windrose` | Rose diagrams | `pip install windrose` |
| `scipy` | Distribution fitting | (already installed) |
| `plotly` | Visualization | (already installed) |

---

## Verification

1. **Skill Activation**: Test trigger phrases activate correct skill
2. **Python Examples**: All code examples run without errors
3. **External Tools**: Document installation and basic usage
4. **HTML Output**: Reports follow html-reporting-standards
5. **Cross-References**: Link to related skills (energy-data-visualizer, marine-safety-incidents)

---

# Previous: Module Implementation (Complete)

The metocean module implementation is complete with 31 Python files. See below for reference.

## Data Sources (Priority Order)

### Tier 1 - Open Access (No Authentication)
| Source | Data Types | API Type | Rate Limit |
|--------|-----------|----------|------------|
| **NOAA NDBC** | Waves, wind, SST, currents | HTTP/Text files | None |
| **NOAA CO-OPS** | Tides, currents, water levels | REST API (JSON) | None |
| **Open-Meteo Marine** | Waves, wind, SST (forecast) | REST API (JSON) | None |
| **IOOS ERDDAP** | Buoy data, gliders, HF radar | ERDDAP protocol | None |

### Tier 2 - Registration Required
| Source | Data Types | API Type | Notes |
|--------|-----------|----------|-------|
| **Copernicus Marine (CMEMS)** | Global ocean (SST, currents, waves) | OPeNDAP/ERDDAP | Free registration |
| **MET Norway** | Ocean forecasts, NORA hindcasts | REST API (JSON) | No auth needed |
| **ECMWF Open Data** | Wave forecasts | Python package | Free registration |

### Tier 3 - Regional (Implement in Phase 4)
| Source | Data Types | API Type | Notes |
|--------|-----------|----------|-------|
| **HYCOM** | Ocean model (currents, SST, salinity) | OPeNDAP/THREDDS | 1992-present |
| **UK Met Office** | Marine forecasts | DataPoint API | Registration required |
| **Australian BOM** | Southern Hemisphere data | FTP/REST | Prototype API |

## Module Structure

```
src/worldenergydata/modules/metocean/
├── __init__.py
├── cli.py                      # Typer CLI commands
├── config.py                   # Pydantic-settings configuration
├── constants.py                # Enums: DataSource, DataType, StationType
├── exceptions.py               # MetoceanError, HTTPError, RateLimitError
├── database/
│   ├── models.py               # Station, Observation, Forecast, FetchLog
│   ├── db_manager.py           # Session management
│   └── init_db.py              # Schema initialization
├── clients/
│   ├── base_client.py          # Abstract base with rate limiting, retries
│   ├── ndbc_client.py          # NOAA NDBC buoy data
│   ├── coops_client.py         # NOAA CO-OPS tides/currents
│   ├── open_meteo_client.py    # Open-Meteo Marine API
│   ├── erddap_client.py        # IOOS ERDDAP federated access
│   └── cmems_client.py         # Copernicus Marine (Phase 4)
├── processors/
│   ├── data_harmonizer.py      # Multi-source standardization
│   ├── unit_converter.py       # knots→m/s, feet→m, °F→°C
│   └── quality_filter.py       # Data quality checks
├── cache/
│   ├── cache_manager.py        # TTL-based caching
│   └── offline_store.py        # Offline data storage
├── exporters/
│   ├── csv_exporter.py
│   ├── json_exporter.py
│   └── netcdf_exporter.py      # CF-compliant NetCDF
└── utils/
    ├── validators.py
    └── coordinates.py          # Geospatial utilities
```

## Database Models

### Core Tables
1. **Station** - Buoy/station metadata (source_id, lat/lon, water_depth, type)
2. **Observation** - Time-series data (wave_height, wind_speed, sst, currents, etc.)
3. **GridPoint** - Model grid points for CMEMS/HYCOM data
4. **Forecast** - Forecast data with init_time and lead_time
5. **FetchLog** - Data fetch operation logging

### Key Design Decisions
- Single `Observation` table with nullable columns (vs separate tables per parameter)
- Composite indexes on (station_id, observation_time) for efficient time-series queries
- Quality flags standardized across all sources

## CLI Commands

```bash
# Station management
wed metocean stations list --source ndbc --region gom --active
wed metocean stations search --bbox -98,-88,25,31

# Data fetching
wed metocean fetch ndbc 41001 --params wave,wind
wed metocean fetch open-meteo 28.5,-88.5 --params wave,sst
wed metocean fetch coops 8761724 --params water_level

# Historical data
wed metocean historical 41001 2024-01-01 2024-12-31 --output data.csv
wed metocean historical 28.5,-88.5 2024-01-01 2024-03-01 --sources ndbc,open-meteo --fuse

# Cache management
wed metocean cache status
wed metocean cache clear --source ndbc

# Export
wed metocean export csv --output waves.csv --station 41001
wed metocean export netcdf --output gom_data.nc --start 2024-01-01
```

## Implementation Phases

### Phase 1: Foundation (Tasks 1-4)
- Module skeleton with config, constants, exceptions
- Database models and schema initialization
- Base API client with rate limiting and retries
- NDBC client implementation (first Tier 1 source)

### Phase 2: Multi-Source (Tasks 5-8)
- NOAA CO-OPS client (tides/currents)
- Open-Meteo Marine client (coordinate queries)
- Data harmonization processor
- Cache manager with TTL and offline support

### Phase 3: CLI & Export (Tasks 9-12)
- Full CLI implementation with Typer
- CSV/JSON/NetCDF exporters
- Statistics and reporting
- Integration with main CLI

### Phase 4: Advanced (Tasks 13-16)
- CMEMS client (registration-based)
- MET Norway client
- Multi-source data fusion
- Documentation and optimization

## Critical Files to Reference

| Pattern | Reference File |
|---------|---------------|
| HTTP client with retries | `modules/marine_safety/scrapers/base_scraper.py` |
| SQLAlchemy 2.0+ models | `modules/marine_safety/database/models.py` |
| Pydantic configuration | `modules/marine_safety/config.py` |
| Cache management | `modules/bsee/data/cache/chunk_manager.py` |
| CLI structure | `modules/marine_safety/cli.py` |

## Configuration

```python
# Environment variables
METOCEAN_DB_HOST=localhost
METOCEAN_DB_PORT=5432
METOCEAN_DB_DATABASE=worldenergydata
METOCEAN_API_REQUEST_TIMEOUT=30
METOCEAN_API_RATE_LIMIT_DELAY=1.0
METOCEAN_API_CMEMS_USERNAME=  # Optional for Tier 2
METOCEAN_API_CMEMS_PASSWORD=  # Optional for Tier 2
METOCEAN_CACHE_TTL_HOURS=24
METOCEAN_CACHE_MAX_SIZE_MB=500
```

## Data Parameters Supported

| Parameter | Unit | Sources |
|-----------|------|---------|
| wave_height_m | meters | NDBC, Open-Meteo, CMEMS |
| wave_period_s | seconds | NDBC, Open-Meteo, CMEMS |
| wave_direction_deg | degrees | NDBC, Open-Meteo, CMEMS |
| wind_speed_ms | m/s | NDBC, Open-Meteo, CO-OPS |
| wind_direction_deg | degrees | NDBC, Open-Meteo |
| current_speed_ms | m/s | CO-OPS, CMEMS |
| current_direction_deg | degrees | CO-OPS, CMEMS |
| sea_surface_temp_c | Celsius | NDBC, Open-Meteo, CMEMS |
| water_level_m | meters | CO-OPS |
| pressure_hpa | hPa | NDBC |

## Verification Plan

### Unit Tests
- Test each API client with mocked responses
- Test data harmonization with sample data
- Test cache manager TTL and invalidation

### Integration Tests
- Fetch real data from NDBC station 41001 (Gulf of Mexico - primary test station)
- Test CO-OPS station 8761724 (Grand Isle, LA) for tides
- Verify data parsing and database storage
- Test CLI commands end-to-end
- Cross-validate NDBC and Open-Meteo data for same coordinates

### Manual Verification
```bash
# 1. Verify module imports
python -c "from worldenergydata.metocean import MetoceanConfig"

# 2. Initialize database
wed metocean db init

# 3. List available stations
wed metocean stations list --source ndbc --region gom

# 4. Fetch real-time data
wed metocean fetch ndbc 41001 --params wave,wind

# 5. Fetch historical data
wed metocean historical 41001 2024-01-01 2024-01-31 --output test.csv

# 6. Verify export
wed metocean export json --output test.json --station 41001
```

## Dependencies

```toml
# Already in project
httpx = ">=0.24"
sqlalchemy = ">=2.0"
pydantic-settings = ">=2.0"
typer = ">=0.9"
rich = ">=13.0"

# New dependencies needed
netCDF4 = ">=1.6"        # NetCDF export
erddapy = ">=2.0"        # ERDDAP client
copernicusmarine = "*"   # CMEMS Python toolbox (Phase 4)
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API rate limits | Built-in rate limiting, configurable delays |
| API downtime | Multiple sources, graceful fallback |
| Large data volumes | Chunked downloads, streaming, cache |
| Data format changes | Abstract parser layer, version checks |
| Network issues | Retry with exponential backoff, offline mode |

## Success Criteria

1. Successfully fetch real-time data from all Tier 1 sources
2. Historical data queries with date ranges work correctly
3. Data harmonization produces consistent units across sources
4. CLI commands are intuitive and well-documented
5. Cache reduces redundant API calls by >80%
6. NetCDF exports are CF-compliant and interoperable
