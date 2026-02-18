---
title: "World Oil Lower Tertiary Articles — Interactive HTML Reports"
description: "Generate three interactive HTML reports with Plotly charts synthesizing insights from the two-part World Oil article series on Lower Tertiary performance, using live BSEE WAR data and legacy production CSVs"
version: "0.3.0"
module: bsee/analysis/lower_tertiary
session:
  id: eager-petting-bonbon
  agent: claude-opus-4.6
  date: 2026-02-09
status: ready — WRK-116 parallel work complete, proceeding with implementation
review:
  cross_review: completed
  iterations: 2
  reviewers: [code-reviewer, tech-architect, domain-expert]
  verdict: APPROVE WITH CHANGES (all changes incorporated below)
work_items: [WRK-024]
target_repo: worldenergydata
resume_notes: |
  Plan v0.3 is complete and cross-reviewed. Ready for implementation.
  Key change in v0.3: YAML-driven architecture (config/input/world_oil_lower_tertiary.yaml).
  Waiting for parallel comprehensive BSEE analysis to complete before starting.
  Implementation order: YAML file → config.py → tests → war_extractor → legacy_loader → analyzer → reports → runner.
---

# World Oil Lower Tertiary Articles — Interactive HTML Reports (v0.3)

## Context

Two World Oil articles by Frontier Deepwater analyze 20 years of Lower Tertiary (LT) Wilcox play performance using BSEE public data:

- **Part 1** (2025-10): "America's Promising Lower Tertiary Frontier — Two Decades Later" — BSEE data showing subsea developments recover only 2–10% STOIIP vs 30–40% for dry-tree; mean subsea NPV is –$1.2B at 10% discount.
- **Part 2** (2026-01): "Enhancing Industry Performance — The Options" — Architecture comparison (Spar, TLP, Semi/DDS, FrPS) showing system architecture, not geology, governs recovery.

**Objective**: Three interactive HTML reports with Plotly charts providing visual insights into the articles' concepts, backed by live BSEE WAR data and legacy production CSVs. **All analysis driven by a YAML input file** for easy reference and modification.

## YAML-Driven Architecture (v0.3 change)

All field definitions, article-derived metrics, architecture ratings, and data paths are specified in a single YAML input file. Python code reads this file at runtime — no hardcoded data dicts.

**YAML file**: `config/input/world_oil_lower_tertiary.yaml`

Follows the established `config/input/` pattern (see `lower_tertiary.yaml`, `bsee_all_wells.yaml`).

### YAML Structure

