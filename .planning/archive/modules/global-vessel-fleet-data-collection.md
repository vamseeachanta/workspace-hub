# Global Vessel Fleet Data Collection & Enrichment Plan

**Version**: 1.0
**Module**: worldenergydata
**Session ID**: logical-kindling-quail
**Session Agent**: claude-opus-4.6
**Related WRKs**: WRK-104 (rig fleet expansion), WRK-103 (heavy construction vessels), WRK-102 (hull definitions)

---

## Context

The rig fleet currently has 16 rigs from BSEE WAR data in a 2KB pickle file. We assessed 163 floaters from XLS files (GREEN portability). The goal is to build a comprehensive global vessel fleet covering **drilling rigs** (floaters, jackups, onshore), **heavy construction vessels** (crane vessels, pipelay, heavy-lift), and **service vessels** — all collected from publicly available online sources.

The same collection infrastructure (web scraping, PDF parsing, maritime registry lookup) serves all vessel categories. Building them in parallel maximizes reuse and avoids duplicate infrastructure.

---

## Two Parallel Workstreams

```
Workstream A: Drilling Rig Fleet (WRK-104)          Workstream B: Construction & Service Vessels (WRK-103)
─────────────────────────────────────────            ──────────────────────────────────────────────────────
Phase 1: Shared infrastructure (collectors, parsers, storage)
         ↓                                                    ↓
Phase 2A: XLS ingest (163 floaters)              Phase 2B: Contractor vessel pages
Phase 3A: Drilling contractor fleet pages        Phase 3B: Marine contractor vessel pages
Phase 4: Shared maritime registry enrichment (Equasis, ABS, DNV)
Phase 5: Shared government data (BOEM, Baker Hughes)
Phase 6: Per-workstream fusion, dedup, quality
```

---

## Phase 1: Shared Collection Infrastructure

**Goal**: Build reusable collectors, parsers, and storage that serve both workstreams.

### New module: `src/worldenergydata/vessel_fleet/`

This is a NEW top-level module (not under `bsee/`) because it covers global fleet data from many sources. The existing `bsee/data/loaders/rig_fleet/` stays as-is and feeds into this as one data source.

```
src/worldenergydata/vessel_fleet/
├── __init__.py
├── constants.py                    # VesselCategory, RigType, VesselType, Status, DataSource enums
├── schemas/
│   ├── __init__.py
│   ├── base.py                     # BaseVesselSchema (shared fields: name, type, owner, IMO, etc.)
│   ├── drilling_rig.py             # DrillingRigSchema extends base (water depth, BOP, derrick, etc.)
│   └── construction_vessel.py      # ConstructionVesselSchema extends base (crane, pipelay, deck area)
├── models/
│   ├── __init__.py
│   ├── base.py                     # BaseVesselEntry dataclass
│   ├── drilling_rig.py             # DrillingRigEntry with rig-specific computed properties
│   └── construction_vessel.py      # ConstructionVesselEntry with vessel-specific properties
├── collectors/                     # REUSABLE across both workstreams
│   ├── __init__.py
│   ├── base.py                     # BaseCollector ABC (rate limit, retry, cache, User-Agent)
│   ├── fleet_page_collector.py     # HTML fleet page scraper (configurable per contractor)
│   ├── spec_pdf_collector.py       # PDF spec sheet downloader + parser
│   ├── equasis_collector.py        # Equasis vessel lookup (IMO, flag, class)
│   ├── classification_collector.py # ABS/DNV/LR register lookups
│   ├── boem_collector.py           # BOEM platform structures CSV
│   └── baker_hughes_collector.py   # Baker Hughes rig count Excel
├── configs/                        # Per-company collection configs
│   ├── __init__.py
│   ├── drilling/                   # Drilling contractor configs
│   │   ├── transocean.py           # 27 rigs, spec PDFs at deepwater.com
│   │   ├── valaris.py              # 52 rigs (jackups + drillships + semisubs)
│   │   ├── noble.py                # 32 rigs (floaters + jackups)
│   │   ├── seadrill.py             # Drillships + semisubs
│   │   ├── borr.py                 # 29 modern jackups
│   │   ├── cosl.py                 # 40+ (32 jackups, 10 semisubs)
│   │   ├── ades.py                 # 83 offshore + 40 onshore
│   │   ├── saipem.py               # 12 drilling rigs
│   │   ├── stena.py                # 6 rigs
│   │   ├── vantage.py              # 4 rigs
│   │   ├── nabors.py               # Onshore + MODS platform rigs
│   │   ├── patterson_uti.py        # 172 super-spec onshore
│   │   └── helmerich_payne.py      # FlexRig fleet onshore
│   └── construction/               # Marine contractor configs
│       ├── heerema.py              # Sleipnir, Thialf, Balder (crane vessels)
│       ├── allseas.py              # Pioneering Spirit, Solitaire (pipelay + heavy-lift)
│       ├── saipem_vessels.py       # Castorone, S7000 (pipelay + crane)
│       ├── subsea7.py              # Seven Borealis, Seven Vega (pipelay + SURF)
│       ├── mcdermott.py            # Amazon, DLV 2000 (derrick lay + pipelay)
│       ├── boskalis.py             # Boka Vanguard, Fjord (heavy transport + crane)
│       ├── deme.py                 # Orion, Apollo (wind installation)
│       ├── van_oord.py             # Aeolus, Boreas (wind installation)
│       ├── eneti.py                # Wind turbine installation vessels
│       └── oht.py                  # Alfa Lift (heavy transport)
├── parsers/                        # REUSABLE across both workstreams
│   ├── __init__.py
│   ├── numeric.py                  # "8,000 ft." → 8000.0, "20 x 40" → (20, 40)
│   ├── xls.py                      # Transposed XLS extraction (DrillRigs.xls)
│   ├── html.py                     # HTML table extraction with CSS selectors
│   └── pdf.py                      # Spec sheet PDF text → structured fields
├── storage/
│   ├── __init__.py
│   ├── parquet.py                  # Parquet read/write with schema enforcement
│   └── csv.py                      # Human-readable CSV export
├── dedup/
│   ├── __init__.py
│   ├── normalizer.py               # Rig/vessel name normalization
│   └── deduplicator.py             # IMO + name composite key dedup
├── quality/
│   ├── __init__.py
│   ├── validator.py                # Cross-field validation rules
│   └── completeness.py             # Per-vessel completeness scoring
└── router.py                       # Query interface (by type, owner, region, status)
```

