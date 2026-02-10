# WRK-011: BSEE All-Lease Field Analysis with Nicknames and Geological Era Grouping

---
title: "BSEE All-Lease Field Analysis"
description: "Expand BSEE analysis to all leases with field nickname lookup and geological era classification"
version: "1.0"
module: worldenergydata/bsee
session:
  id: enumerated-conjuring-cake
  agent: claude-opus-4.6
review:
  status: pending
  related: [WRK-009, WRK-010, WRK-011]
---

## Context

WRK-010 successfully ran production and financial analysis for 7 lower tertiary fields (Jack/St. Malo, Stones, Julia, Anchor, Cascade/Chinook, Shenandoah, Big Foot). WRK-011 expands this to ALL leases in the BSEE database, adding field nickname mapping and geological era grouping.

**User decision**: Two-tier approach — full financial analysis for the 7 known fields (existing configs), production-only for all other fields. Field nicknames derived from BSEE data.

## Approach: Two-Tier Analysis + Field Discovery

### Tier 1: All Fields — Production Analysis + Geology + Nicknames
- Load all production data from BSEE historical OGOR files
- Aggregate by field (via `BOTM_FLD_NAME_CD` / `FIELD_NAME_CODE`)
- Join with Paleowells data for geological era classification
- Derive field display names from `deepwater_field_leases.bin` and platform structure data
- Generate per-field production summaries and grouped-by-era report

### Tier 2: Lower Tertiary Fields — Full Financial Analysis
- Reuse existing `config/analysis/lower_tertiary/fields/*.yml` configs
- Run the existing WRK-010 financial pipeline (NPV, IRR, cash flow)
- Include in the all-fields report with financial columns populated

## Implementation Steps

### Step 1: Field Name Resolver (new module)

**File**: `src/worldenergydata/bsee/data/field_names.py`

Build a `FieldNameResolver` class that:
1. Loads `data/modules/bsee/bin/deepqual/mv_deep_water_field_leases.bin` — extract `FIELD_NAME_CODE` → `FIELD_NAME` mapping
2. Loads platform structure data — extract additional `FIELD_NAME_CODE` → name mappings
3. Loads `data/modules/bsee/bin/lab/mv_lease_area_block.bin` — lease → area/block mapping
4. Provides `resolve(field_code: str) -> str` returning display name or code as fallback

**Key functions**:
```python
class FieldNameResolver:
    def __init__(self, data_dir: Path)
    def load_field_names(self) -> Dict[str, str]  # code -> display name
    def resolve(self, field_code: str) -> str
    def resolve_batch(self, field_codes: List[str]) -> Dict[str, str]
```

### Step 2: Geological Era Classifier (extend existing module)

**File**: `src/worldenergydata/bsee/paleowells/era_classifier.py`

Extend `PaleowellsDataProcessor` to provide era classification for any well:
1. Load `Paleowells.csv` (16K+ rows with `API Well Number` → `Paleo Age`)
2. Parse `Paleo Age` string to extract era (Paleocene, Eocene, Oligocene, Miocene, Pliocene, Pleistocene)
3. Map wells to fields via API number → field code join
4. Classify each field's dominant era (most wells, or deepest penetration)

**Key functions**:
```python
class GeologicalEraClassifier:
    ERAS = ["Paleocene", "Eocene", "Oligocene", "Miocene", "Pliocene", "Pleistocene"]

    def __init__(self, paleowells_csv: Path)
    def classify_well(self, api_well_number: str) -> Optional[str]
    def classify_field(self, field_wells: List[str]) -> str  # dominant era
    def get_era_summary(self) -> Dict[str, int]  # era -> well count
```

### Step 3: All-Fields Production Runner (new module)

**File**: `src/worldenergydata/bsee/analysis/all_fields_runner.py`

Orchestrator that:
1. Loads all BSEE production data (OGOR historical yearly files)
2. Groups production by field code
3. For each field: compute cumulative oil/gas/water, peak rate, active years, well count
4. Joins with FieldNameResolver for display names
5. Joins with GeologicalEraClassifier for era labels
6. For Tier 2 fields (lower tertiary with configs): also runs the financial pipeline
7. Outputs a unified DataFrame with all fields

**Key functions**:
```python
class AllFieldsRunner:
    def __init__(self, field_resolver: FieldNameResolver, era_classifier: GeologicalEraClassifier)
    def run(self, production_data: pd.DataFrame, well_data: pd.DataFrame) -> pd.DataFrame
    def _compute_field_production(self, field_code: str, field_df: pd.DataFrame) -> Dict
    def _run_financial_tier(self, field_code: str) -> Optional[Dict]
```

**Output DataFrame columns**:
```
FIELD_CODE | FIELD_NAME | GEOLOGICAL_ERA | AREA_CODE | WATER_DEPTH_AVG |
WELL_COUNT | ACTIVE_WELLS | FIRST_PRODUCTION | LAST_PRODUCTION |
CUM_OIL_MMBBL | CUM_GAS_BCF | CUM_WATER_MMBBL | PEAK_OIL_BOPD |
NPV10_MM_USD | IRR_PCT | PAYBACK_YRS  (Tier 2 only, null for Tier 1)
```

### Step 4: Report Generator

