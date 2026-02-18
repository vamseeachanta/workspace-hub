# Offshore Rig Fleet Inventory + Data Indexing Plan

## Context

The worldenergydata repository has **rig names in BSEE WAR data** (well activity records) but no structured rig fleet inventory — no type classification, specs, contractor info, or status tracking. The `digitalmodel` submodule has **template rig specs** (drillship.csv, vessel_database.json) and a **drilling rig scraper framework** (DrillingRigScraper + VesselScraper base) with standard vessel fields, but no populated fleet database.

The user wants to:
1. **Add a rig fleet inventory** — a structured database of offshore drilling rigs with type, specs, contractor, and status
2. **Create a data indexing system** — a machine-readable catalog for efficient data discovery across the entire repo

---

## Phase 1: Data Catalog (build first — foundational)

Creates a machine-readable inventory of all datasets across the repository for efficient discovery.

### 1.1 Catalog data models

**New file:** `src/worldenergydata/common/catalog.py`

```python
@dataclass DatasetEntry:     name, path, format, domain, size_bytes, row_count?, columns?, update_frequency?, source_url?, last_modified?, description?
@dataclass ModuleCatalogEntry: name, description, path, domains, datasets, documentation
@dataclass DataCatalog:        version, generated_at, total_modules, total_datasets, total_size_bytes, modules
```

### 1.2 Catalog generation script

**New file:** `scripts/generate_data_catalog.py`