### Data storage

```
data/modules/vessel_fleet/
├── raw/                            # Raw per-source data (Parquet)
│   ├── xls_historical/
│   ├── drilling_contractors/
│   ├── construction_contractors/
│   ├── equasis/
│   └── boem/
├── curated/                        # Deduplicated, validated fleet
│   ├── drilling_rigs.parquet       # All drilling rigs
│   ├── drilling_rigs.csv
│   ├── construction_vessels.parquet # All construction/service vessels
│   └── construction_vessels.csv
└── provenance/
    └── collection_log.json         # Audit trail
```

### Build/collection scripts (in repo for reuse)

```
worldenergydata/scripts/vessel_fleet/
├── collect_drilling_fleet.py       # Runs all drilling contractor collectors
├── collect_construction_fleet.py   # Runs all construction contractor collectors
├── enrich_from_registries.py       # Runs Equasis + classification society enrichment
├── enrich_from_government.py       # Runs BOEM + Baker Hughes enrichment
├── ingest_xls_historical.py        # Ingests DrillRigs.xls (163 floaters)
├── fuse_and_deduplicate.py         # Merges all sources, deduplicates, validates
├── export_fleet.py                 # Exports curated Parquet + CSV
└── run_full_pipeline.py            # End-to-end orchestrator (all steps in order)
```

### Key files to create (Phase 1)

| File | Purpose |
|------|---------|
| `vessel_fleet/__init__.py` | Package init, version |
| `vessel_fleet/constants.py` | All enums (VesselCategory, RigType, VesselType, DataSource, etc.) |
| `vessel_fleet/schemas/base.py` | BaseVesselSchema — ~20 shared fields |
| `vessel_fleet/schemas/drilling_rig.py` | DrillingRigSchema — ~35 rig-specific fields |
| `vessel_fleet/schemas/construction_vessel.py` | ConstructionVesselSchema — ~20 vessel-specific fields |
| `vessel_fleet/parsers/numeric.py` | Mixed-format numeric parser |
| `vessel_fleet/collectors/base.py` | BaseCollector with rate limit, retry, cache |
| `vessel_fleet/storage/parquet.py` | Parquet store |

### Key patterns to follow

- **BSEEWebScraper** (`bsee/data/scrapers/bsee_web.py`): Session management, retry, streaming
- **WARDataAcquirer** (`bsee/data/loaders/rig_fleet/war_acquirer.py`): Cache with metadata JSON, dependency injection
- **SodirAPIClient** (`sodir/api_client.py`): Rate limiting, TTL cache, exponential backoff
- **RigFleetSchema** (`bsee/data/schemas/rig_fleet.py`): Pydantic validation with coercion