**File**: `src/worldenergydata/bsee/reports/all_fields_report.py`

Generate structured report:
1. **Executive summary**: total fields, total production, era distribution
2. **By geological era**: table grouped by era, sorted by cumulative production
3. **By field**: sortable table with all metrics
4. **Tier 2 financial summary**: lower tertiary fields with NPV/IRR/payback
5. **Output formats**: Markdown report + CSV export + HTML interactive (Plotly)

**Output files**:
- `reports/bsee/all_fields_analysis.md` — structured markdown report
- `results/bsee/all_fields_summary.csv` — machine-readable data
- `results/bsee/all_fields_dashboard.html` — interactive Plotly dashboard

### Step 5: Configuration

**File**: `config/analysis/all_fields/analysis_config.yml`

Minimal config for the all-fields runner:
```yaml
analysis_scope:
  tier_1: all  # all fields get production analysis
  tier_2:      # these fields get full financial analysis
    config_dir: config/analysis/lower_tertiary/fields/
    fields: [anchor, cascade_chinook, jack_st_malo, julia, shenandoah, stones, big_foot]
data_sources:
  production: data/modules/bsee/bin/historical_production_yearly/
  paleowells: data/modules/bsee/paleowells/Paleowells.csv
  field_leases: data/modules/bsee/bin/deepqual/mv_deep_water_field_leases.bin
  platform_structures: data/modules/bsee/bin/platstruc/mv_platstruc_structures.bin
  lease_area_block: data/modules/bsee/bin/lab/mv_lease_area_block.bin
```

### Step 6: Tests (TDD)

**Files**:
- `tests/unit/bsee/test_field_names.py` — FieldNameResolver unit tests
- `tests/unit/bsee/test_era_classifier.py` — GeologicalEraClassifier unit tests
- `tests/unit/bsee/test_all_fields_runner.py` — AllFieldsRunner unit tests
- `tests/unit/bsee/test_all_fields_report.py` — Report generator tests

**Key test cases**:
- Field resolver: known deep water fields resolve correctly, unknown codes return code as fallback
- Era classifier: wells with Paleocene/Eocene ages classified correctly, wells without paleo data return None
- Runner: handles empty production data, single-field, multi-field; Tier 2 fields get financial columns
- Report: markdown renders correctly, CSV has expected columns, era grouping sorts properly

## Critical Files

### Existing (read/reuse)
| File | Purpose |
|------|---------|
| `src/worldenergydata/bsee/bsee.py` | Main router — extend to support all-fields mode |
| `src/worldenergydata/bsee/analysis/bsee_analysis.py` | Analysis orchestrator |
| `src/worldenergydata/bsee/paleowells/data_processor.py` | Paleowells processor with era extraction regex |
| `src/worldenergydata/bsee/analysis/financial/` | Tier 2 financial pipeline (reuse as-is) |
| `src/worldenergydata/bsee/data/bsee_data.py` | Data loading layer |
| `config/analysis/lower_tertiary/fields/*.yml` | 7 field configs for Tier 2 |
| `data/modules/bsee/paleowells/Paleowells.csv` | 16K+ rows of geological well data |
| `data/modules/bsee/bin/deepqual/mv_deep_water_field_leases.bin` | Field name mapping source |
| `data/modules/bsee/bin/historical_production_yearly/` | OGOR production data |

### New (create)
| File | Purpose |
|------|---------|
| `src/worldenergydata/bsee/data/field_names.py` | Field nickname resolver |
| `src/worldenergydata/bsee/paleowells/era_classifier.py` | Geological era classifier |
| `src/worldenergydata/bsee/analysis/all_fields_runner.py` | All-fields orchestrator |
| `src/worldenergydata/bsee/reports/all_fields_report.py` | Report generator |
| `config/analysis/all_fields/analysis_config.yml` | Runner configuration |
| `tests/unit/bsee/test_field_names.py` | Field resolver tests |
| `tests/unit/bsee/test_era_classifier.py` | Era classifier tests |
| `tests/unit/bsee/test_all_fields_runner.py` | Runner tests |
| `tests/unit/bsee/test_all_fields_report.py` | Report tests |

## Verification

1. **Unit tests**: `PYTHONPATH="src:../assetutilities/src" python3 -m pytest tests/unit/bsee/test_field_names.py tests/unit/bsee/test_era_classifier.py tests/unit/bsee/test_all_fields_runner.py -v --tb=short --noconftest`
2. **Field name resolution**: Load deepwater field leases bin, verify known fields (Thunder Horse, Mars, etc.) resolve
3. **Era classification**: Load Paleowells.csv, verify era extraction matches known wells
4. **Production totals**: Cross-check a few known fields against WRK-010 lower tertiary results
5. **Report output**: Verify markdown report has era grouping, CSV has expected columns, HTML renders

## Risks

| Risk | Mitigation |
|------|------------|
| Binary .bin files may need deserialization logic | Check existing loaders in `data/loaders/` for patterns |
| Paleowells.csv may not cover all fields | Fields without paleo data get "Unknown" era — document in report |
| Production data volume (29 yearly files) may be slow | Process in chunks, cache intermediate results |
| Field code mapping may be incomplete | Fallback to raw code; document unmapped fields |
