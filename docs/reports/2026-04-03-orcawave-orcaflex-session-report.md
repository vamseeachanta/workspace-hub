# OrcaWave/OrcaFlex Session Report — 2026-04-03/04

## Summary

Executed all 4 dev-primary OrcaWave/OrcaFlex issues that were unblocked by licensed-win-1 fixture generation. Built the full automated pipeline from OrcaWave results to OrcaFlex vessel type files.

## Issues Closed (9)

| Issue | Title | Machine |
|-------|-------|---------|
| #1765 | RAO extractor: xlsx → RAODatabase | dev-primary |
| #1766 | OrcaWave-to-OrcaFlex handoff validation suite | dev-primary |
| #1768 | Automated handoff pipeline + CLI | dev-primary |
| #1605 | OrcaWave-to-OrcaFlex integration test | dev-primary |
| #1592 | Automate OrcaWave → OrcaFlex handoff | dev-primary |
| #1761 | Queue validation with WAMIT batch | licensed-win-1 |
| #1762 | Minimal OrcaFlex .sim fixture | licensed-win-1 |
| #1763 | OrcaWave .owr result fixtures (4/5, hemisphere failed) | licensed-win-1 |
| #1764 | Mooring .sim with RAO vessel | licensed-win-1 |

## New Production Modules

### 1. `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/rao_extractor.py`
- **XlsxFormatDetector**: auto-detect pipeline vs native OrcaWave xlsx
- **PipelineXlsxReader**: parse process-queue.py xlsx (RAOs, AddedMass, Damping sheets)
- **NativeXlsxReader**: parse OrcaWave GUI xlsx (Displacement RAOs, per-frequency 6x6 blocks)
- **HydroCoefficients**: dataclass for 6x6 added mass + damping matrices
- **xlsx_to_rao_data()**: convenience auto-detecting function → RAOData
- **xlsx_to_hydro_coefficients()**: convenience for matrix extraction
- **populate_database_from_xlsx()**: full pipeline → RAODatabase with Parquet persistence
- No OrcFxAPI dependency

### 2. `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_to_orcaflex.py`
- **convert_orcawave_xlsx_to_orcaflex()**: single-command pipeline
- **rao_data_to_diffraction_results()**: bridge RAOData → DiffractionResults
- CLI: `python -m digitalmodel.hydrodynamics.diffraction.orcawave_to_orcaflex input.xlsx -o output/`
- No OrcFxAPI dependency

### 3. Queue Integration
- `scripts/solver/post-process-hook.py`: `try_orcaflex_handoff()` auto-converts completed OrcaWave jobs

## New Tests (240 total)

| Test File | Count | Coverage |
|-----------|-------|----------|
| test_rao_extractor.py | 45 | Pipeline/native xlsx readers, RAODatabase population, persistence |
| test_orcawave_to_orcaflex_integration.py | 33 | Full round-trip, DOF-level 1%/5° validation, cross-format |
| test_orcawave_to_orcaflex_pipeline.py | 24 | Single-command pipeline, CLI, error handling |
| test_report_data_models.py | 69 | All dataclasses, serialization, defaults |
| test_report_computations.py | 69 | All computation functions, boundary cases |

## Commits

| Repo | Commit | Description |
|------|--------|-------------|
| digitalmodel | b923c993 | RAO extractor pipeline |
| digitalmodel | afa495bf | Handoff validation suite |
| digitalmodel | 49f174d9 | Report data models + computations tests |
| digitalmodel | 23275916 | Automated handoff pipeline + CLI |
| workspace-hub | 9a76a176 | Post-process-hook integration + operator map |

## Future Issues Created (6)

| Issue | Title | Priority |
|-------|-------|----------|
| #1784 | diffraction: benchmark subsystem test coverage (11 files) | medium |
| #1785 | diffraction: CLI and exporter test coverage (6 files) | low |
| #1786 | RAO comparison plots: extracted vs WAMIT reference | medium |
| #1787 | auto-populate RAODatabase from solver queue completions | medium |
| #1788 | OrcaFlex .sim snapshot testing | medium |
| #1789 | licensed-win-1: retry hemisphere.owr (missing .gdf) | low |

## Recommended Next Priority

1. **#1787** — RAODatabase auto-population (extends post-process-hook.py, quick win)
2. **#1786** — RAO comparison plots (visualization evidence for GTM)
3. **#1784** — Benchmark test coverage (code quality)
4. **#1788** — .sim snapshot testing (requires creative approach without OrcFxAPI)
5. **#1694** — Fatigue post-processing chain (new engineering capability)

## Key Technical Discoveries

1. **xlsx sidecar strategy works**: All dev-primary work was done without OrcFxAPI by reading .xlsx files exported on licensed-win-1. This is the canonical pattern.

2. **Two xlsx formats exist**: Pipeline format (from process-queue.py) uses clean flat tables. Native format (from OrcaWave GUI) uses per-heading blocks with heading in column 0. The auto-detector handles both.

3. **Two RAO data models must be bridged**: RAOData (simple, from models.py) vs DiffractionResults (complex, from output_schemas.py). The bridge function `rao_data_to_diffraction_results()` handles this.

4. **Hydrodynamic matrices are NOT symmetric**: Surge-pitch and sway-roll coupling terms differ by ~1-3%. Tests should not assert exact symmetry.

5. **DiffractionResults.added_mass/damping are NOT Optional**: Must provide zero-filled matrices when coefficients are unavailable.
