# Plan: Parametric Hull Analysis Module (#466)

## Context

The digitalmodel repository has three mature hydrodynamics modules — hull_library (parametric geometry + mesh), capytaine (BEM solver), and passing_ship (Wang 1975 slender-body forces) — but no orchestration layer that sweeps hull forms through these solvers to produce comparison tables and operability charts. This module fills that gap.

**Critical finding from research**: Capytaine cannot do multi-body + forward-speed simultaneously (limitation until v3.0). Ship-ship interaction uses the existing passing_ship module. Capytaine handles finite-depth BEM natively via Delhommeau Green function — no custom shallow water BEM needed.

## Module Structure

```
src/digitalmodel/hydrodynamics/parametric_hull_analysis/
├── __init__.py          # Public API, v0.1.0
├── manifest.yaml        # DNV-RP-C205 + PIANC 121 traceability
├── models.py            # Pydantic/dataclass configs + result containers
├── sweep.py             # Core: hull_library → Capytaine BEM → RAODatabase
├── forward_speed.py     # DNV-RP-C205 §7.4 encounter frequency corrections
├── shallow_water.py     # DNV validation factors + PIANC 121 bank effects
├── passing_ship_sweep.py # hull variants → passing_ship forces
└── charts.py            # matplotlib parametric plots
```

## Implementation Phases

### Phase A — Core Sweep (implement first)
1. **models.py** — `SweepConfig`, `SweepResultEntry`, `DepthClassification`, `BankSlopeType`, `PassingShipSweepConfig`, `PassingShipSweepEntry`, `BankEffectResult`, `classify_depth()`
2. **sweep.py** — `run_parametric_sweep(config, catalog, output_dir)` → `(list[SweepResultEntry], RAODatabase)`
   - Build `HullParametricSpace` from config
   - For each variation: `HullMeshGenerator().generate()` → `PanelMesh` → `export_scaled_gdf()` → `.gdf` file
   - Build `BodyConfig(mesh=MeshConfig(path=gdf))` + `WaveConditions(water_depth=...)`
   - `run_bem_analysis()` → `BEMResult` → `compute_rao()` → `RAOResult`
   - Store in `RAODatabase`, return results list
   - `sweep_to_dataframe()` for comparison tables
3. **manifest.yaml** — 6 function entries with clause traceability
4. **__init__.py** — exports

### Phase B — Shallow Water + Forward Speed
5. **shallow_water.py**
   - `dnv_shallow_water_factor(h_over_T, dof)` — analytical correction from DNV-RP-C205 Table 7-1
   - `validate_shallow_water_results(bem_deep, bem_shallow, draft, depth)` — compare Capytaine vs DNV
   - `pianc_bank_suction_force(speed, depth, Am, clearance, slope)` — PIANC 121 §5.2 bank model
   - `pianc_bank_clearance_width(beam, draft, depth, speed, slope)` — PIANC 121 Table 5.4
6. **forward_speed.py**
   - `encounter_frequency(omega, U, heading, depth)` — ω_e = ω - k·U·cos(β) per DNV §7.4.1
   - `wave_number(omega, depth)` — dispersion relation (Newton iteration for finite depth)
   - `correct_rao_for_speed(rao, U, depth)` — remap RAO to encounter frequency domain
   - `strip_theory_speed_correction(A, B, omega, U, L)` — first-order A/B corrections

### Phase C — Passing Ship Integration
7. **passing_ship_sweep.py**
   - `hull_profile_to_vessel_config(HullProfile)` → `VesselConfig`
   - `run_passing_ship_sweep(hull_variants, passing_vessel, config)` → `list[PassingShipSweepEntry]`
   - `passing_ship_to_dataframe()`, `peak_force_envelope()`, `pianc_operability_check()`

### Phase D — Visualization
8. **charts.py**
   - `rao_comparison_grid()` — overlay all variations per DOF
   - `parameter_sensitivity_plot()` — single param vs peak RAO
   - `depth_sensitivity_plot()` — Capytaine A(h/T) vs DNV curve
   - `passing_ship_contour()` — (separation × speed) → peak force
   - `operability_chart()` — green/red binary per scenario

## Key Integration Points

| From | Function | To |
|---|---|---|
| hull_library | `HullParametricSpace.generate_profiles(catalog)` | sweep.py |
| hull_library | `HullMeshGenerator().generate(profile, config)` | sweep.py |
| hull_library | `export_scaled_gdf(mesh, path)` | sweep.py (mesh export) |
| hull_library | `RAODatabase.store(entry)` | sweep.py (result storage) |
| capytaine | `run_bem_analysis(body, waves, solver)` | sweep.py |
| capytaine | `compute_rao(bem_result)` | sweep.py |
| passing_ship | `PassingShipCalculator`, `VesselConfig`, `EnvironmentalConfig` | passing_ship_sweep.py |
| passing_ship | `generate_time_history()` | passing_ship_sweep.py |

## Design Decisions

1. **Mesh path**: `PanelMesh` → `export_scaled_gdf(mesh, output_dir/meshes/var_id.gdf)` → `MeshConfig(path=...)`. Write to `output_dir/meshes/` (not temp files) for reproducibility.
2. **No Capytaine wrapper modification**: Use analytical encounter frequency correction rather than exposing `forward_speed` on `CapytaineSolver`. Simpler, works for all cases.
3. **No multi-body BEM**: Use passing_ship module for ship-ship interaction. Capytaine limitation is fundamental.
4. **Memory**: For large sweeps, store to RAODatabase incrementally. `SweepResultEntry` holds full objects for small sweeps; for >100 variations, flush to Parquet.

## Verification

1. `uv run python scripts/validate_manifests.py` — manifest schema passes
2. Small sweep test: 2 hull variants × 3 periods × 1 heading at infinite depth → verify RAO shapes reasonable
3. Shallow water: run same hull at depth=inf and depth=20m → compare `validate_shallow_water_results()` error < 20%
4. Forward speed: verify `encounter_frequency()` matches ω_e = ω - ω²U·cos(β)/g for deep water
5. Passing ship: 1 hull variant, 3 separations × 2 speeds → verify forces scale with V² and decay with distance
6. Import test: `from digitalmodel.hydrodynamics.parametric_hull_analysis import run_parametric_sweep`
