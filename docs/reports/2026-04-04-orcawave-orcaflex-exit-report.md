# OrcaWave/OrcaFlex Work Stream — Exit Report

Date: 2026-04-04
Sessions: 3 (April 3 dev-primary, April 3-4 licensed-win-1, April 4 dev-primary)

## Executive Summary

The OrcaWave → OrcaFlex automated pipeline is complete and validated. All dev-primary engineering work is done. Remaining items are either blocked on licensed-win-1 (.sim metadata extraction) or low-priority enhancements.

## Issues Closed (14 total)

### Dev-Primary (9)
| Issue | Title |
|-------|-------|
| #1597 | RAO extractor and database population pipeline |
| #1592 | Automate OrcaWave → OrcaFlex handoff |
| #1605 | OrcaWave-to-OrcaFlex integration test |
| #1765 | RAO extractor implementation |
| #1766 | Handoff validation suite |
| #1768 | Automated pipeline + CLI |
| #1784 | Benchmark test coverage (266 tests) |
| #1785 | CLI/exporter test coverage (84 tests) |
| #1786 | RAO comparison plots |
| #1787 | RAODatabase auto-population |
| #1572 | Domain capability roadmaps |

### Licensed-Win-1 (4)
| Issue | Title |
|-------|-------|
| #1761 | Queue validation with WAMIT batch |
| #1762 | Minimal OrcaFlex .sim fixture |
| #1763 | OrcaWave .owr result fixtures |
| #1764 | Mooring .sim with RAO vessel |

## Production Modules Delivered

| Module | Purpose |
|--------|---------|
| `hull_library/rao_extractor.py` | xlsx → RAOData + HydroCoefficients (auto-detects pipeline/native format) |
| `diffraction/orcawave_to_orcaflex.py` | Single-command pipeline + CLI: xlsx → OrcaFlex YAML/CSV |
| `scripts/solver/post-process-hook.py` | Queue auto-hooks: JSONL + RAODatabase + OrcaFlex handoff |
| `scripts/solver/query_rao_database.py` | CLI to list/inspect/query RAODatabase |
| `scripts/solver/generate_rao_comparison_plots.py` | Interactive Plotly comparison: extracted vs benchmark |
| `scripts/solver/validate_xlsx_against_owr.py` | Licensed-win-1 validation: xlsx vs .owr binary |

## Test Coverage

| Test File | Tests | Coverage |
|-----------|-------|----------|
| test_rao_extractor.py | 45 | Pipeline/native xlsx readers, RAODatabase |
| test_orcawave_to_orcaflex_integration.py | 33 | Full round-trip, DOF validation |
| test_orcawave_to_orcaflex_pipeline.py | 24 | Pipeline, CLI, error handling |
| test_report_data_models.py | 69 | All report dataclasses |
| test_report_computations.py | 69 | All computation functions |
| test_benchmark_*.py (11 files) | 266 | Full benchmark subsystem |
| test_orcaflex_exporter.py | 28 | Export to YAML/CSV/Excel |
| test_batch_processor.py | 32 | Batch job processing |
| test_geometry_quality.py | 24 | Mesh quality analysis |
| **Total new tests** | **590** | |

## Validation Evidence

| Test | Result |
|------|--------|
| xlsx-vs-owr (3 geometries) | ALL PASS at machine epsilon (~1e-16) |
| RAO comparison (6 DOFs) | <0.06% on all significant amplitudes |
| OrcaFlex model creation | Pipeline output loaded by OrcaFlex on licensed-win-1 |
| Cross-format consistency | Pipeline vs native xlsx: identical results |

## Fixture Library (7 .owr + 6 .xlsx + 2 .sim)

| File | Geometry | Freq | Headings |
|------|----------|------|----------|
| test01_unit_box.owr/.xlsx | Unit box | 50 | 2 |
| ellipsoid.owr/.xlsx | Ellipsoid | 1 | 18 |
| L00_test01.owr/.xlsx | Unit box (native) | 50 | 2 |
| L01_001_ship_raos.owr/.xlsx | Ship | ? | ? |
| L02_OC4_semi_sub.owr/.xlsx | Semi-sub | 32 | 9 |
| minimal_test.sim/.dat | Vessel + mooring | — | — |
| mooring_with_raos.sim | Mooring with RAO vessel | — | — |

## Future Issues Created (4)

| Issue | Title | Priority |
|-------|-------|----------|
| #1827 | licensed-win-1: extract .sim metadata to JSON for snapshot testing | medium |
| #1828 | populate RAODatabase from all 5 xlsx fixtures | low |
| #1829 | RAO comparison plots for L02 OC4 semi-sub | low |
| #1830 | review and close solver queue bug fixes #1703-#1706 | medium |

## Still Open

| Issue | Title | Status |
|-------|-------|--------|
| #1586 | Harden solver queue | 90% done, pending #1703-#1706 review |
| #1652 | OrcaFlex .sim snapshot testing | Blocked on licensed-win-1 (#1827) |
| #1788 | .sim snapshot testing | Blocked on licensed-win-1 (#1827) |
| #1789 | Hemisphere .gdf | Blocked/backlog — file not found anywhere |
| #1694 | Fatigue post-processing chain | Future engineering work |

## Key Technical Learnings

1. **xlsx sidecar strategy is the canonical bridge** — all dev-primary work uses .xlsx, validated bit-exact against .owr
2. **Rotational DOFs need rad→deg conversion** — OrcFxAPI outputs rad/m, benchmark/display uses deg/m
3. **DiffractionResults.added_mass/damping are NOT Optional** — must zero-fill when coefficients unavailable
4. **OrcFxAPI 11.6 API differences** — `d.frequencyCount`/`d.bodyCount` don't exist, use `len(np.array(d.frequencies))` and `d.addedMass.shape[1]//6`
5. **Hydrodynamic matrices are NOT symmetric** — surge-pitch coupling differs by ~1-3%
6. **HemisphereAndLid0814.gdf does not exist** on any accessible drive — searched /mnt/ace, D:\, C:\Program Files\Orcina\

## Recommended Next Priorities

1. **#1830** — review queue bug fixes (quick triage, may already be resolved)
2. **#1827** — .sim metadata extraction on licensed-win-1 (unblocks #1652, #1788)
3. **#1694** — fatigue post-processing (new engineering capability, high GTM value)
4. **#1828/#1829** — database population + L02 plots (low-priority polish)
