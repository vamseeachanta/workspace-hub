---
title: "WRK-116: Comprehensive GOM Activity Analysis"
description: "Multi-phase data-to-insights pipeline combining WAR, borehole, and paleowells data for drilling + intervention analysis"
version: "1.0"
module: bsee/analysis/intervention
session:
  id: expressive-marinating-dolphin
  agent: claude-opus-4-6
review:
  status: cross-reviewed
  reviewers:
    - agent: architecture-reviewer (a821cec)
      verdict: APPROVE_WITH_CHANGES
    - agent: testing-reviewer (a5f3895)
      verdict: APPROVE_WITH_CHANGES
    - agent: data-engineering-reviewer (a8fca75)
      verdict: APPROVE_WITH_CHANGES
---

# WRK-116: Comprehensive GOM Activity Analysis

## Context

The current drilling and intervention reports are built from **WAR data + fleet classification only**. This limits analysis to activity counts and rig type distribution. Key gaps:

- **Drilling duration** is estimated (WAR records × 7 days) — actual SPUD_DATE / TD_DATE data exists but is not integrated
- **Well depth** (BH_TOTAL_MD) is empty in WAR data — the borehole dataset has it for all wells
- **Water depth** coverage is 11% in WAR — borehole data has near-100% coverage
- **Geological era** classification exists (Paleowells.csv, 6,363 wells) but is not connected to activity reports
- **Well status** (completed, P&A'd, suspended) is not analyzed

**Goal**: Build a data-to-insights pipeline: DATA → ENRICHMENT → ANALYSIS → INSIGHTS → REPORTS.

### Iterative Research & Domain Refinement

After completing each phase, conduct a domain research review before starting the next:

1. **Post-Phase Research**: Search field expert documentation (SPE papers, BSEE technical reports, OCS regulations, drilling engineering references) to validate methodologies used and identify industry-standard approaches for the next phase.
2. **Methodology Validation**: Compare our analysis approaches against published GOM studies — e.g., MMS/BSEE annual reports, OCS operations reports, drilling performance benchmarks.
3. **Data Dictionary Cross-Check**: Verify column interpretations against BSEE's official data dictionary (available on data.bsee.gov) to ensure correct semantic mapping.
4. **Gap Identification**: As more data becomes available after each phase, reassess which additional analyses or data sources could improve output quality.
5. **Expert Pattern Matching**: Review how petroleum engineering professionals present similar analysis — drilling efficiency metrics, well design standards (API RP 96, API Spec 5CT for casing grades), completion best practices — and align our output format accordingly.

This ensures each phase builds on validated domain knowledge rather than assumptions, producing outputs that match industry expectations.

## Data Sources Inventory

| Source | Location | Records | Status | Key Columns |
|--------|----------|---------|--------|-------------|
| WAR activity | `.local/war/` (cached) | 2M | Ready | RIG_NAME, API_WELL_NUMBER, dates, AREA_CODE |
| Rig fleet | `.local/rig_fleet/` (cached) | 2,320 | Ready | RIG_NAME, RIG_TYPE |
| **Borehole** | **BSEE download needed** | ~57K | **Phase 1** | WELL_SPUD_DATE, TOTAL_DEPTH_DATE, BH_TOTAL_MD, WATER_DEPTH, BOREHOLE_STAT_CD |
| Paleowells | `paleowells/Paleowells.csv` | 6,363 | Ready | API_WELL_NUMBER → geological era |
| well_data.csv | `current/wells/` | 100 (sample) | Superseded by borehole download |

**Critical finding**: `well_data.csv` is only 100 sample rows. The full well dataset must be downloaded. **Approach**: Use `BoreholeRawData.zip` directly (URL in `BSEEDataDownloader.DATA_SOURCES["borehole"]` at `src/.../paleowells/data_downloader.py:28`). APDRawData.zip is permit data, NOT borehole data.

**Cross-review correction**: All 3 reviewers flagged that APD ≠ Borehole. Existing loaders: `WellData.get_BoreholeRawData_from_bin()` in `src/.../loaders/api/well.py` and `BSEEDataDownloader` in `paleowells/data_downloader.py`.

## Phase 0: SHARED INFRASTRUCTURE (prerequisite)

**Objective**: Extract shared utilities before Phase 1 to prevent duplication.

### 0a. API Well Number Normalizer
**File**: `src/.../data/utils/api_well_normalizer.py` (~40 lines)
```python
def normalize_api_well_number(series: pd.Series) -> pd.Series:
    """Normalize API well numbers to stripped strings without trailing .0"""
```
Handles: float64 → str (drop `.0`), int64 → str, "API Well Number" (with spaces) column rename, zero-padding normalization.

### 0b. Shared Test Fixtures
**File**: `tests/modules/bsee/analysis/intervention/conftest.py` (~120 lines)
- Shared `_make_war_df()`, `_make_fleet_df()`, `_make_empty_war_df()` fixtures
- New `_make_borehole_df()`, `_make_enriched_df()` fixtures
- Consolidates 4+ duplicate fixture definitions across existing test files

### 0c. Report HTML Utilities (stretch)
Extract `_fhtml()`, `_tbl()`, `_bul()`, CSS constants from dashboard.py into a shared module if duplication grows.

**Tests**: `tests/.../data/utils/test_api_well_normalizer.py` (~60 lines)

---

## Phase 1: DATA ACQUISITION — Borehole Download + Cache

**Objective**: Download borehole well data and cache it following the WAR acquirer pattern.

### 1a. Use BoreholeRawData.zip directly
**URL**: `BoreholeRawData.zip` (already in `BSEEDataDownloader.DATA_SOURCES["borehole"]`).
**NOT** APDRawData.zip — APD is permit data, not borehole measurements.

Existing loaders to evaluate for reuse:
- `WellData.get_BoreholeRawData_from_bin()` at `src/.../loaders/api/well.py`
- `BSEEDataDownloader` at `src/.../paleowells/data_downloader.py`

### 1b. Create BoreholeDataAcquirer
**File**: `src/.../data/loaders/well/borehole_acquirer.py` (~150 lines)
- Replicate `war_acquirer.py` pattern exactly (DI for scraper + processor)
- Cache to `data/modules/bsee/.local/borehole/`
- Normalize columns: API_WELL_NUMBER via shared normalizer, dates (datetime), depths (float32)
- **Deduplicate sidetracks**: Group by API_WELL_NUMBER, keep primary bore (SIDETRACK_CD == "ST00BP00" or first)
- 30-day cache freshness
- **Column mapping**: WELL_SPUD_DATE, TOTAL_DEPTH_DATE, BH_TOTAL_MD, WATER_DEPTH, BOREHOLE_STAT_CD

### 1c. Build script
**File**: `scripts/build_borehole_data.py` (~60 lines)

### Tests
**File**: `tests/.../loaders/well/test_borehole_acquirer.py` (~200 lines)
- Mock scraper/processor, test column normalization, cache logic
- Test sidetrack deduplication
- Test API_WELL_NUMBER normalization (float, int, string inputs)

### Reuse
- `war_acquirer.py` — identical download/cache/normalize pattern
- `BSEEDataDownloader` — existing borehole URL and download logic
- `MemoryProcessor` — existing zip extraction
- `normalize_api_well_number()` — shared normalizer (Phase 0)

**Verification**: Download completes, pickle cached, ~57K unique wells (deduplicated) with WELL_SPUD_DATE, TOTAL_DEPTH_DATE, BH_TOTAL_MD populated.

### Post-Phase 1 Research Gate
- Review BSEE data dictionary for borehole table to confirm column semantics (BOREHOLE_STAT_CD codes, SIDETRACK_CD format)
- Verify actual column names in downloaded data match plan assumptions
- Identify any additional useful columns not originally planned (e.g., WELL_TYPE_CD, COMPLETION_NAME)
- Check data.bsee.gov for any supplementary datasets that could enrich the pipeline

---

## Phase 2: DATA ENRICHMENT — Multi-Source Join Engine

**Objective**: Join WAR + Fleet + Borehole + Paleowells into one enriched DataFrame.

### Create ActivityEnrichmentEngine
**File**: `src/.../analysis/intervention/enrichment_engine.py` (~200 lines)

```python
class ActivityEnrichmentEngine:
    def __init__(self, war_df, fleet_df, borehole_df, era_classifier): ...
    def enrich(self) -> pd.DataFrame: ...
```

**Join pipeline**:
1. WAR → Fleet (left-join on RIG_NAME, heuristic fallback) — reuse `WARActivityAggregator._join_rig_types()`
2. WAR → Borehole (left-join on normalized API_WELL_NUMBER) — adds WELL_SPUD_DATE, TOTAL_DEPTH_DATE, BH_TOTAL_MD, BH_WATER_DEPTH, BOREHOLE_STAT_CD
   - **Column conflict**: WAR has `WATER_DEPTH`; borehole has `WATER_DEPTH`. Rename borehole's to `BH_WATER_DEPTH`, then coalesce: `WATER_DEPTH_FINAL = WAR.WATER_DEPTH.fillna(BH_WATER_DEPTH)`
   - **Sidetrack safety**: Borehole must be pre-deduplicated in Phase 1 (one row per API_WELL_NUMBER)
3. WAR → Paleowells (vectorized `Series.map(dict)` via `era_classifier.get_well_eras()` — NOT per-row `.apply()`)

**Derived columns**:
- `DRILLING_DAYS` = (TOTAL_DEPTH_DATE - WELL_SPUD_DATE).days — actual, per well
- `WATER_DEPTH_CLASS` = Shallow (<500ft) / Mid (500-1500) / Deep (1500-5000) / Ultra-deep (>5000)
- `GEOLOGICAL_ERA` = from paleowells (Miocene, Eocene, etc.) — ~11% coverage, note in reports
- `ACTIVITY_CATEGORY` = drilling / intervention / unknown
- `WELL_STATUS` = BOREHOLE_STAT_CD mapped to human-readable (COM/PA/TA/DRL)

**Memory optimization**: Use `category` dtype for RIG_TYPE, ACTIVITY_CATEGORY, AREA_CODE, WELL_STATUS. Use `float32` for depths.

**Key design**: Enrichment produces row-level data (2M rows). No aggregation here — that's Phase 3.

### Data Validation Gate (between Phase 2 → Phase 3)
Before passing to Phase 3, verify:
- Row count matches original WAR count (no row explosion from joins)
- At least 60% of rows have non-null BH_TOTAL_MD (borehole join success)
- At least 5% of rows have non-null GEOLOGICAL_ERA (paleowells join success)
- No negative DRILLING_DAYS values
- Log join hit rates for each source

### Tests
**File**: `tests/.../analysis/intervention/test_enrichment_engine.py` (~300 lines)
- Test borehole join fills water depth gaps
- Test DRILLING_DAYS computation (correct column names: WELL_SPUD_DATE, TOTAL_DEPTH_DATE)
- Test negative DRILLING_DAYS clamped to NaN
- Test era mapping via vectorized Series.map
- Test unmatched wells get NaN enrichment
- Test empty inputs handled gracefully
- Test WATER_DEPTH column conflict resolution (coalesce WAR → borehole)
- Test API_WELL_NUMBER normalization across formats (float, int, string, zero-padded)
- Test row count preservation (no explosion from many-to-many)

### Reuse
- `WARActivityAggregator._join_rig_types()` — rig type join logic
- `GeologicalEraClassifier.get_well_eras()` — era mapping dict
- `classify_activity()` — activity category assignment

**Verification**: Enriched DataFrame has all WAR rows + new columns. Run on real data, verify join hit rates.

### Post-Phase 2 Research Gate
- Review join hit rates and identify why unmatched records exist — consult BSEE well numbering standards (API Bulletin D12A)
- Research water depth classification conventions used in GOM studies (shallow/deep/ultra-deep boundaries vary by source — MMS uses 1,000ft, industry often uses 1,500ft)
- Validate DRILLING_DAYS computation against published benchmarks (SPE drilling performance papers for GOM wells)
- Assess whether additional derived columns would improve downstream analysis (e.g., WELL_AGE, DAYS_SINCE_LAST_ACTIVITY)

---

## Phase 3: ANALYSIS — Comprehensive Cross-Cutting Analyzer

**Objective**: Compute structured analysis metrics from the enriched DataFrame.

### Create ComprehensiveActivityAnalyzer
**File**: `src/.../analysis/intervention/comprehensive_analyzer.py` (~400 lines)

```python
class ComprehensiveActivityAnalyzer:
    def __init__(self, enriched_df): ...
    def analyze(self) -> dict: ...
```

**Analysis modules** (each returns a dict/DataFrame):

| Module | Key Metrics |
|--------|-------------|
| `drilling_efficiency` | Actual drilling days distribution, by rig type, by depth class, by era |
| `well_depth` | BH_TOTAL_MD distribution, depth by rig type/area, depth trends over time |
| `geological_era` | Activity counts by era, drilling vs intervention by era, era trends |
| `cross_activity` | Drilling-to-intervention ratio by field/era/depth, wells with both activities |
| `well_lifecycle` | Status distribution (COM/PA/TA), status by depth class, completion rate |
| `operator_portfolio` | Operators by depth class, rig type preference, area diversification |
| `duration_benchmarking` | Drilling days by depth × rig type, performance quartiles |

### Tests
**File**: `tests/.../analysis/intervention/test_comprehensive_analyzer.py` (~400 lines)
- Test all 7 analysis keys returned
- Test drilling efficiency uses actual days (TOTAL_DEPTH_DATE - WELL_SPUD_DATE, not WAR×7 estimate)
- Test empty input returns empty results for all modules
- Test each analysis module independently (7 × ~40 lines)
- Test edge cases: all-drilling data, all-intervention data, single-year data

### Reuse
- All aggregation patterns from `WARActivityAggregator.aggregate_by_year_and_type()`

**Verification**: Run on enriched data, verify metric counts match expectations.

### Post-Phase 3 Research Gate
- Compare drilling efficiency metrics against published GOM benchmarks (IADC drilling performance reports, SPE/IADC conference papers)
- Review geological era analysis methodology against BOEM geological assessments and paleontological zone classifications
- Research operator performance benchmarking approaches used in industry (Rushmore Reviews, drilling KPIs)
- Validate well lifecycle status interpretations against BSEE well status codes and regulatory definitions
- Identify any industry-standard KPIs or metrics that should be added to the analyzer

---

## Phase 4: INSIGHTS — Narrative Insight Generator

**Objective**: Transform analysis results into ranked business findings.

### Create InsightGenerator
**File**: `src/.../analysis/intervention/insight_generator.py` (~200 lines)

```python
class InsightGenerator:
    def __init__(self, analysis_results: dict): ...
    def generate(self) -> dict: ...
```

**Insight categories**:
- `key_findings` — Top 5 data-driven observations (ranked by significance)
- `market_trends` — Growth/decline by segment
- `competitive_intelligence` — Operator positioning
- `opportunity_areas` — Underserved segments
- `risk_factors` — Declining areas, regulatory trends

Pure programmatic pattern detection — compare values, rank deltas, identify outliers. No LLM calls.

### Tests
**File**: `tests/.../analysis/intervention/test_insight_generator.py` (~200 lines)
- Test all 5 insight categories returned with non-empty lists
- Test each category independently with targeted synthetic data
- Test edge cases: flat trends (no growth/decline), single operator, single area

**Verification**: Each insight section returns non-empty list of strings.

### Post-Phase 4 Research Gate
- Review market intelligence report formats from industry analysts (Wood Mackenzie, Rystad Energy, IHS Markit/S&P Global) for structure and terminology
- Research how competitive intelligence is presented in oilfield services market reports
- Validate trend detection methodology — review statistical approaches for identifying significant changes vs noise in cyclical energy markets
- Cross-reference insights against known GOM events (Macondo moratorium 2010, COVID downturn 2020, recent rig market recovery) to validate temporal patterns

---

## Phase 5: REPORTS — Enhanced HTML Reports

**Objective**: Rewrite drilling report to use enriched data; update dashboard.

### 5a. Enhanced Drilling Report
**File**: `src/.../analysis/intervention/drilling_report.py` (rewrite, ~450 lines)

New constructor: `__init__(self, enriched_df, analysis_results, insights)`

**New/enhanced sections**:
- **Actual Drilling Duration** — real SPUD→TD days, not WAR×7 estimate. Actual vs estimated comparison scatter.
- **Well Depth Analysis** — BH_TOTAL_MD distributions (histogram + by rig type + by area)
- **Geological Era** — stacked bar of activity by era, drilling vs intervention per era
- **Well Lifecycle** — status distribution (COM/PA/TA), completion rate by depth class
- **Duration Benchmarking** — boxplots by depth class × rig type
- **Key Insights** — narrative section from InsightGenerator

Backward compatibility: keep old `__init__(war_df, fleet_df)` signature as alternative constructor.

### 5b. Enhanced Build Script
**File**: `scripts/build_enhanced_reports.py` (~100 lines)

Master pipeline:
1. Load WAR + Fleet + Borehole + Paleowells
2. Run enrichment → analysis → insights
3. Generate all 3 reports (drilling, intervention detail, dashboard)

### 5c. Dashboard Update
**File**: `src/.../analysis/intervention/dashboard.py` — add key insights summary + enhanced cross-links (~30 lines)

### Tests
Update `test_drilling_report.py` with tests for new sections and enriched data path.

### 5d. Pipeline Integration Test
**File**: `tests/.../analysis/intervention/test_pipeline_integration.py` (~150 lines)
- End-to-end test: synthetic data → enrichment → analysis → insights → report generation
- Validates schema compatibility across all phases
- Uses shared fixtures from `conftest.py`
- No network/filesystem dependencies

**Verification**: `build_enhanced_reports.py` produces all 3 reports. All tests pass. Integration test validates full pipeline.

### Post-Phase 5 Research Gate
- Review report output against professional engineering analysis reports — formatting, chart types, narrative structure
- Research how BSEE/BOEM publishes their own GOM activity summaries and align terminology
- Validate that report sections address the key questions an engineering services company would ask about the GOM intervention market
- Assess whether additional report types are needed (e.g., per-operator deep-dive, per-area summary, time-series forecast)

---

## Phase 6: WELL DESIGN — Casing Program & Well Architecture Analysis

**Objective**: Analyze well design data (casing program, completions, geology, BOP) to understand drilling engineering decisions.

### Data Sources (all in `data/modules/bsee/current/`)

| File | Records | Key Columns | Analysis |
|------|---------|-------------|----------|
| `wells/well_tubulars.csv` | ~1000 | CSNG_HOLE_SIZE, CASING_SIZE, CASING_GRADE, CSNG_SETTING_BOTM_MD, CSNG_CEMENT_VOL | Casing program reconstruction |
| `completions/completion_perforations.csv` | ~100 | PERF_TOP_MD, PERF_BOTM_TVD, PERF_BASE_MD | Production target depths |
| `geology/geology_markers.csv` | ~100 | GEO_MARKER_NAME, TOP_MD | Formation tops |
| `geology/hydrocarbon_bearing_interval.csv` | ~100 | INTERVAL_NAME, TOP_MD, BOTTOM_MD, HYDROCARBON_TYPE_CD | Pay zones (oil/gas) |
| `operations/well_activity_bop_tests.csv` | ~100 | RAM_TST_PRSS, ANNULAR_TST_PRSS | Well pressure envelope |
| `operations/well_activity_open_hole.csv` | ~100 | LOG_INTV_TOP_MD, LOG_INTV_BOTM_MD, TOOL_LOGGING_METHOD_NAME | Logging data |
| `operations/cut_casings.csv` | ~100 | CASING_CUT_DEPTH, CASING_CUT_METHOD_CD | Abandonment ops |

**Note**: These are sample CSVs (~100 rows each). Full data comes from the APD/WAR zips (Phase 1). The WAR zip has `mv_war_tubular_summaries.txt` with 389K rows of casing data.

### Create WellDesignAnalyzer
**File**: `src/.../analysis/intervention/well_design_analyzer.py` (~350 lines)

```python
class WellDesignAnalyzer:
    def __init__(self, well_df, tubulars_df, perforations_df, geology_df): ...
    def analyze(self) -> dict: ...
```

**Analysis capabilities**:

1. **Casing Program Summary**: Reconstruct casing strings per well — hole size progression (36" → 26" → 17.5" → 12.25" → 8.5"), casing sizes, grades, setting depths
2. **Well Design Classification**: Vertical vs deviated vs horizontal (from MD/TVD ratio + kickoff depth), subsea vs surface completion (UNDWTR_COMP_STUB)
3. **Casing Grade Analysis**: Grade distribution (K-55, P-110, Q-125, etc.) by water depth class and era
4. **Cement Coverage**: Cement volume vs interval length ratios — quality indicator
5. **Pressure Envelope**: BOP test pressures correlated with water depth and well depth
6. **Formation Penetration**: Geology markers depth sequence — identify key formation boundaries that drive casing seat decisions
7. **Pay Zone Targeting**: Perforation intervals relative to casing shoes — completion strategy

### Tests
**File**: `tests/.../analysis/intervention/test_well_design_analyzer.py` (~150 lines)

**Verification**: Run on sample CSVs, verify casing program reconstruction for known wells.

### Post-Phase 6 Research Gate
- Review casing design standards: API Spec 5CT (casing/tubing specs), API RP 96 (deepwater well design), API RP 65-2 (cementing)
- Research typical GOM well architectures by water depth class — validate casing program patterns against published well schematics
- Cross-reference casing grade selections with pressure/temperature envelopes (API TR 5C3)
- Review BSEE regulations on well design requirements (30 CFR 250 Subpart D) to validate status code interpretations
- Assess whether additional well design data from the downloaded borehole zip could enhance analysis

---

## Phase 7: VISUALIZATION — Field/Lease Architecture Module

**Objective**: Create an interactive visualization module that shows lease/field layout for end users using GIS maps, Plotly 3D, and Blender export.

### Existing Capabilities to Reuse

| Capability | Location | Technology |
|------------|----------|------------|
| Well location maps | `src/.../reports/comprehensive/visualizations/geographic_charts.py` | Plotly Scattermapbox |
| 3D well trajectories | `geographic_charts.py` | Plotly Scatter3d |
| Blender automation | `digitalmodel/src/.../blender_automation/` | subprocess wrapper |
| Mesh export (STL/OBJ/GLTF) | `digitalmodel/src/.../mesh_exporter.py` | Blender export pipeline |
| OBJ mesh visualization | `vessel_hull_models/visualization/plotly_3d.py` | Plotly Mesh3d |
| SVG schematics | `digitalmodel/.../rod_pump_schematic.py` | Custom SVG |

### Create FieldVisualizationModule
**File**: `src/.../analysis/intervention/field_visualization.py` (~400 lines)

```python
class FieldVisualizationModule:
    def __init__(self, enriched_df, well_design_data, field_code=None): ...

    def generate_map(self, output_path) -> str: ...          # GIS map (Plotly Scattermapbox)
    def generate_3d_view(self, output_path) -> str: ...      # Plotly 3D subsurface
    def generate_well_schematic(self, api, output_path): ... # SVG casing diagram
    def export_blender_scene(self, output_path) -> str: ...  # GLTF/OBJ for Blender
```

**Visualization layers**:

1. **GIS Map View** (Plotly Scattermapbox — HTML output)
   - Well locations color-coded by status (COM/PA/TA/DRL)
   - Marker size by activity count or depth
   - Field/lease boundary overlay (from AREA_CODE + BLOCK_NUMBER)
   - Water depth contours from well locations
   - Hover info: well name, operator, depth, rig used, era

2. **3D Subsurface View** (Plotly Scatter3d — HTML output)
   - Well trajectories: surface → kickoff → bottom (using SURF_LAT/LON, BOTM_LAT/LON, WATER_DEPTH, BH_TOTAL_MD)
   - Seabed surface plane at WATER_DEPTH
   - Formation layers from geology markers
   - Color wells by rig type, operator, or era
   - Casing shoe depth markers along trajectory

3. **Well Casing Schematic** (SVG — per well)
   - Vertical cross-section showing:
     - Water column (blue)
     - Conductor, surface casing, intermediate casing, production liner
     - Hole sizes and casing OD labels
     - Setting depths (MD)
     - Cement intervals
     - Perforation zones (red markers)
     - Formation names at marker depths
   - Reuse SVG generation pattern from digitalmodel rod_pump_schematic

4. **Blender Export** (GLTF/OBJ — for offline 3D)
   - Export well trajectories as 3D curves
   - Casing strings as cylinders at correct depths
   - Seabed mesh at water depth
   - Formation planes
   - Uses `digitalmodel` BlenderWrapper for post-processing
   - Output: `.gltf` file viewable in Blender, web (three.js), or AR/VR

### Build Script
**File**: `scripts/build_field_visualization.py` (~80 lines)
- Takes --field-code or --area-code to scope visualization
- Generates map + 3D view + schematics for top wells

### Tests
**File**: `tests/.../analysis/intervention/test_field_visualization.py` (~150 lines)
- Test map generation with synthetic coordinate data
- Test 3D view generates valid HTML
- Test SVG schematic contains casing elements
- Test empty data handled gracefully

**Verification**: Generate visualization for a real field (e.g., MC area), open in browser.

### Post-Phase 7 Research Gate
- Review GIS visualization best practices for subsurface data — OGC standards, well trajectory conventions
- Research how operators and service companies visualize field architecture (Petrel, OpenWorks, COMPASS comparisons for Plotly output quality)
- Validate 3D well trajectory interpolation against directional survey standards (minimum curvature method)
- Assess Blender export quality against industry 3D visualization tools
- Review BOEM lease/block boundary data availability for more accurate map overlays

---

## Updated Dependency Order

```
Phase 0 (shared infra) ───────────────────────┐
Phase 1 (borehole data download) ─────────────┤
Paleowells (already on disk) ──────────────────┤
WAR + Fleet (already cached) ──────────────────┤
                                               ▼
Phase 2 (enrichment engine) ───────────────────┤
                                               ▼
Phase 3 (comprehensive analyzer) ──────────────┤
                          ┌────────────────────┤
                          ▼                    ▼
Phase 4 (insight gen)     Phase 6 (well design)
                          │                    │
                          ▼                    ▼
Phase 5 (enhanced reports) ◄───────────────────┤
                                               ▼
                          Phase 7 (visualization)
```

Phases 4 and 6 can run in parallel after Phase 3. Phase 7 depends on Phases 5+6.

## Updated Critical Files

| File | Action | Phase |
|------|--------|-------|
| `src/.../data/utils/api_well_normalizer.py` | **New** | 0 |
| `tests/.../analysis/intervention/conftest.py` | **New** | 0 |
| `src/.../loaders/well/borehole_acquirer.py` | **New** | 1 |
| `scripts/build_borehole_data.py` | **New** | 1 |
| `src/.../intervention/enrichment_engine.py` | **New** | 2 |
| `src/.../intervention/comprehensive_analyzer.py` | **New** | 3 |
| `src/.../intervention/insight_generator.py` | **New** | 4 |
| `src/.../intervention/drilling_report.py` | **Rewrite** | 5 |
| `src/.../intervention/dashboard.py` | Modify | 5 |
| `scripts/build_enhanced_reports.py` | **New** | 5 |
| `tests/.../intervention/test_pipeline_integration.py` | **New** | 5 |
| `src/.../intervention/well_design_analyzer.py` | **New** | 6 |
| `src/.../intervention/field_visualization.py` | **New** | 7 |
| `scripts/build_field_visualization.py` | **New** | 7 |

## Risks & Mitigations

1. **API_WELL_NUMBER format mismatch** — WAR (string), borehole (float64), paleowells (spaced column name). **Mitigation**: Phase 0 shared normalizer applied to all sources before any join.
2. **Borehole sidetrack row explosion** — Multiple rows per API_WELL_NUMBER (ST00BP00, ST01BP00, etc.). **Mitigation**: Deduplicate in Phase 1 acquirer, keep primary bore only.
3. **WATER_DEPTH column conflict** — Both WAR and borehole have this column. **Mitigation**: Rename borehole's to BH_WATER_DEPTH, coalesce in enrichment.
4. **Paleowells coverage** — only 6,363 of ~57K wells have era data (~11%). Note this limitation in reports.
5. **Memory** — Peak during joins could reach 1.5-2GB. **Mitigation**: Use `category` dtype for categorical columns, `float32` for depths.
6. **Sample data limitation** — casing/geology/completion CSVs are ~100 rows each (samples). Full tubular data (389K rows) requires WAR zip extraction. Phase 6 should work with whatever is available.
7. **Blender dependency** — Blender export is optional; core viz uses Plotly (web-only, no install needed). Blender integration via digitalmodel repo is a stretch goal.
8. **Coordinate data** — well_data.csv has coordinates but only 100 sample rows. Full coordinates come from borehole download (Phase 1).
9. **Existing loader duplication** — `WellData.get_BoreholeRawData_from_bin()` and `BSEEDataDownloader` already handle borehole data. **Mitigation**: Evaluate reuse in Phase 1; wrap existing logic if suitable, else document why new acquirer is needed.

---

## Cross-Review Summary

3 reviewers, all returned **APPROVE_WITH_CHANGES**. Key corrections applied:

| Issue | Severity | Resolution |
|-------|----------|------------|
| APD ≠ Borehole data | HIGH | Changed to BoreholeRawData.zip |
| Column names (SPUD_DATE→WELL_SPUD_DATE) | HIGH | Fixed throughout |
| Existing borehole loaders not acknowledged | HIGH | Added to Phase 1 reuse list |
| API_WELL_NUMBER type inconsistency | HIGH | Added Phase 0 shared normalizer |
| Sidetrack row explosion risk | HIGH | Added deduplication in Phase 1 |
| Test budget too low (0.37 ratio) | HIGH | Increased to ~2,050 lines (0.75 ratio) |
| No shared test fixtures | MEDIUM | Added conftest.py in Phase 0 |
| No integration test | MEDIUM | Added test_pipeline_integration.py in Phase 5d |
| WATER_DEPTH column conflict | MEDIUM | Added rename+coalesce strategy |
| Memory underestimate | MEDIUM | Added category/float32 optimization |
| Data validation gate missing | MEDIUM | Added between Phase 2→3 |

## Estimated Scope

- **Phase 0**: ~160 lines source + ~180 lines tests (shared infra)
- **Phases 1-5**: ~1,900 lines source + ~1,250 lines tests (core pipeline)
- **Phase 6**: ~350 lines source + ~250 lines tests (well design)
- **Phase 7**: ~400 lines source + ~200 lines tests (visualization)
- **Total**: ~2,810 lines source + ~1,880 lines tests across 14 new/modified files
- 8 phases (0-7), with parallelism possible after Phase 3