### Tests (Phase 1)

```
tests/modules/vessel_fleet/
├── parsers/test_numeric.py         # All format edge cases from XLS assessment
├── schemas/test_base.py            # Shared field validation
├── schemas/test_drilling_rig.py    # Rig-specific field validation
├── schemas/test_construction.py    # Vessel-specific field validation
├── collectors/test_base.py         # Rate limit, retry, cache behavior
├── storage/test_parquet.py         # Round-trip save/load
└── test_constants.py               # Enum completeness
```

---

## Phase 2A: XLS Ingest (163 Floaters)

**Goal**: Parse `DrillRigs.xls`, transpose, map fields, validate, store as Parquet.

### Files

| File | Purpose |
|------|---------|
| `vessel_fleet/parsers/xls.py` | `XlsFleetParser` — transpose, map, parse compound values |
| `scripts/vessel_fleet/ingest_xls_historical.py` | CLI script to run ingest |

### Key logic

- Transpose XLS (rig-per-column → rig-per-row)
- Map 95 XLS field labels → DrillingRigSchema columns (mapping from assessment doc)
- Parse mixed formats via `numeric.py` ("8,000 ft." → 8000.0)
- Convert ft → m for LOA, BEAM
- Parse compound dimensions ("89.2 ft. x 36.7 ft." → moonpool length + width)
- Map vessel types ("SS" → semi_submersible, "DS" → drillship)
- Set `DATA_SOURCE = "xls_historical"`
- Store raw: `data/modules/vessel_fleet/raw/xls_historical/floaters.parquet`

### Acceptance

- 163 rigs ingested
- Priority 1 fields (10 fields) ≥87% populated
- All pass DrillingRigSchema validation
- No client references (legal scan clean)

---

## Phase 2B: Construction Contractor Fleet Pages (parallel with 2A)

**Goal**: Collect heavy construction and service vessel data from marine contractors.

### Target contractors and vessel counts

| Contractor | Vessels | Types | Free Data |
|------------|---------|-------|-----------|
| Heerema | 3 | Crane vessels (Sleipnir: 20,000t, Thialf: 14,200t) | heerema.com/fleet |
| Allseas | 4+ | Pipelay, heavy-lift (Pioneering Spirit: 48,000t lift) | allseas.com/equipment |
| Saipem | 17 | Pipelay, crane, FPSO install (spec PDFs available) | saipem.com/fleet-and-yards |
| Subsea7 | 10+ | Pipelay, SURF, flex-lay | subsea7.com/our-fleet |
| McDermott | 5+ | Derrick lay, pipelay (Amazon, DLV 2000) | mcdermott.com/fleet |
| Boskalis | 15+ | Heavy transport, crane, cable-lay | boskalis.com/fleet |
| DEME | 6+ | Wind installation, dredging (Orion: 3,000t) | deme-group.com/fleet |
| Van Oord | 5+ | Wind installation (Aeolus, Boreas) | vanoord.com/fleet |
| Eneti/Cadeler | 4 | Wind turbine installation | cadeler.com/fleet |
| OHT | 2+ | Heavy transport (Alfa Lift) | ofrfrshore-heavy-transport.com |

**Estimated total**: ~70-100 vessels

### ConstructionVesselSchema fields

**Shared with base**: VESSEL_NAME, VESSEL_TYPE, OWNER, OPERATOR, IMO_NUMBER, FLAG_STATE, YEAR_BUILT, CLASSIFICATION_SOCIETY, LOA_M, BEAM_M, DISPLACEMENT_TONNES, DP_CLASS, QUARTERS_CAPACITY

**Construction-specific**:

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `MAIN_CRANE_CAPACITY_T` | float | tonnes | Primary crane SWL |
| `MAIN_CRANE_REACH_M` | float | m | Main crane max radius |
| `AUX_CRANE_CAPACITY_T` | float | tonnes | Secondary crane |
| `PIPELAY_CAPACITY_IN` | float | inches | Max pipe diameter |
| `PIPELAY_TENSION_T` | float | tonnes | Max lay tension |
| `PIPELAY_METHOD` | str | -- | S-lay, J-lay, reel-lay |
| `DECK_AREA_M2` | float | m2 | Clear deck area |
| `DECK_LOAD_CAPACITY_T` | float | tonnes | Max deck load |
| `TRANSIT_SPEED_KNOTS` | float | knots | Service speed |
| `BOLLARD_PULL_T` | float | tonnes | If tug/AHTS |
| `HEAVY_LIFT_CAPACITY_T` | float | tonnes | Max single lift |
| `WATER_DEPTH_RATING_M` | float | m | Operational depth |
| `ROV_SYSTEMS` | int | -- | Number of ROV systems |
| `HELIDECK` | bool | -- | Has helideck |
| `VESSEL_SUBTYPE` | str | -- | crane, pipelay, heavy_lift, wind_install, cable_lay, etc. |

