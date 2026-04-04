# World Energy Data - Memory

## Environment
- venv at `.venv/` has broken python symlink (python3.11 not installed)
- Use `/usr/bin/python3` (3.12.3) with `PYTHONPATH=src` for running tests
- `assetutilities` was manually installed via `pip3 install --user --break-system-packages`
- pytest requires: `--override-ini="addopts=-v --tb=short" -W "default::pytest.PytestRemovedIn9Warning"` to avoid conftest deprecation error

## Test Running
```bash
PYTHONPATH=src /usr/bin/python3 -m pytest tests/modules/bsee/data/loaders/rig_fleet/ -v --override-ini="addopts=-v --tb=short" -W "default::pytest.PytestRemovedIn9Warning"
```

## Pre-existing Test Failures
- `tests/cli/` - missing `typer` module
- `tests/modules/bsee/analysis/directional_surveys/` - 19 failures (unrelated to rig fleet)
- `tests/modules/bsee/analysis/api12_drilling_completion_analysis/` - 5 failures
- Multiple other modules: missing `sqlalchemy`, `scipy`, etc.

## Rig Fleet Module Structure
- Constants: `src/.../loaders/rig_fleet/constants.py` (RigType, RigStatus, DataSource, classify_rig_type)
- Loader: `src/.../loaders/rig_fleet/rig_fleet_loader.py` (build_fleet_from_war, load_overrides)
- WAR Acquirer: `src/.../loaders/rig_fleet/war_acquirer.py` (WARDataAcquirer with DI + caching)
- Schema: `src/.../schemas/rig_fleet.py` (Pydantic)
- Model: `src/.../models/rig_fleet.py` (dataclass with properties)
- Build Script: `scripts/build_rig_fleet_from_war.py` (--source download/local, --dry-run)

## Key Patterns
- Loader checks `.local/` first, falls back to `bin/` for sample data
- WAR acquirer caches zip to `data/modules/bsee/.local/war/` with 30-day freshness
- Build script outputs to `.local/rig_fleet/` (gitignored)
- Override CSV at `data/modules/bsee/bin/rig_fleet/rig_type_overrides.csv`

## World Oil Lower Tertiary Reports (WRK-024) — COMPLETED
- **Plan file**: `specs/modules/eager-petting-bonbon.md`
- **Tests**: 124 pass in `tests/modules/bsee/analysis/lower_tertiary/`
- **Key design**: YAML-driven at `config/input/world_oil_lower_tertiary.yaml`
- **Modules** (all in `src/.../bsee/analysis/lower_tertiary/`):
  - `config.py` — LTConfig YAML loader
  - `war_extractor.py` — LTWarExtractor (field filtering from config)
  - `legacy_loader.py` — LegacyProductionLoader (wide→long CSV melt)
  - `analyzer.py` — LTAnalyzer (WAR + legacy + YAML metrics)
  - `report_part1.py` — Part 1 Performance Analysis (10 sections)
  - `report_part2.py` — Part 2 Architecture Options (8 sections)
  - `report_executive.py` — Executive Summary (5 sections)
- **Runner**: `scripts/bsee/generate_world_oil_reports.py` (--config, --report, --output-dir)
- **Output**: 3 HTML reports (4.7-4.8MB each) + copies to `reports/bsee/lower_tertiary/`

## Buckskin Analysis Module (COMPLETED)
- Location: `src/.../bsee/analysis/buckskin/` (extractor, analyzer, report)
- Script: `scripts/bsee/analyze_buckskin.py`
- Tests: 27 pass in `tests/modules/bsee/analysis/buckskin/`
- Key reusable: `load_war_from_zip()` in extractor.py

## WRK-116: Comprehensive GOM Activity Analysis (COMPLETED)
- **Plan**: `specs/modules/expressive-marinating-dolphin.md`
- **Session**: expressive-marinating-dolphin
- **Pipeline**: DATA → ENRICHMENT → ANALYSIS → INSIGHTS → REPORTS
- **Tests**: 161 pass in `tests/modules/bsee/analysis/intervention/`
- **Phases**: 0 (shared infra) → 1 (borehole) → 2 (enrichment) → 3 (analyzer) → 4 (insights) → 5 (reports) → 6 (well design) → 7 (visualization)
- **Key modules** (all in `src/.../bsee/analysis/intervention/`):
  - `enrichment_engine.py` — joins WAR+Fleet+Borehole+Paleowells
  - `comprehensive_analyzer.py` — 7 analysis modules
  - `insight_generator.py` — 5 insight categories + `_filter_valid_years()` helper
  - `well_design_analyzer.py` — casing/completion/geology/BOP
  - `field_visualization.py` — Plotly maps, 3D views, SVG schematics
  - `drilling_report.py` — enhanced with `from_enriched()` classmethod
  - `dashboard.py` — updated with optional `insights` param
- **Shared utils**: `src/.../data/utils/api_well_normalizer.py`
- **Data acquirer**: `src/.../data/loaders/well/borehole_acquirer.py` (caches to `.local/borehole/`)
- **Build scripts**: `scripts/build_enhanced_reports.py`, `scripts/build_field_visualization.py`, `scripts/build_borehole_data.py`
- **Data facts**: WAR=2M rows (8 files merged), mv_war_main=363K, Borehole=57K wells, Paleowells=458 wells with era
- **Real data results**: fleet=12%, borehole=20%, era≈0% (458/2M), 5 findings, 2 trends, 1 risk
- **Gotcha**: WAR zip `mv_war_boreholes_view.txt` introduces BH_TOTAL_MD/WELL_SPUD_DATE/TOTAL_DEPTH_DATE columns into merged WAR DataFrame — enrichment engine drops these before borehole join to avoid pandas `_x`/`_y` suffix collision
- **Gotcha**: Comprehensive analyzer groups YEAR as string → "nan" rows; insight generator must filter with `_filter_valid_years()` before int conversion

## Hull Library (digitalmodel repo)
- Location: `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/`
- Tests: `digitalmodel/tests/hydrodynamics/hull_library/` (65 tests, all pass)
- Seed data: `digitalmodel/data/hull_library/profiles/` (unit_box, generic_barge, generic_tanker)
- Run tests: `cd digitalmodel && uv run python -m pytest tests/hydrodynamics/hull_library/ -v --tb=short`
- Note: digitalmodel `.venv` has broken symlink; `uv run` uses `-c /dev/null` workaround
- Modules: profile_schema, mesh_generator (+ adaptive + coarsen_mesh), schematic_generator, catalog
- WRK-106/107/108 implemented; WRK-101 mesh coarsening addressed via `coarsen_mesh()` + `adaptive_density`
