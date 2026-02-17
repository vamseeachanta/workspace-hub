# WRK-038: Global LNG Terminal Dataset with Engineering Design Data

## Overview

Build a new `lng_terminals` module to compile a global dataset of LNG terminal projects with comprehensive engineering design parameters. The dataset covers all facility types (onshore import/export, FSRU, FLNG) with equal depth of detail including full pipeline inventories, process equipment specs, hull/floater design, storage, and marine infrastructure.

**Route**: C (Complex) | **Target repo**: worldenergydata

---

## Module Structure

```
src/worldenergydata/modules/lng_terminals/
    __init__.py
    constants.py              # Enums (TerminalType, Status, PipelineType, etc.)
    config.py                 # Pydantic-settings config
    exceptions.py             # LNGTerminalError extending ModuleError
    models/
        __init__.py
        terminal.py           # Core LNGTerminal model
        design.py             # Engineering sub-models (hull, pipeline, process, storage)
        data_quality.py       # SourceCitation, QualityScore
    collectors/
        __init__.py
        base_collector.py     # ABC: fetch_data() -> parse_records() -> validate()
        seed_collector.py     # Parse curated data from docs/modules/lng/
        ferc_collector.py     # US regulatory data (CSV)
        gie_collector.py      # European terminal inventory (JSON/CSV)
        giignl_collector.py   # Global annual report (PDF via pdfplumber)
        web_collector.py      # Trade publications, Marine Insight
    processors/
        __init__.py
        normalizer.py         # Country codes, units, status standardization
        deduplicator.py       # Cross-source matching by name+country+coords
        enricher.py           # Merge multi-source records, source priority
        quality_scorer.py     # Per-field and per-record completeness scores
    exporters/
        __init__.py
        csv_exporter.py
        parquet_exporter.py
    analysis/
        __init__.py
        capacity_analysis.py  # Regional/global capacity summaries
        timeline_analysis.py  # Construction pipeline, FID timelines
    reports/
        __init__.py
        terminal_map.py       # Plotly interactive global map
        quality_dashboard.py  # Data completeness report
    cli.py                    # Typer CLI entry point

config/lng_terminals.yml      # Data source URLs, rate limits, processing params
data/modules/lng_terminals/   # raw/, processed/, reports/
tests/modules/lng_terminals/  # test files + fixtures/
```

---

## Data Schema

### Core Model: `LNGTerminal`

| Field | Type | Description |
|-------|------|-------------|
| terminal_id | str | Generated slug (name + country) |
| terminal_name | str | Official name |
| aliases | list[str] | Alternative names |
| country | str | ISO 3166 alpha-3 |
| region | str | Geographic region enum |
| latitude / longitude | float? | WGS84 coordinates |
| terminal_type | TerminalType | ONSHORE_IMPORT, ONSHORE_EXPORT, FSRU, FLNG, ONSHORE_LIQUEFACTION |
| function | TerminalFunction | IMPORT, EXPORT, BIDIRECTIONAL |
| status | TerminalStatus | OPERATIONAL, UNDER_CONSTRUCTION, PLANNED, PROPOSED, DECOMMISSIONED, MOTHBALLED |
| capacity_mtpa | float? | Nameplate capacity |
| year_commissioned | int? | |
| operator / owner | str? | |
| epc_contractor | str? | |
| capex_usd_million | float? | |
| hull_design | HullDesign? | Floater details (FSRU/FLNG) |
| pipelines | list[PipelineSpec] | Full pipeline inventory |
| process_equipment | ProcessEquipment? | Trains, compressors, heat exchangers |
| storage | StorageSpec? | Tank details |
| marine_infrastructure | MarineInfrastructure? | Jetty, loading arms, mooring |
| metocean_notes | str? | Environmental/metocean context |
| sources | list[SourceCitation] | Provenance tracking |
| data_quality_score | float? | 0-100 computed score |
| last_updated | datetime | |

### Sub-model: `HullDesign` (FSRU/FLNG/Offshore)

| Field | Type | Description |
|-------|------|-------------|
| hull_type | str | Ship-shaped, barge, semi-submersible, spar |
| loa_m | float? | Length overall (meters) |
| beam_m | float? | Beam width |
| depth_m | float? | Hull depth |
| draft_m | float? | Operating draft |
| displacement_tonnes | float? | |
| mooring_type | str? | Spread, internal turret, external turret, tower, CALM |
| turret_details | str? | Turret type and specs |
| riser_count | int? | Number of risers |
| riser_details | str? | Riser type, size, material |
| conversion_vessel | str? | Original vessel name if converted |
| builder_yard | str? | Shipyard |
| year_built | int? | Hull construction year |