```yaml
# config/input/world_oil_lower_tertiary.yaml
metadata:
  feature_name: "world-oil-lower-tertiary-reports"
  version: "1.0.0"
  description: "World Oil LT article analysis — field mappings, article metrics, report config"
  articles:
    part1:
      title: "America's Promising Lower Tertiary Frontier — Two Decades Later"
      publication: "World Oil"
      date: "2025-10"
      author: "Frontier Deepwater"
    part2:
      title: "Enhancing Industry Performance — The Options"
      publication: "World Oil"
      date: "2026-01"
      author: "Frontier Deepwater"

# ── Field Block Mappings ──────────────────────────────────────────────
fields:
  subsea:
    Jack:
      area: WR
      blocks: [718, 719, 758, 759]
      operator: "Chevron"
      first_oil: 2014
    "St. Malo":
      area: WR
      blocks: [633, 634, 677, 678]
      operator: "Chevron"
      first_oil: 2014
    Julia:
      area: WR
      blocks: [540, 584, 627]
      operator: "ExxonMobil"
      first_oil: 2016
    Stones:
      area: WR
      blocks: [508]
      operator: "Shell"
      first_oil: 2016
    "Cascade/Chinook":
      area: WR
      blocks: [205, 206, 469, 470]
      operator: "Petrobras"
      first_oil: 2012
    Anchor:
      area: GC
      blocks: [807]
      operator: "Chevron"
      first_oil: 2024
    Shenandoah:
      area: WR
      blocks: [51, 52, 53]
      operator: "Beacon Offshore"
      first_oil: null  # Under development
    Kaskida:
      area: KC
      blocks: [291, 292]
      operator: "BP"
      first_oil: null
    Tiber:
      area: KC
      blocks: [102]
      operator: "BP"
      first_oil: null

  dry_tree:
    Mars:
      area: MC
      blocks: [687, 727, 763, 807]
      operator: "Shell"
      first_oil: 1996
      platform: "TLP"
    Ursa:
      area: MC
      blocks: [809, 810, 854]
      operator: "Shell"
      first_oil: 1999
      platform: "TLP"
    "Mad Dog":
      area: GC
      blocks: [782, 826]
      operator: "BP"
      first_oil: 2005
      platform: "Spar"
    "Horn Mountain":
      area: MC
      blocks: [126, 127]
      operator: "BP"
      first_oil: 2002
      platform: "Spar"

# ── Article-Derived Metrics ───────────────────────────────────────────
# Source: Frontier Deepwater analysis of BSEE data (2025)
article_metrics:
  source_attribution: "Frontier Deepwater analysis of BSEE data (2025)"
  aggregate:
    total_investment_billion: 50
    total_modu_days: 20000
    total_dc_cost_billion: 20
    subsea_uptime_pct: 67
    zones_perforated_pct_range: [25, 30]
    intervention_cost_per_well_million: 100

  recovery_factors:
    subsea:
      range_pct: [2, 10]
      label: "Subsea tieback"
    dry_tree:
      range_pct: [30, 40]
      label: "Dry-tree (Spar/TLP)"

  economics:
    mean_subsea_npv_billion: -1.2
    discount_rate: 0.10

  julia_deep_dive:
    oip_billion_bbl: 6
    sanctioned_billion_bbl: 1
    actual_recovery_mmbbl: 71
    legacy_csv_mmbbl: 68.4

  validation_table:
    # Extractable from article Section 3.1
    fields:
      - name: "Jack/St. Malo"
        appraisal_wells: 7
        discovery_to_fo_years: 11
        recovery_factor_pct: 2.5
      - name: "Julia"
        appraisal_wells: 4
        discovery_to_fo_years: 9
        recovery_factor_pct: 1.2
      - name: "Stones"
        appraisal_wells: 3
        discovery_to_fo_years: 12
        recovery_factor_pct: 3.1
      - name: "Cascade/Chinook"
        appraisal_wells: 5
        discovery_to_fo_years: 8
        recovery_factor_pct: 2.0

# ── Architecture Ratings (Part 2) ────────────────────────────────────
# Qualitative heatmap: 5 systems × 6 criteria, scale 1–5
architecture:
  systems: ["Subsea Tieback", "Spar", "TLP", "Semi/DDS", "FrPS"]
  criteria: ["Intervention Access", "Recovery Potential", "Water Depth Range",
             "CAPEX Efficiency", "Operational Uptime", "Well Count Capacity"]
  ratings:
    "Subsea Tieback": [1, 2, 5, 4, 3, 2]
    "Spar":           [4, 4, 4, 3, 4, 3]
    "TLP":            [5, 5, 2, 3, 5, 5]
    "Semi/DDS":       [5, 5, 5, 2, 4, 5]
    "FrPS":           [4, 4, 5, 4, 4, 4]

  depth_limits_ft:
    "Subsea Tieback": {min: 0, max: 12000}
    "Spar":           {min: 2000, max: 8000}
    "TLP":            {min: 1000, max: 6000}
    "Semi/DDS":       {min: 3000, max: 10000}
    "FrPS":           {min: 3000, max: 10000}

  pros_cons:
    "Subsea Tieback":
      pros: ["Lower CAPEX", "Ultra-deepwater capable", "Modular expansion"]
      cons: ["No intervention access", "Low recovery 2–10%", "High workover cost $100M+"]
    "Spar":
      pros: ["Dry-tree wells", "Good motion characteristics", "Proven to 8000ft"]
      cons: ["Higher CAPEX", "Limited to ~8000ft water depth"]
    "TLP":
      pros: ["Full dry-tree access", "Highest recovery 30–40%", "Best intervention"]
      cons: ["Depth limited to ~5–6000ft", "Tendon fatigue in ultra-deep"]
    "Semi/DDS":
      pros: ["Deepwater capable", "Dry-tree access", "High well count"]
      cons: ["Highest CAPEX", "Complex risers", "New technology risk"]
    "FrPS":
      pros: ["Floating production flexibility", "Deepwater capable", "Redeployable"]
      cons: ["No dry-tree", "Riser complexity", "Turret challenges"]

# ── Data Paths ────────────────────────────────────────────────────────
data:
  war_zip: "data/modules/bsee/.local/war/eWellWARRawData.zip"
  legacy_results_dir: "tests/modules/bsee/analysis/legacy/results"
  legacy_fields:
    julia:
      rate: "prod_rate_bopd_goa_julia.csv"
      cumulative: "prod_cumulative_mmbbl_goa_julia.csv"
      prod_summary: "prod_summ_goa_julia.csv"
      well_summary: "well_summ_goa_julia.csv"
    stmalo:
      rate: "prod_rate_bopd_goa_stmalo.csv"
      cumulative: "prod_cumulative_mmbbl_goa_stmalo.csv"
      prod_summary: "prod_summ_goa_stmalo.csv"
      well_summary: "well_summ_goa_stmalo.csv"
    stones:
      rate: "prod_rate_bopd_goa_stones.csv"
      cumulative: "prod_cumulative_mmbbl_goa_stones.csv"
      prod_summary: "prod_summ_goa_stones.csv"
      well_summary: "well_summ_goa_stones.csv"

# ── Report Output Configuration ──────────────────────────────────────
output:
  visualization:
    library: plotly
    interactive: true
    theme: plotly_white
  reports:
    part1:
      filename: "lt_performance_report.html"
      title: "Lower Tertiary Performance Analysis"
      output_dir: "frontierdeepwater/Mktg/World Oil/2025-10"
    part2:
      filename: "lt_options_report.html"
      title: "Architecture Options Analysis"
      output_dir: "frontierdeepwater/Mktg/World Oil/2026-01"
    executive:
      filename: "lt_executive_summary.html"
      title: "Lower Tertiary Executive Summary"
      output_dir: "frontierdeepwater/Mktg/World Oil"
  copy_to: "reports/bsee/lower_tertiary"

execution:
  entry_point: "scripts/bsee/generate_world_oil_reports.py"
  bash_command: |
    PYTHONPATH=src /usr/bin/python3 scripts/bsee/generate_world_oil_reports.py \
      --config config/input/world_oil_lower_tertiary.yaml \
      --report all
```