### Files

| File | Purpose |
|------|---------|
| `vessel_fleet/schemas/construction_vessel.py` | ConstructionVesselSchema |
| `vessel_fleet/models/construction_vessel.py` | ConstructionVesselEntry |
| `vessel_fleet/configs/construction/*.py` | 10 contractor configs (URLs, selectors, mappings) |
| `scripts/vessel_fleet/collect_construction_fleet.py` | Run all construction collectors |

---

## Phase 3A: Drilling Contractor Fleet Pages

**Goal**: Collect drilling rig specs from 13 contractor fleet pages.

### Target contractors

| Contractor | Rigs | Types | Key Data |
|------------|------|-------|----------|
| Transocean | 27 | Floaters | Spec PDFs at deepwater.com/documents/RigSpecs/*.pdf |
| Valaris | ~52 | Jackups + floaters | Fleet page + quarterly FSR |
| Noble | ~32 | Floaters + jackups | Fleet page + FSR |
| Seadrill | ~12 | Floaters | Fleet page + FSR PDFs |
| Borr Drilling | 29 | Jackups (all modern) | Fleet page + investor presentations |
| COSL | 40+ | Jackups + semisubs | Fleet page (less detailed) |
| ADES/Shelf | 83+40 | Jackups + onshore | Fleet page + FSR |
| Saipem | 12 | Drilling rigs | Detailed spec PDFs |
| Stena | 6 | Drillships + 1 semi | Individual rig pages |
| Vantage | 4 | Drillships + jackups | Spec PDFs |
| Nabors | 200+ | Onshore + MODS platform | Product pages |
| Patterson-UTI | 172 | Onshore super-spec | Fleet overview |
| H&P | 150+ | Onshore FlexRig | Fleet overview |

**Estimated total**: ~800-1000 rigs (floaters ~80, jackups ~200, onshore ~700)

### Collection strategy per contractor type

**Contractors with spec PDFs** (Transocean, Saipem, Vantage):
1. Fetch fleet page HTML → extract rig names + spec PDF URLs
2. Download each spec PDF → extract with pdfplumber
3. Parse key-value pairs from PDF text → map to schema

**Contractors with HTML fleet tables** (Valaris, Noble, Borr, COSL, ADES, Stena):
1. Fetch fleet page HTML → parse table with BeautifulSoup
2. Optionally follow links to individual rig detail pages
3. Map table columns to schema

**Contractors with FSR PDFs** (Seadrill, Borr, Noble, Valaris):
1. Download latest FSR PDF → extract tabular data
2. Provides contract status, dayrate, customer, location

**Onshore rig contractors** (Nabors, Patterson-UTI, H&P):
1. Fetch product/fleet pages → extract rig model specs
2. Onshore rigs are typically described by model (e.g., "PACE-X1500") not individual rig name
3. Capture: model name, hookload, mast height, drawworks HP, drilling depth, walking system

### Jackup-specific fields to capture

| Field | Type | Unit |
|-------|------|------|
| `LEG_LENGTH_FT` | float | ft |
| `LEG_TYPE` | str | -- (independent, mat-supported) |
| `CANTILEVER_REACH_FT` | float | ft |
| `CANTILEVER_CAPACITY_KIPS` | float | kips |
| `PRELOAD_CAPACITY_ST` | float | short tons |
| `SPUD_CAN_DIAMETER_FT` | float | ft |
| `JU_DESIGN` | str | -- (F&G JU-3000N, Gusto MSC CJ50, etc.) |

### Onshore rig-specific fields

| Field | Type | Unit |
|-------|------|------|
| `MAST_HEIGHT_FT` | float | ft |
| `HOOKLOAD_RATING_KIPS` | float | kips |
| `DRAWWORKS_HP` | float | HP |
| `WALKING_SYSTEM` | bool | -- |
| `AC_SCR_POWER` | str | -- (AC, SCR, mechanical) |
| `SETBACK_CAPACITY_KIPS` | float | kips |
| `RIG_MODEL` | str | -- (PACE-X1500, FlexRig3, etc.) |
| `SUPER_SPEC` | bool | -- (1500+ HP, 750k+ setback, 7500+ PSI) |

### Files

| File | Purpose |
|------|---------|
| `vessel_fleet/collectors/fleet_page_collector.py` | HTML fleet page scraper |
| `vessel_fleet/collectors/spec_pdf_collector.py` | PDF spec sheet parser |
| `vessel_fleet/configs/drilling/*.py` | 13 contractor configs |
| `scripts/vessel_fleet/collect_drilling_fleet.py` | Run all drilling collectors |

---

## Phase 4: Maritime Registry Enrichment (Shared)

**Goal**: Add IMO numbers, flag states, classification from free registries. Serves both drilling rigs and construction vessels.

### Sources (all free)

| Source | URL | Fields | Access |
|--------|-----|--------|--------|
| Equasis | equasis.org | IMO, flag, class, owner, MMSI | Free (registration) |
| ABS Record | ww2.eagle.org | Class notations, principal particulars | Free |
| DNV Register | vesselregister.dnv.com | IMO, class status, notations | Free |
| Lloyd's Register | lr.org/ships-in-class | IMO, flag, class notations | Free |
| IACS Search | iacs.org.uk/vessels-in-class | Aggregated across all 12 societies | Free |

### Strategy

1. For each vessel without IMO: search Equasis by name → get IMO + flag + class
2. For each vessel with IMO: lookup ABS/DNV/LR for detailed classification data
3. Cache all lookups aggressively (vessel details change rarely)
4. Rate limit: 1 request per 3 seconds for Equasis (be polite)

### Files

| File | Purpose |
|------|---------|
| `vessel_fleet/collectors/equasis_collector.py` | Equasis vessel lookup |
| `vessel_fleet/collectors/classification_collector.py` | ABS/DNV/LR lookups |
| `scripts/vessel_fleet/enrich_from_registries.py` | Batch enrichment script |

---

## Phase 5: Government Data Enrichment (Shared)

### Sources

| Source | URL | Data | Format |
|--------|-----|------|--------|
| BOEM Data Center | data.boem.gov | Platform structures, drilling permits | CSV download |
| Baker Hughes | rigcount.bakerhughes.com | Weekly rig counts by region/type | Excel download |
| Data.gov MarineCadastre | marinecadastre.gov | Platform geospatial data | GeoJSON, CSV |

### Files

| File | Purpose |
|------|---------|
| `vessel_fleet/collectors/boem_collector.py` | BOEM platform CSV |
| `vessel_fleet/collectors/baker_hughes_collector.py` | Rig count Excel |
| `scripts/vessel_fleet/enrich_from_government.py` | Government data enrichment |

---

## Phase 6: Data Fusion & Quality

### Deduplication

- **Primary key**: IMO_NUMBER (unique, persistent across name/owner changes)
- **Fallback key**: Normalized vessel name (uppercase, stripped prefixes)
- **Merge strategy**: Most-populated record wins per field, with source priority:
  1. Contractor spec sheet PDF (most detailed)
  2. Contractor fleet page HTML
  3. XLS historical data
  4. Equasis / classification registries
  5. BOEM / BSEE / government data
  6. BSEE WAR derived data

### Name normalization

```
"T.O. DEEPWATER TITAN"  → "DEEPWATER TITAN"
"ENSCO 87"              → "ENSCO 87" (keep, it's the actual name)
"VALARIS DS-4"          → "VALARIS DS-4"
"M/V SLEIPNIR"          → "SLEIPNIR"
"SAIPEM 10000"          → "SAIPEM 10000"
```

### Quality checks

- Cross-field: Jackups should not have DP_CLASS > 1; onshore rigs should not have DISPLACEMENT
- Range: WATER_DEPTH_RATING_FT 0-40,000; YEAR_BUILT 1950-2030
- Format: IMO_NUMBER is 7 digits; FLAG_STATE is ISO 3166 code
- Completeness: Score per vessel, report per fleet category

### Files

| File | Purpose |
|------|---------|
| `vessel_fleet/dedup/normalizer.py` | Vessel name normalization |
| `vessel_fleet/dedup/deduplicator.py` | Multi-source dedup + merge |
| `vessel_fleet/quality/validator.py` | Cross-field validation |
| `vessel_fleet/quality/completeness.py` | Completeness scoring |
| `scripts/vessel_fleet/fuse_and_deduplicate.py` | Merge all sources |
| `scripts/vessel_fleet/export_fleet.py` | Export curated Parquet + CSV |
| `scripts/vessel_fleet/run_full_pipeline.py` | End-to-end orchestrator |

---

## BSEE Integration Bridge

The existing `bsee/data/loaders/rig_fleet/` stays untouched. Add one method to `rig_fleet_loader.py`:

```python
def export_to_vessel_fleet(self, war_df: pd.DataFrame) -> pd.DataFrame:
    """Export BSEE WAR fleet data in global DrillingRigSchema format."""
```

This feeds BSEE data as one source into the global fusion pipeline.

---

## Implementation Order

```
Week 1: Phase 1 (shared infrastructure) — TDD, all parsers and base collector tested
         ↓
Week 2: Phase 2A (XLS ingest)    ║    Phase 2B (construction vessel configs) — PARALLEL
         ↓                        ║         ↓
Week 3: Phase 3A (drilling configs — top 5 contractors first)
         ↓
Week 4: Phase 4 (registry enrichment) + Phase 5 (government data)
         ↓
Week 5: Phase 6 (fusion, dedup, quality) + BSEE bridge
```

### Priority contractors (implement first)

**Drilling** (Phase 3A, first batch):
1. Transocean — best spec PDFs, clear URL pattern
2. Valaris — largest mixed fleet, good HTML tables
3. Borr — pure jackup fleet, modern data
4. Saipem — detailed spec PDFs
5. Noble — post-Diamond acquisition, large fleet

**Construction** (Phase 2B, first batch):
1. Heerema — iconic crane vessels, clean fleet page
2. Allseas — Pioneering Spirit, well-documented
3. Saipem vessels — detailed PDFs already available
4. Subsea7 — good fleet page

---

## Target Fleet Size

| Category | Current | Target | Sources |
|----------|---------|--------|---------|
| Drillships | 0 (16 WAR) | ~50 | XLS + contractors |
| Semisubmersibles | 0 | ~40 | XLS + contractors |
| Jackups | 0 | ~200 | Contractors (Borr, Valaris, Noble, ADES, COSL) |
| Onshore/Land rigs | 0 | ~500+ | Contractors (Nabors, P-UTI, H&P, ADES) |
| Platform rigs | 0 | ~30 | Nabors MODS, others |
| Crane vessels | 0 | ~15 | Heerema, Saipem, others |
| Pipelay vessels | 0 | ~20 | Allseas, Saipem, Subsea7, McDermott |
| Heavy-lift/transport | 0 | ~10 | Allseas, Boskalis, OHT |
| Wind installation | 0 | ~15 | DEME, Van Oord, Cadeler |
| **Total** | **16** | **~900+** | |

---

## Legal Compliance

- All sources are publicly available contractor fleet pages and government databases
- No subscription data (RigLogix, Petrodata, Esgian premium excluded)
- No client references in any code, comments, paths
- Run `scripts/legal/legal-sanity-scan.sh --repo=worldenergydata` before every commit
- `DATA_SOURCE_URL` field provides full provenance for every record

---

## Verification

1. **Unit tests**: Each parser, collector, schema, model has dedicated test file with fixtures
2. **Integration test**: `scripts/vessel_fleet/run_full_pipeline.py` produces curated Parquet
3. **Quality report**: Completeness scores per vessel category ≥70% on core fields
4. **Dedup check**: No duplicate IMO numbers in final fleet
5. **Legal scan**: Zero violations before commit
6. **Test command**: `PYTHONPATH="src:../assetutilities/src" python3 -m pytest tests/modules/vessel_fleet/ -v --tb=short --noconftest`

---

## Critical Files Reference

| Existing File | Purpose |
|---------------|---------|
| `src/worldenergydata/bsee/data/scrapers/bsee_web.py` | Web scraper pattern (session, retry, streaming) |
| `src/worldenergydata/bsee/data/loaders/rig_fleet/war_acquirer.py` | Cache + metadata pattern |
| `src/worldenergydata/sodir/api_client.py` | Rate limit + TTL cache pattern |
| `src/worldenergydata/bsee/data/schemas/rig_fleet.py` | Pydantic schema pattern |
| `src/worldenergydata/bsee/data/models/rig_fleet.py` | Dataclass model pattern |
| `docs/data/rig-fleet-xls-assessment.md` | XLS field mapping (Phase 2A reference) |
