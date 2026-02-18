---
title: BSEE Offshore Infrastructure Data Acquisition
description: Add platform structures, pipeline permits, deepwater structures, and pipeline locations to worldenergydata BSEE module with full refresh modes
version: "1.0"
module: worldenergydata/modules/bsee
session:
  id: bsee-infrastructure-2026-01-31
  agent: claude-opus-4.5
review:
  status: implemented
  iterations: 1
  completed: 2026-01-31
  commit: 81a4c970
---

# BSEE Offshore Infrastructure Data Acquisition

## Objective

Extend the existing BSEE module in worldenergydata to download, process, and serve 4 new infrastructure datasets from data.bsee.gov. All acquisition follows existing refresh mode patterns (legacy + enhanced). Then produce a reference catalog documenting what BSEE provides vs. gaps needing online research.

## New Data Sources

| Key | ZIP File | URL | Update Freq |
|-----|----------|-----|-------------|
| `platform` | PlatStrucRawData.zip | `data.bsee.gov/Platform/Files/PlatStrucRawData.zip` | daily |
| `pipeline_permit` | PipePermRawData.zip | `data.bsee.gov/Pipeline/Files/PipePermRawData.zip` | daily |
| `deepwater_structure` | PermStrucRawData.zip | `data.bsee.gov/Platform/Files/PermStrucRawData.zip` | daily |
| `pipeline_location` | PipeLocAllRawData.zip | `data.bsee.gov/Pipeline/Files/PipeLocAllRawData.zip` | daily |

## Phase 1: Schemas + Models (TDD, no network)

### Tests First

| Test File | Tests |
|-----------|-------|
| `tests/modules/bsee/data/schemas/test_platform_schema.py` | Valid record, invalid water depth, date parsing, optional defaults |
| `tests/modules/bsee/data/schemas/test_pipeline_schema.py` | Valid record, MAOP bounds, OD code parsing, status codes |
| `tests/modules/bsee/data/models/test_platform_model.py` | `is_active`, `structure_key`, type classification |
| `tests/modules/bsee/data/models/test_pipeline_model.py` | `is_active`, `is_deepwater`, segment key |

### Then Implementation

**New files:**
- `src/worldenergydata/modules/bsee/data/schemas/__init__.py`
- `src/worldenergydata/modules/bsee/data/schemas/platform.py` - PlatformStructureSchema (Pydantic)
- `src/worldenergydata/modules/bsee/data/schemas/pipeline.py` - PipelinePermitSchema, PipelineLocationSchema
- `src/worldenergydata/modules/bsee/data/schemas/deepwater_structure.py` - DeepwaterStructureSchema
- `src/worldenergydata/modules/bsee/data/models/__init__.py`
- `src/worldenergydata/modules/bsee/data/models/platform.py` - PlatformStructure dataclass
- `src/worldenergydata/modules/bsee/data/models/pipeline.py` - PipelinePermit, PipelineLocation dataclasses
- `src/worldenergydata/modules/bsee/data/models/deepwater_structure.py` - DeepwaterStructure dataclass

### Key Platform Fields
AREA_CODE, BLOCK_NUMBER, COMPLEX_ID_NUM, STRUCTURE_NUMBER, STRUCTURE_NAME, STRUC_TYPE_CODE, MAJ_STRUC_FLAG, FIELD_NAME_CODE, WATER_DEPTH, INSTALL_DATE, REMOVAL_DATE, DECK_COUNT, SLOT_COUNT, SLANT_SLOT_COUNT, SLOT_DRILL_COUNT, SATELLITE_COMPLETION_COUNT, UNDERWATER_COMPLETION_COUNT, HELIPORT_FLAG, ATTENDED_8_HR_FL, MANNED_24_HR_FL, LATITUDE, LONGITUDE, LEASE_NUMBER, DISTRICT_CODE, AUTHORITY_TYPE, AUTHORITY_NUMBER, AUTHORITY_STATUS, STE_CLRNCE_DATE, INCS