## Data Availability & Limitations

| Source | Status | Content |
|--------|--------|---------|
| WAR zip (`.local/war/eWellWARRawData.zip`) | Available | 363,588 records, 1988–2026 |
| Legacy CSVs (`tests/.../legacy/results/`) | Available | Julia, St. Malo, Stones: rate, cumulative, well/prod summary |
| Production .bin files | LFS stubs | NOT available locally |
| Article tables (2.1, 2.2, 3.2.1) | Embedded images in .docx | Only partially reconstructable from text |

**Key constraints**: Tables 2.1/2.2 are images; financial figures must be attributed; only 3 of 12 fields have production CSVs; Part 2 architecture data is qualitative (heatmap, not radar).

**Strategy**: WAR data for drilling/activity analysis. Legacy CSVs for subsea production curves. Article-derived metrics in YAML with source attribution.

## Deliverables — Three Reports

### Report 1: Part 1 — LT Performance Analysis
**File**: `frontierdeepwater/Mktg/World Oil/2025-10/lt_performance_report.html`

| # | Section | Data Source | Chart Type |
|---|---------|-------------|------------|
| 1 | Executive Summary | YAML `article_metrics.aggregate` | Stat cards |
| 2 | Validation Metrics | YAML `article_metrics.validation_table` | Comparison table |
| 3 | Recovery Factor Comparison | YAML `article_metrics.recovery_factors` | Grouped bar |
| 4 | Julia Deep-Dive | YAML `article_metrics.julia_deep_dive` + legacy CSV | Bar + annotation |
| 5 | WAR Drilling Activity by Field | Live WAR data | Stacked bar (field × year) |
| 6 | Rig Utilization | Live WAR data | Horizontal bar (rig × field) |
| 7 | Subsea Production Curves | Legacy CSVs via YAML `data.legacy_fields` | Line chart (BOPD) |
| 8 | Cumulative Production | Legacy CSVs | Line chart (MMBBL) |
| 9 | Well Summary | Legacy CSVs (prod_summ + well_summ) | Table |
| 10 | Methodology & Attribution | YAML `article_metrics.source_attribution` | Text section |