### Sub-model: `PipelineSpec` (one per pipeline)

| Field | Type | Description |
|-------|------|-------------|
| pipeline_type | PipelineType | FEED_GAS, LNG_TRANSFER, LNG_LOADING, BOIL_OFF_GAS, SEND_OUT, PROCESS, CONDENSATE |
| diameter_inches | float? | Nominal pipe size |
| length_km | float? | |
| wall_thickness_mm | float? | |
| material | str? | Carbon steel, stainless, duplex, invar |
| design_pressure_barg | float? | |
| design_temperature_c | float? | Min/max design temp |
| insulation_type | str? | PUF, vacuum, aerogel, none |
| offshore_segment | bool | Whether pipeline has offshore section |
| notes | str? | |

### Sub-model: `ProcessEquipment`

| Field | Type | Description |
|-------|------|-------------|
| liquefaction_process | str? | C3MR, AP-X, AP-C3MR, DMR, cascade, PRICO, MR |
| number_of_trains | int? | |
| capacity_per_train_mtpa | float? | |
| compressor_type | str? | Centrifugal, axial |
| compressor_driver | str? | Gas turbine, electric motor, steam turbine |
| compressor_power_mw | float? | Per train or total |
| main_heat_exchanger_type | str? | SWHE, plate-fin, shell-and-tube |
| mche_vendor | str? | APCI, Linde, etc. |
| regasification_capacity_mmscfd | float? | For import terminals |
| regasification_type | str? | ORV, SCV, IFV, AAV |
| boil_off_rate_percent | float? | Daily BOG rate |
| pre_treatment | str? | Acid gas removal, dehydration, mercury removal |
| notes | str? | |

### Sub-model: `StorageSpec`

| Field | Type | Description |
|-------|------|-------------|
| tank_type | str | Full containment, membrane (GTT Mark III / NO96), self-supporting (SPB, Moss), in-ground |
| number_of_tanks | int? | |
| capacity_per_tank_m3 | float? | |
| total_capacity_m3 | float? | |
| tank_material | str? | 9% nickel steel, stainless, aluminium |
| insulation_type | str? | Perlite, PUF, composite |
| containment_vendor | str? | GTT, IHI-SPB, etc. |

### Sub-model: `MarineInfrastructure`

| Field | Type | Description |
|-------|------|-------------|
| water_depth_m | float? | At berth/mooring location |
| jetty_count | int? | |
| berth_count | int? | |
| max_vessel_size_m3 | float? | Max LNG carrier capacity |
| loading_arms_count | int? | |
| loading_arm_size_inches | float? | |
| loading_rate_m3_per_hr | float? | |
| fender_type | str? | |
| breakwater | bool? | |
| approach_channel_depth_m | float? | |
| tug_requirements | str? | |

### Data Quality: `SourceCitation`

| Field | Type | Description |
|-------|------|-------------|
| source_name | str | e.g., "GIIGNL Annual Report 2024" |
| source_url | str? | |
| access_date | date | |
| fields_sourced | list[str] | Which fields from this source |
| reliability | HIGH / MEDIUM / LOW | |

---

## Data Collection Strategy

### Source Priority (highest first)

1. **FERC** (US) — Structured CSV, capacity, status, operator. Reliability: HIGH
2. **GIE ALSI** (Europe) — JSON/CSV API, terminal inventory. Reliability: HIGH
3. **GIIGNL** (Global) — PDF table extraction via pdfplumber. Reliability: HIGH
4. **Seed data** — Parse existing `docs/modules/lng/lng_market.md` into structured records (~100-150 terminals). Reliability: MEDIUM
5. **Web sources** — Trade pubs, Marine Insight (ref article), Wikipedia. Reliability: LOW-MEDIUM

### Engineering Design Data Sources