### Key Pipeline Fields
SEGMENT_NUM, PPL_SIZE_CODE (OD), MAOP_PRSS, RECV_MAOP_PRSS, SEG_LENGTH, MAX_WTR_DPTH, MIN_WTR_DPTH, PROD_CODE, CATHODIC_CODE, CAT_LIFE_TM, BUR_DSGN_FL, LK_DETEC_FL, BD_PPL_SDV_FL, BD_PPL_FSV_FL, BIDIR_FLAG, DEP_FLAG, STATUS_CODE, PPL_CONST_DATE, INIT_HS_DT, APPROVED_DATE, ABAN_DATE, ABAN_APRV_DT, ABAN_TYPE

## Phase 2: Web Scraper + Config

### Tests First

| Test File | Tests |
|-----------|-------|
| `tests/modules/bsee/data/scrapers/test_bsee_web_infrastructure.py` | URL keys exist, URL patterns correct, timeout values set |
| `tests/modules/bsee/data/config/test_config_router_infrastructure.py` | New data flags in default config, validation accepts new types |

### Modify Existing Files

**`src/worldenergydata/modules/bsee/data/scrapers/bsee_web.py`**
- Add 4 URLs to `URLS` dict
- Add 4 timeout entries to `TIMEOUTS` dict
- Add 4 download convenience methods (following `download_well_data()` pattern)

**`src/worldenergydata/modules/bsee/data/config/config_router.py`**
- Add data flags: `platform`, `pipeline_permit`, `deepwater_structure`, `pipeline_location`
- Add source entries with URLs and update frequencies
- Extend `validate_config()` data_flags list
- Update `get_system_info()` feature/source entries

## Phase 3: Processing Pipeline (Enhanced Mode + Refresh)

### Tests First

| Test File | Tests |
|-----------|-------|
| `tests/modules/bsee/data/processors/test_in_memory_infrastructure.py` | Column parsing, date coercion, type casting for each data type |
| `tests/modules/bsee/data/refresh/test_infrastructure_refresh.py` | Flag routing, binary save, refresh lifecycle |

### Modify Existing Files

**`src/worldenergydata/modules/bsee/data/processors/in_memory.py`**
- Add `process_platform_data(zip_data, cfg)`
- Add `process_pipeline_permit_data(zip_data, cfg)`
- Add `process_deepwater_structure_data(zip_data, cfg)`
- Add `process_pipeline_location_data(zip_data, cfg)`
- Each: extract CSV from ZIP -> define columns -> parse dates/numerics -> return DataFrame

**`src/worldenergydata/modules/bsee/data/refresh/data_refresh_enhanced.py`**
- Add flag checks in `router()` for 4 new types
- Add `refresh_platform_data_enhanced(cfg)` (follows `refresh_well_data_enhanced()` pattern)
- Add `refresh_pipeline_permit_data_enhanced(cfg)`
- Add `refresh_deepwater_structure_data_enhanced(cfg)`
- Add `refresh_pipeline_location_data_enhanced(cfg)`
- Add `_save_*_data_binary()` methods for each

## Phase 4: ZIP Sources + Loaders (Legacy Mode)

### New Files

**ZIP source processors (follow `well_data.py` pattern):**
- `src/worldenergydata/modules/bsee/data/sources/zip/platform_data.py` - PlatformDataFromZip
- `src/worldenergydata/modules/bsee/data/sources/zip/pipeline_data.py` - PipelinePermitDataFromZip
- `src/worldenergydata/modules/bsee/data/sources/zip/deepwater_structure_data.py` - DeepwaterStructureDataFromZip
- `src/worldenergydata/modules/bsee/data/sources/zip/pipeline_location_data.py` - PipelineLocationDataFromZip

**Query-time loaders (follow `block/local_files.py` pattern):**
- `src/worldenergydata/modules/bsee/data/loaders/infrastructure/__init__.py`
- `src/worldenergydata/modules/bsee/data/loaders/infrastructure/platform_loader.py`
- `src/worldenergydata/modules/bsee/data/loaders/infrastructure/pipeline_loader.py`
- `src/worldenergydata/modules/bsee/data/loaders/infrastructure/router.py`