### Report 2: Part 2 — Architecture Options
**File**: `frontierdeepwater/Mktg/World Oil/2026-01/lt_options_report.html`

| # | Section | Data Source | Chart Type |
|---|---------|-------------|------------|
| 1 | Executive Summary | YAML `metadata.articles.part2` | Stat cards |
| 2 | Architecture Comparison | YAML `architecture.ratings` | Heatmap |
| 3 | Water Depth Feasibility | YAML `architecture.depth_limits_ft` | Horizontal bar |
| 4 | Recovery by Architecture | YAML `article_metrics.recovery_factors` | Grouped bar |
| 5 | Intervention Cost | YAML `article_metrics.aggregate` | Bar |
| 6 | Subsea vs Dry-Tree WAR | Live WAR data grouped by YAML `fields.subsea/dry_tree` | Grouped bar |
| 7 | Architecture Pros/Cons | YAML `architecture.pros_cons` | Styled table |
| 8 | Conclusions | Article text | Highlight box |

### Report 3: Executive Summary
**File**: `frontierdeepwater/Mktg/World Oil/lt_executive_summary.html`

| # | Section | Data Source | Chart Type |
|---|---------|-------------|------------|
| 1 | Two-Decade Scorecard | YAML `article_metrics.aggregate` | Stat cards |
| 2 | The Performance Gap | YAML `article_metrics.recovery_factors` | Side-by-side bars |
| 3 | Live WAR Data Snapshot | Live WAR data per YAML field defs | Summary table |
| 4 | Investment Implications | YAML `article_metrics.economics` | Annotated bar |
| 5 | Path Forward | Article text | Highlight boxes |

## Implementation Plan

### File Structure

```
config/input/
└── world_oil_lower_tertiary.yaml   # ★ Single source of truth for all analysis inputs

src/worldenergydata/bsee/analysis/lower_tertiary/
├── __init__.py
├── config.py            # Load & validate YAML → typed dataclass/dict
├── war_extractor.py     # Extract WAR data for all fields defined in YAML
├── legacy_loader.py     # Load legacy CSVs (paths from YAML, wide→long transform)
├── analyzer.py          # Intermediate analysis layer (aggregation, pivots)
├── report_part1.py      # Part 1 HTML report generator
├── report_part2.py      # Part 2 HTML report generator
├── report_executive.py  # Executive summary report generator

scripts/bsee/
└── generate_world_oil_reports.py   # CLI runner (--config, --report, --output-dir)

tests/modules/bsee/analysis/lower_tertiary/
├── __init__.py
├── test_config.py          # YAML loading, validation, field iteration
├── test_war_extractor.py
├── test_legacy_loader.py
└── test_reports.py
```

### Phase 1: YAML Input File (`config/input/world_oil_lower_tertiary.yaml`)

Create the YAML file with all content shown in the YAML Structure section above. This is the single source of truth — field block mappings, article metrics, architecture ratings, data paths, and output configuration.

### Phase 2: Config Loader (`config.py`)