- `DataCatalogGenerator` class scans `data/modules/` directories
- For CSV: reads header row (nrows=0) for columns, line count for rows, file size
- For .bin/.parquet: file size + inferred domain from parent directory name
- Outputs to `data/catalog/data-catalog.yml` (YAML format, matching existing config/*.yml pattern)
- CLI: `uv run python scripts/generate_data_catalog.py [--module bsee] [--format json]`

### 1.3 Output + cross-reference

- **Generated:** `data/catalog/data-catalog.yml`
- **Modified:** `docs/data/DATA_MAP.md` — add reference to machine-readable catalog

### 1.4 Tests

- `tests/unit/test_catalog_models.py` — DatasetEntry, ModuleCatalogEntry serialization
- `tests/unit/test_data_catalog.py` — scan_csv_file, infer_domain, scan_module against fixture dirs

---

## Phase 2: Rig Fleet — Constants, Schema, Model (pure data layer)

### 2.1 Rig type enum + classifier

**New file:** `src/worldenergydata/modules/bsee/data/loaders/rig_fleet/constants.py`

```python
class RigType(str, Enum):
    DRILLSHIP, SEMI_SUBMERSIBLE, JACK_UP, PLATFORM_RIG,
    TENDER_ASSISTED, INLAND_BARGE, SUBMERSIBLE, UNKNOWN

class RigStatus(str, Enum):
    ACTIVE, STACKED_COLD, STACKED_WARM, UNDER_CONTRACT,
    AVAILABLE, IN_TRANSIT, IN_SHIPYARD, SCRAPPED, UNKNOWN

def classify_rig_type(rig_name: str) -> RigType:
    # Heuristic classification from known rig name patterns
    # Overrides loaded from rig_type_overrides.csv
```

### 2.2 Pydantic validation schema

**New file:** `src/worldenergydata/modules/bsee/data/schemas/rig_fleet.py`

Follows `platform.py` pattern exactly. Fields combine BSEE WAR linkage with digitalmodel's VesselScraper standard fields:

| Field | Type | Source |
|-------|------|--------|
| RIG_NAME | str (required) | BSEE WAR data |
| RIG_TYPE | Optional[str] | Classified from name / manual override |
| RIG_STATUS | Optional[str] | Manual / scraper |
| OWNER | Optional[str] | Scraper / manual |
| OPERATOR | Optional[str] | Drilling contractor |
| WATER_DEPTH_RATING_FT | Optional[float] | Spec sheet |
| DRILLING_DEPTH_RATING_FT | Optional[float] | Spec sheet |
| LOA_M | Optional[float] | digitalmodel template field |
| BEAM_M | Optional[float] | digitalmodel template field |
| DISPLACEMENT_TONNES | Optional[float] | digitalmodel template field |
| DP_CLASS | Optional[int] | digitalmodel template field |
| YEAR_BUILT | Optional[int] | Scraper |
| IMO_NUMBER | Optional[str] | Scraper |
| FLAG_STATE | Optional[str] | Scraper |
| WELLS_DRILLED_COUNT | Optional[int] | Computed from WAR |
| LAST_WAR_DATE | Optional[str] | Computed from WAR |
| LAST_AREA_CODE | Optional[str] | Computed from WAR |

Validators: strip whitespace, empty-to-None, coerce numeric strings, validate ranges (depth >= 0, year 1900-2030).

### 2.3 Domain model

**New file:** `src/worldenergydata/modules/bsee/data/models/rig_fleet.py`

Follows `platform.py` dataclass pattern. Computed properties:
- `is_active` — not stacked/scrapped
- `is_deepwater_capable` — water depth rating >= 4000 ft
- `rig_key` — normalized name for deduplication
- `rig_type_display` — human-readable type string

### 2.4 Tests

- `tests/modules/bsee/data/loaders/rig_fleet/test_constants.py` — enum values, classify_rig_type heuristics
- `tests/modules/bsee/data/loaders/rig_fleet/test_rig_fleet_schema.py` — validation, coercion, rejection
- `tests/modules/bsee/data/loaders/rig_fleet/test_rig_fleet_model.py` — computed properties

---

## Phase 3: Rig Fleet — Loader + Router (I/O layer)

### 3.1 Fleet loader

**New file:** `src/worldenergydata/modules/bsee/data/loaders/rig_fleet/rig_fleet_loader.py`

Follows `infrastructure/platform_loader.py` pattern:

- `build_fleet_from_war(cfg)` — extract unique RIG_NAME from `mv_war_main.bin`, aggregate wells_drilled_count / last_war_date / last_area_code per rig, classify types
- `enrich_from_digitalmodel()` — merge LOA, beam, displacement, DP class from `digitalmodel/docs/modules/orcaflex/templates/components/vessels/drillship.csv` and `vessel_database.json` for matching rig types
- `load_overrides(path)` — apply manual rig_type corrections from `rig_type_overrides.csv`
- `get_rigs_by_type(rig_type)`, `get_rig_well_history(rig_name)` — query methods

### 3.2 Router

**New file:** `src/worldenergydata/modules/bsee/data/loaders/rig_fleet/router.py`

Config-driven dispatch, same pattern as `infrastructure/router.py`.

### 3.3 Package init + parent exports

- **New:** `src/worldenergydata/modules/bsee/data/loaders/rig_fleet/__init__.py`
- **Modified:** `src/worldenergydata/modules/bsee/data/schemas/__init__.py` — add RigFleetSchema
- **Modified:** `src/worldenergydata/modules/bsee/data/models/__init__.py` — add RigFleetEntry

### 3.4 Tests

- `tests/modules/bsee/data/loaders/rig_fleet/test_rig_fleet_loader.py` — build_fleet_from_war with fixture WAR data, enrich_from_digitalmodel, override loading

---

## Phase 4: Integration + Initial Data Population

1. Run `build_fleet_from_war()` against actual WAR binary data
2. Review classified rig types, create `data/modules/bsee/bin/rig_fleet/rig_type_overrides.csv` for corrections
3. Run enrichment from digitalmodel template specs
4. Regenerate data catalog to include rig fleet datasets

---

## Key Existing Files to Reuse

| File | Reuse |
|------|-------|
| `src/.../bsee/data/schemas/platform.py` | Schema pattern (Pydantic + validators) |
| `src/.../bsee/data/models/platform.py` | Model pattern (dataclass + properties) |
| `src/.../bsee/data/loaders/infrastructure/platform_loader.py` | Loader pattern (bin loading, cfg-driven) |
| `src/.../bsee/analysis/well_rig_days.py` | WAR RIG_NAME extraction logic |
| `digitalmodel/.../vessels/drillship.csv` | Template rig specs (4 drillship configs) |
| `digitalmodel/.../vessel_database.json` | Template specs (drillship, semi-sub, jack-up) |
| `digitalmodel/.../vessel_scraper.py` | Standard vessel fields list + column mapping |
| `digitalmodel/.../drilling_rig_scraper.py` | Future scraper for external fleet data |

---

## New Files Summary

| # | File | Purpose |
|---|------|---------|
| 1 | `src/worldenergydata/common/catalog.py` | Catalog dataclasses |
| 2 | `scripts/generate_data_catalog.py` | Catalog generation script |
| 3 | `data/catalog/data-catalog.yml` | Generated catalog output |
| 4 | `src/.../bsee/data/loaders/rig_fleet/__init__.py` | Package init |
| 5 | `src/.../bsee/data/loaders/rig_fleet/constants.py` | RigType, RigStatus enums |
| 6 | `src/.../bsee/data/schemas/rig_fleet.py` | RigFleetSchema |
| 7 | `src/.../bsee/data/models/rig_fleet.py` | RigFleetEntry dataclass |
| 8 | `src/.../bsee/data/loaders/rig_fleet/rig_fleet_loader.py` | Fleet loader |
| 9 | `src/.../bsee/data/loaders/rig_fleet/router.py` | Fleet router |
| 10 | `data/modules/bsee/bin/rig_fleet/rig_type_overrides.csv` | Manual type corrections |
| 11-16 | `tests/...` (6 test files) | TDD tests for all above |

## Modified Files

| File | Change |
|------|--------|
| `src/.../bsee/data/schemas/__init__.py` | Export RigFleetSchema |
| `src/.../bsee/data/models/__init__.py` | Export RigFleetEntry |
| `docs/data/DATA_MAP.md` | Reference to data catalog |

---

## Verification

1. **Tests:** `uv run pytest tests/modules/bsee/data/loaders/rig_fleet/ tests/unit/test_catalog_models.py tests/unit/test_data_catalog.py -v`
2. **Catalog generation:** `uv run python scripts/generate_data_catalog.py` — verify YAML output has all modules
3. **Fleet build:** Load WAR data, verify unique rigs extracted with correct counts
4. **Schema validation:** Create RigFleetSchema instances, verify validators catch bad data
5. **Type classification:** Verify known rigs (e.g., "T.O. DEEPWATER TITAN" → DRILLSHIP) classify correctly