Engineering design data is sparser than commercial data. Target sources:
- **Operator project pages** (QatarEnergy, Cheniere, Shell, Woodside)
- **EPC contractor project references** (Bechtel, Technip, COOEC, Samsung)
- **Classification society records** (DNV, Lloyd's, ABS) for FSRU/FLNG hull data
- **FERC environmental impact statements** — contain detailed facility design specs
- **Trade journals** — LNG Industry, Offshore Engineer, Gas Processing News
- **Conference papers** — OTC, Gastech, LNG Process Technology Conference

Design data will be populated incrementally. Initial records will have commercial parameters filled; engineering sub-models will be enriched over successive collection passes.

---

## Processing Pipeline

```
Collectors (per source) --> data/modules/lng_terminals/raw/ (per-source CSVs)
         |
    Normalizer  --> country codes, units (MTPA, inches, meters), status enums
         |
   Deduplicator --> fuzzy name match + country + coord proximity (<50km)
         |
     Enricher   --> merge multi-source by priority, combine citations
         |
  QualityScorer --> per-field completeness, weighted score (0-100)
         |
     Exporter   --> processed/lng_terminals.csv + .parquet + _metadata.json
```

**Deduplication**: Normalize names (strip "LNG", "Terminal", "Liquefaction"), fuzzy match (>0.85 similarity), require country match, coordinate proximity when available. Manual alias overrides in YAML config for known cases.

**Flattening for CSV/Parquet**: Sub-models serialize as prefixed columns (e.g., `hull_loa_m`, `hull_beam_m`, `pipeline_feed_gas_diameter_inches`). For pipelines (1:N), the primary approach is one row per terminal with pipeline data in repeated column groups (`pipeline_1_type`, `pipeline_1_diameter_inches`, ...) up to a reasonable max (e.g., 8 pipelines). A separate `lng_terminals_pipelines.csv` provides the fully normalized relational view.

---

## Implementation Phases

### Phase 1: Foundation
- `constants.py` — all enums
- `models/terminal.py` — LNGTerminal with all sub-models
- `models/design.py` — HullDesign, PipelineSpec, ProcessEquipment, StorageSpec, MarineInfrastructure
- `models/data_quality.py` — SourceCitation, DataQualityNote
- `exceptions.py` — LNGTerminalError hierarchy
- `config.py` + `config/lng_terminals.yml`
- Tests: `test_models.py` (schema validation, edge cases, enum coverage)

### Phase 2: Seed Dataset + Normalizer + Export
- `collectors/base_collector.py` — ABC
- `collectors/seed_collector.py` — parse existing LNG market research
- `processors/normalizer.py` — unit conversion, country codes, status mapping
- `exporters/csv_exporter.py` + `parquet_exporter.py`
- Tests: `test_normalizer.py`, `test_seed_collector.py`, `test_csv_exporter.py`
- **Deliverable**: Initial dataset of ~100-150 terminals in CSV/parquet

### Phase 3: FERC + Dedup + Enrichment
- `collectors/ferc_collector.py` — US regulatory data
- `processors/deduplicator.py` — cross-source matching
- `processors/enricher.py` — merge with source priority
- Tests: `test_ferc_collector.py`, `test_deduplicator.py`, `test_enricher.py`

### Phase 4: GIE + GIIGNL + Quality Scoring
- `collectors/gie_collector.py` — European terminal data
- `collectors/giignl_collector.py` — PDF extraction
- `processors/quality_scorer.py` — field completeness scoring
- Tests: `test_quality_scorer.py`

### Phase 5: Web Enrichment + Engineering Data
- `collectors/web_collector.py` — trade pubs, operator pages
- Focus on filling engineering sub-models (hull, pipeline, process, storage)
- Marine Insight reference article processing
- Tests: `test_web_collector.py`

### Phase 6: Analysis + Reports + CLI
- `analysis/capacity_analysis.py` — regional summaries
- `analysis/timeline_analysis.py` — FID/construction timelines
- `reports/terminal_map.py` — Plotly interactive map
- `reports/quality_dashboard.py` — completeness report
- `cli.py` — Typer CLI (collect, process, export, report subcommands)
- Tests: `test_cli.py`

---

## Key Files to Modify/Reference

| File | Purpose |
|------|---------|
| `src/worldenergydata/modules/marine_safety/scrapers/base_scraper.py` | HTTP pattern to follow |
| `src/worldenergydata/common/exceptions.py` | Exception hierarchy to extend |
| `src/worldenergydata/common/validation/schemas.py` | Pydantic model patterns |
| `src/worldenergydata/engine.py` | Register module (Phase 6) |
| `docs/modules/lng/lng_market.md` | Seed data source |
| `config/canada.yml` | YAML config pattern |

---

## Verification

1. **Unit tests**: `uv run pytest tests/modules/lng_terminals/ -v`
2. **Schema validation**: Load processed CSV back through LNGTerminal model, assert 100% parse success
3. **Coverage**: `uv run pytest tests/modules/lng_terminals/ --cov=src/worldenergydata/modules/lng_terminals --cov-report=term` — target 80%+
4. **Data quality**: Run quality scorer on final dataset, assert average score >40 (many fields sparse initially) with required fields (name, country, type, status) at 100%
5. **Round-trip**: Export to CSV and parquet, re-import, assert equality
6. **Map report**: Generate `terminal_map.html`, open in browser, verify terminal markers render with correct coordinates