Replaces the old `fields.py`. Thin loader that reads the YAML and provides convenient accessors:

```python
class LTConfig:
    def __init__(self, config_path: Path):
        with open(config_path) as f:
            self._cfg = yaml.safe_load(f)

    @property
    def all_fields(self) -> dict[str, dict]:
        """Merge subsea + dry_tree fields from YAML."""

    @property
    def subsea_fields(self) -> dict[str, dict]:
        return self._cfg["fields"]["subsea"]

    @property
    def dry_tree_fields(self) -> dict[str, dict]:
        return self._cfg["fields"]["dry_tree"]

    @property
    def article_metrics(self) -> dict:
        return self._cfg["article_metrics"]

    @property
    def architecture(self) -> dict:
        return self._cfg["architecture"]

    @property
    def data_paths(self) -> dict:
        return self._cfg["data"]

    @property
    def output_config(self) -> dict:
        return self._cfg["output"]

    def field_blocks(self, name: str) -> tuple[str, list[int]]:
        """Return (area_code, block_list) for a named field."""

    def legacy_csv_paths(self, field: str, base_dir: Path) -> dict[str, Path]:
        """Return resolved paths for a legacy field's CSVs."""
```

### Phase 3: WAR Extractor (`war_extractor.py`)

Accepts `LTConfig` — reads field definitions from YAML, not hardcoded dicts:

```python
class LTWarExtractor:
    def __init__(self, war_zip_path: Path, config: LTConfig):
        self._df = load_war_from_zip(war_zip_path)  # reuse from buckskin
        self._config = config
        self._strip_strings()

    def extract_field(self, field_name: str) -> pd.DataFrame:
        area, blocks = self._config.field_blocks(field_name)
        # Filter using area + block set (int + str forms)

    def extract_all_fields(self) -> dict[str, pd.DataFrame]:
    def drilling_activity_by_year(self) -> pd.DataFrame:
    def rig_utilization(self) -> pd.DataFrame:
    def subsea_vs_drytree_activity(self) -> dict[str, pd.DataFrame]:
```

### Phase 4: Legacy Production Loader (`legacy_loader.py`)

Reads CSV file names from YAML `data.legacy_fields` section:

```python
class LegacyProductionLoader:
    def __init__(self, config: LTConfig, root_dir: Path):
        self._config = config
        self._root = root_dir

    def load_production_rate(self, field: str) -> pd.DataFrame:
        paths = self._config.legacy_csv_paths(field, self._root)
        # Load + melt wide CSV → long format

    def load_cumulative(self, field: str) -> pd.DataFrame:
    def load_well_summary(self, field: str) -> pd.DataFrame:
    def load_production_summary(self, field: str) -> pd.DataFrame:
    def available_fields(self) -> list[str]:
    def field_total_rate(self, field: str) -> pd.DataFrame:
```

### Phase 5: Analyzer (`analyzer.py`)

```python
class LTAnalyzer:
    def __init__(self, config: LTConfig, war: LTWarExtractor,
                 legacy: LegacyProductionLoader):
        self._config = config
        # Article metrics read from config.article_metrics
        # Architecture data from config.architecture

    def war_summary_table(self) -> pd.DataFrame:
    def subsea_vs_drytree_comparison(self) -> dict:
    def production_comparison(self) -> dict[str, pd.DataFrame]:
    def well_inventory(self) -> pd.DataFrame:
```

### Phase 6: Report Generators

Follow `buckskin/report.py` pattern. All article-derived content read from `config.article_metrics` and `config.architecture`. Use `fig.to_html(include_plotlyjs=(idx==0))` for Plotly embedding.

Charts (Plotly):
- **Grouped bar**: recovery factors, costs by system type
- **Line**: production rate curves (BOPD), cumulative (MMBBL)
- **Stacked bar**: WAR records by field × year
- **Horizontal bar**: rig utilization, water depth limits
- **Heatmap**: architecture comparison (5 × 6 matrix from YAML)
- **Annotated bar**: Julia deep-dive (OIP vs sanctioned vs actual from YAML)

