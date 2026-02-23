# WRK-129 Phase 1 Implementation Plan

## Context

The `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/` package already exists with full
Phase 1+2+3 implementation (models, css.py, section_builders, renderers, report_generator.py).
32 tests exist and pass. **The gap is coverage: 70.35% vs 80% required** by the project's coverage
gate (`pyproject.toml: fail_under = 80.0`). The spec also requires a `test_mesh_quality.py` file.

## Current State

| Component | Files | Tests | Coverage |
|-----------|-------|-------|----------|
| Models | ✅ all 12 + report.py | ✅ test_models.py | ✅ 94–100% |
| css.py | ✅ | — | ✅ 100% |
| section_builders | ✅ all 17 | ⚠️ partial | 0–100% |
| renderers | ✅ all 5 | ⚠️ partial | 72–95% |
| report_generator.py | ✅ | ⚠️ partial | 83% |
| **Overall** | | 32 tests | **70.35%** |

## Low-coverage files (target to fix):

| File | Current | Gap |
|------|---------|-----|
| `section_builders/other_structures.py` | 0% | add `_build_other_structures_html` with data test |
| `section_builders/boundary_conditions.py` | 12.5% | add test with BCData populated |
| `section_builders/materials.py` | 12.5% | add test with MaterialData populated |
| `section_builders/results_dynamic.py` | 27.3% | add test with DynamicResultsData |
| `section_builders/results_extreme.py` | 33.3% | add test with ExtremeResultsData |
| `section_builders/results_static.py` | 55.1% | add test with StaticResultsData |
| `section_builders/loads.py` | 60.6% | add test with EnvironmentData |
| `section_builders/fatigue.py` | 60.9% | add test with FatigueResultsData |
| `renderers/riser.py` | 72.1% | add report-level riser test |
| `renderers/pipeline.py` | 74.4% | add report-level pipeline test |
| `report_generator.py` | 83.3% | add offline mode + invalid structure_type |

## Plan

### Step 1: Add `test_mesh_quality.py` (spec required, currently missing)

File: `tests/solvers/orcaflex/reporting/test_mesh_quality.py`

Tests:
- Segment adjacency ratio calculation correctness
- `MeshQualityData.verdict = "PASS"` for ratio < 3.0
- `MeshQualityData.verdict = "WARNING"` for ratio >= 3.0
- `MeshData` with empty segment list → `verdict = "insufficient_data"`

### Step 2: Expand `test_section_builders.py` — add results/loads/fatigue/materials/BC/other tests

Add to `tests/solvers/orcaflex/reporting/test_section_builders.py`:
- `test_static_results_builder_with_data` — StaticResultsData with tension_profile + bm_profile
- `test_dynamic_results_builder_with_data` — DynamicResultsData with TimeSeriesData + EnvelopeData
- `test_extreme_results_builder_with_data` — ExtremeResultsData with mpm_values
- `test_loads_builder_with_data` — EnvironmentData with LoadCaseData
- `test_fatigue_builder_with_data` — FatigueResultsData
- `test_materials_builder_with_data` — MaterialData with LineTypeData
- `test_boundary_conditions_builder_with_data` — BCData
- `test_other_structures_builder_with_data` — OtherStructuresData

### Step 3: Expand `test_report_generator.py` — offline mode + invalid structure_type

Add to `tests/solvers/orcaflex/reporting/test_report_generator.py`:
- `test_generate_report_offline_mode` — `include_plotlyjs=True`; assert no `cdn.plot.ly` in output
- `test_generate_report_invalid_structure_type` — `data.structure_type="invalid"` → ValueError
- `test_generate_report_creates_parent_directory` — output path with nonexistent parent

### Step 4: Add riser/pipeline renderer integration tests

Add to `tests/solvers/orcaflex/reporting/test_renderers.py`:
- `test_riser_renderer_with_tdp_excursion` — riser report with DynamicResultsData.tdp_excursion_history
- `test_pipeline_renderer_sections` — pipeline report produces `#geometry-kp-chainage`

### Step 5: Run tests + coverage check

```bash
cd /d/workspace-hub/digitalmodel
python -m pytest tests/solvers/orcaflex/reporting/ -v --cov=digitalmodel.solvers.orcaflex.reporting --cov-fail-under=80
```

Target: ≥ 80% coverage, 0 failures.

### Step 6: Legal sanity scan

```bash
bash /d/workspace-hub/scripts/legal/legal-sanity-scan.sh
```

### Step 7: Commit and update WRK-129 spec progress

Commit in `digitalmodel` submodule first, then update hub pointer.
Update `specs/modules/wrk-129-orcaflex-analysis-reporting.md`:
- Phase 1 → ✅ Complete
- progress: 20% → 50%

## Critical Files

- **Tests to expand**: `digitalmodel/tests/solvers/orcaflex/reporting/test_section_builders.py`
- **Tests to create**: `digitalmodel/tests/solvers/orcaflex/reporting/test_mesh_quality.py`
- **Tests to expand**: `digitalmodel/tests/solvers/orcaflex/reporting/test_report_generator.py`
- **Tests to expand**: `digitalmodel/tests/solvers/orcaflex/reporting/test_renderers.py`
- **Spec to update**: `specs/modules/wrk-129-orcaflex-analysis-reporting.md`

## Verification

1. `python -m pytest tests/solvers/orcaflex/reporting/ -v --cov=digitalmodel.solvers.orcaflex.reporting --cov-fail-under=80` — must show ≥ 80% + all pass
2. `bash /d/workspace-hub/scripts/legal/legal-sanity-scan.sh` — must pass (0 block violations)
3. `git diff --stat` in digitalmodel — only test additions, no source changes