**Loader query methods:**
- `get_platforms_by_area_block(area_code, block_number)`
- `get_platforms_by_complex(complex_id)`
- `get_pipelines_by_status(status_code)`
- `get_infrastructure_by_lease(lease_number)`

### Modify Existing Files

- `src/worldenergydata/modules/bsee/data/sources/zip/__init__.py` - register new classes
- `src/worldenergydata/modules/bsee/data/__init__.py` - register new exports
- `src/worldenergydata/modules/bsee/__init__.py` - add lazy imports

## Phase 5: CLI + Integration

### Modify Existing File

**`src/worldenergydata/cli/commands/bsee.py`**
- Extend `DataType` enum: add `platform`, `pipeline_permit`, `deepwater_structure`, `pipeline_location`, `infrastructure` (all 4 combined)
- Update `refresh` command config builder to route new types
- `infrastructure` type triggers all 4 new datasets

### Test

| Test File | Tests |
|-----------|-------|
| `tests/cli/test_bsee_cli_infrastructure.py` | DataType enum values, refresh config building, infrastructure combo type |

### CLI Usage After Implementation
```bash
# Refresh individual types
worldenergydata bsee refresh --type platform
worldenergydata bsee refresh --type pipeline_permit

# Refresh all infrastructure
worldenergydata bsee refresh --type infrastructure

# Refresh everything (existing + new)
worldenergydata bsee refresh --type all
```

## Phase 6: Data Catalog + Gap Analysis

**New file:** `worldenergydata/docs/bsee/infrastructure_data_catalog.md`

Contents:
1. All 4 datasets with complete field definitions
2. Data relationships (platform -> complex, pipeline -> segment -> location)
3. Available engineering data vs. gaps table
4. Structure type code reference (FP, CT, TLP, SPAR, FPS, FPSO, SS)
5. Pipeline product code reference (43+ codes)
6. Pipeline OD standard sizes (0.5" to 54")
7. Suggested supplementary sources for missing data

### Known Gaps (for later online research)

| Missing Data | Potential Source |
|-------------|----------------|
| Wall thickness | BSEE scanned pipeline maps, FOIA requests |
| Inside Diameter (ID) | Calculate from OD + wall thickness |
| Material grade (X52, X65) | DNV reports, operator filings |
| Riser specifications | Not in BSEE public data; operator docs |
| Jumper details (rigid/flexible) | Not tracked; subsea vendor data |
| Material strength (SMYS) | Derive from material grade |
| Coating/insulation | Not in BSEE; operator engineering docs |
| Platform structural dimensions | Not public; structural design reports |
| Subsea equipment (manifolds, trees) | BSEE eWell/permit data, operator filings |

## Verification

1. Run `pytest tests/modules/bsee/data/schemas/` - all schema tests pass
2. Run `pytest tests/modules/bsee/data/models/` - all model tests pass
3. Run `pytest tests/modules/bsee/data/scrapers/test_bsee_web_infrastructure.py` - URL tests pass
4. Run `worldenergydata bsee refresh --type platform --force` - downloads and processes platform data
5. Run `worldenergydata bsee refresh --type infrastructure` - all 4 datasets refresh
6. Verify `.bin` files created in `data/modules/bsee/bin/`
7. Run `worldenergydata bsee refresh --type infrastructure` again (no --force) - chunk manager detects no changes, skips download

## Critical Files Reference

| File | Purpose |
|------|---------|
| `src/.../bsee/data/scrapers/bsee_web.py` | URL registry + download methods |
| `src/.../bsee/data/refresh/data_refresh_enhanced.py` | Refresh orchestration |
| `src/.../bsee/data/processors/in_memory.py` | ZIP -> DataFrame processing |
| `src/.../bsee/data/config/config_router.py` | Config flags + routing |
| `src/.../cli/commands/bsee.py` | CLI DataType enum + commands |
| `src/.../bsee/data/sources/zip/well_data.py` | Pattern template for ZIP sources |
| `src/.../bsee/data/loaders/block/local_files.py` | Pattern template for loaders |