### Phase 7: Runner Script

```bash
PYTHONPATH=src /usr/bin/python3 scripts/bsee/generate_world_oil_reports.py \
  --config config/input/world_oil_lower_tertiary.yaml --report all
```

Options:
- `--config PATH` — YAML input file (required)
- `--report part1|part2|executive|all`
- `--output-dir PATH` (overrides YAML `output.reports.*.output_dir`)

### Phase 8: Tests (TDD)

- `test_config.py`: YAML loads successfully, all 13 fields present, block mappings correct, article metrics accessible, architecture ratings have correct dimensions
- `test_war_extractor.py`: Real WAR data (Tiber: 38 records) filtered by YAML field config
- `test_legacy_loader.py`: Wide→long melt, field_total_rate, paths from YAML
- `test_reports.py`: Integration — each report generates without error, contains expected headings

## Reuse From Existing Codebase

| Component | Source | Reuse Pattern |
|-----------|--------|---------------|
| WAR zip loading | `buckskin/extractor.py:load_war_from_zip()` | Import directly |
| String stripping | `buckskin/extractor.py:_strip_strings()` | Copy pattern |
| HTML/CSS template | `buckskin/report.py:_CSS`, `_card()` | Import or copy |
| Plotly→HTML | `intervention/dashboard.py:_fhtml()` | Adopt pattern |
| YAML loading | `config_router.py:yaml.safe_load()` | Same pattern |
| Config input pattern | `config/input/lower_tertiary.yaml` | Follow structure |
| API normalizer | `data/utils/api_well_normalizer.py` | Import for WAR joins (WRK-116) |
| Enrichment engine | `intervention/enrichment_engine.py` | Reference pattern for WAR→borehole joins (WRK-116) |
| Dashboard patterns | `intervention/dashboard.py` | Reuse `_fhtml()`, `_tbl()`, CSS (WRK-116) |

## Verification

1. **Tests**: `PYTHONPATH=src /usr/bin/python3 -m pytest tests/modules/bsee/analysis/lower_tertiary/ -v --override-ini="addopts=-v --tb=short" -W "default::pytest.PytestRemovedIn9Warning"`
2. **Generate**: `PYTHONPATH=src /usr/bin/python3 scripts/bsee/generate_world_oil_reports.py --config config/input/world_oil_lower_tertiary.yaml --report all`
3. **Validate**: 3 HTML files open with interactive Plotly charts; WAR data populates across fields; legacy production curves render for Julia, St. Malo, Stones
4. **YAML reference**: Open `config/input/world_oil_lower_tertiary.yaml` to verify all field definitions, article metrics, and architecture ratings are easily readable

## Review Resolution Log

| Finding | Reviewer | Resolution |
|---------|----------|------------|
| Missing analyzer layer | Code | Added `analyzer.py` (Phase 5) |
| Legacy CSV wide format | Code | Loader does wide→long melt |
| No report tests | Code | Added `test_reports.py` integration tests |
| Kaskida area code wrong (GC→KC) | Tech | Corrected in YAML field mapping |
| Shenandoah missing block 51 | Tech | Added to YAML mapping |
| Cascade/Chinook wrong blocks | Tech | Corrected in YAML |
| Julia missing block 540 | Tech | Added to YAML mapping |
| Jack/St. Malo should be split | Code+Tech | Split in YAML |
| Tables 2.1/2.2 not reconstructable | Domain | Scoped to extractable text in YAML |
| Radar chart needs numeric data | Domain | Changed to qualitative heatmap |
| Financial data attribution | Domain | `source_attribution` in YAML |
| Cross-repo output risk | Tech | `--output-dir` + copies to worldenergydata |
| No mocks per testing rules | Code | Tests use real WAR data |
| **Analysis must be YAML-driven** | **User** | **All data in `config/input/world_oil_lower_tertiary.yaml`; `fields.py` → `config.py` loader** |
