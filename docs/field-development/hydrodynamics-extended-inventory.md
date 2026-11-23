# Offshore Hydrodynamics — Extended Code Coverage Inventory (R5)

**Issue:** [#2673](https://github.com/vamseeachanta/workspace-hub/issues/2673) (R5 Code Audit, parent [#2668](https://github.com/vamseeachanta/workspace-hub/issues/2668) — Domain Sweep: Offshore Hydrodynamics)
**Companion to:** [`hydrodynamics-preliminary-inventory.md`](./hydrodynamics-preliminary-inventory.md)
**Date:** 2026-05-12
**Audit author:** R5 subagent (extended scope)
**Scope:** `digitalmodel/src/digitalmodel/hydrodynamics/` — the sibling package flagged as "Surprise 1" in the preliminary inventory. Read-only audit; no code modifications.

> **Status note:** All rows below carry `PRELIMINARY — pending R1/R2 validation` (same gate as the preliminary inventory). The `hydrodynamics/` package is markedly larger than the `orcawave/` surface — 18 top-level units and ~2,615 test functions across 138 test files.

---

## 1. Inventory Table

| Component | Module Path | Standards / References (docstring) | Tests | Status |
|---|---|---|---|---|
| Package facade (re-exports models, spectra, OCIMF, interpolator, seakeeping helpers, optional capytaine) | `digitalmodel/src/digitalmodel/hydrodynamics/__init__.py` | (re-exports below) | n/a | PRELIMINARY — pending R1/R2 validation |
| CLI (`spectrum`, `wind`, `current`, `combined-env`) | `digitalmodel/src/digitalmodel/hydrodynamics/cli.py` | OCIMF MEG4 | 15 (`tests/hydrodynamics/test_hydrodynamics_cli.py`) | PRELIMINARY — pending R1/R2 validation |
| Data models: `HydrodynamicMatrix`, `VesselProperties`, `WaveSpectrumType`, `WaveParameters`, `EnvironmentalConditions`, `RAOData`, `MatrixDOF`, `get_vessel_type` | `digitalmodel/src/digitalmodel/hydrodynamics/models.py` | DNV-RP-C205 (axis convention) | 25 shared with unit suite (`tests/hydrodynamics/test_hydrodynamics_unit.py`) | PRELIMINARY — pending R1/R2 validation |
| Wave spectra: JONSWAP, Pierson-Moskowitz, Bretschneider, ISSC, spectral moments, stats (Hs, Tz, Tp, ε) | `digitalmodel/src/digitalmodel/hydrodynamics/wave_spectra.py` | DNV-RP-C205 §3.5.1, §3.5.2 | (covered in unit + seakeeping suites; ~20 tests touching spectra) | PRELIMINARY — pending R1/R2 validation |
| Seakeeping: response spectrum, spectral moments, significant amplitude, Rayleigh exceedance, **operability analysis** | `digitalmodel/src/digitalmodel/hydrodynamics/seakeeping.py` | DNV-RP-C205; Journée & Massie Ch.6; PNA Vol III | 20 (`tests/hydrodynamics/test_seakeeping.py`) | PRELIMINARY — pending R1/R2 validation |
| OCIMF wind/current/combined loads + Newman drift force; vessel area estimator | `digitalmodel/src/digitalmodel/hydrodynamics/ocimf_loading.py` | OCIMF MEG4 §3.2, §3.3; OCIMF "Prediction of Wind and Current Loads on VLCCs" | 26 (`tests/marine_ops/marine_engineering/environmental_loading/test_ocimf.py`) + integration | PRELIMINARY — pending R1/R2 validation |
| Frequency-dependent 6×6 hydro coefficient database (JSON persist, symmetry/PD checks, infinite-freq added mass) | `digitalmodel/src/digitalmodel/hydrodynamics/coefficient_database.py` | DNV-RP-H103 | (in `test_hydrodynamics_unit.py`) | PRELIMINARY — pending R1/R2 validation |
| RAO/coefficient interpolator (1D/2D in freq×heading; cubic fallback to linear; per-DOF extract) | `digitalmodel/src/digitalmodel/hydrodynamics/interpolator.py` | (none in docstring) | (in `test_hydrodynamics_unit.py`) | PRELIMINARY — pending R1/R2 validation |
| Propeller-rudder interaction (Söding/Brix primary; actuator-disk + flat-plate fallback) | `digitalmodel/src/digitalmodel/hydrodynamics/propeller_rudder.py` | McTaggart (2005) DRDC TM 2005-071; Carlton (2007); Molland & Turnock (2007) | 36 (`tests/test_propeller_rudder_interaction.py`) + 26 (`tests/docs/test_propeller_rudder_method_selection.py`) | PRELIMINARY — pending R1/R2 validation |
| **aqwa/** subpackage — ANSYS AQWA pre/post, DAT/LIS/AH1 readers, RAO extraction, viscous damping orchestration, EF server, CLI router | `digitalmodel/src/digitalmodel/hydrodynamics/aqwa/` (15 modules + `aqwa_validation/`) | (vendor-format docs; no formal code refs in docstrings) | 33 across 14 files (`tests/hydrodynamics/aqwa/`) | PRELIMINARY — pending R1/R2 validation |
| **bemrosetta/** subpackage — AQWA→OrcaFlex coefficient conversion (parsers, converters, validators, mesh formats, optional `BEMRosetta_cl.exe` runner) | `digitalmodel/src/digitalmodel/hydrodynamics/bemrosetta/` (parsers, converters, validators, mesh, core, models, cli) | (file-format-driven; OpenFAST HydroDyn future) | 358 across 10 files (`tests/hydrodynamics/bemrosetta/`) | PRELIMINARY — pending R1/R2 validation |
| **capytaine/** subpackage — Capytaine BEM solver wrapper (mesh adapter, solver, RAO impedance, NetCDF/plot results) | `digitalmodel/src/digitalmodel/hydrodynamics/capytaine/` | DNV-RP-C205 §7.1, §7.2.1, §7.2.5, §7.3.1, §3.3 (`manifest.yaml` machine-readable) | 29 across 3 files (cylinder, sphere, OC4-semisub benchmarks) | PRELIMINARY — pending R1/R2 validation |
| **diffraction/** subpackage — unified RAO/added-mass/damping schemas; AQWA + OrcaWave backends/runners/batch + OrcaFlex export; benchmark suite; output_validator (resonance, symmetry, completeness); report generator | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/` (~60 modules) | DNV-OS-C301 (MOU freeboard min); ISO 6954 (phase convention); Faltinsen 1990 *Sea Loads on Ships and Offshore Structures* | 1,365 across 59 files (`tests/hydrodynamics/diffraction/`) | PRELIMINARY — pending R1/R2 validation |
| **rao_analysis/** subpackage — OrcaFlex displacement RAO reading, plotting, comparison (multi-vessel/heading) | `digitalmodel/src/digitalmodel/hydrodynamics/rao_analysis/` | (none in docstring) | 1 (`tests/hydrodynamics/rao_analysis/`) | PRELIMINARY — pending R1/R2 validation |
| **hull_library/** subpackage — line-profile hull definition; on-demand panel mesh generation; mesh coarsening/refinement/scaling (gmsh + VTK decimation); panel catalog; RAO registry + database; schematic generator; lookup; parametric hull space | `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/` (24 modules + `line_generator/`) | (none formally; mesh-quality heuristics) | 428 across 24 files (`tests/hydrodynamics/hull_library/`) | PRELIMINARY — pending R1/R2 validation |
| **parametric_hull_analysis/** subpackage — orchestrates hull_library + capytaine + passing_ship sweeps; forward-speed encounter-frequency RAO correction (Salvesen-Tuck-Faltinsen 1970); DNV shallow-water amplification table; PIANC 121 bank suction + clearance; **`pianc_operability_check`** (binary go/no-go on sway+yaw thresholds); operability/sensitivity charts | `digitalmodel/src/digitalmodel/hydrodynamics/parametric_hull_analysis/` (sweep, forward_speed, shallow_water, passing_ship_sweep, charts, models; `manifest.yaml`) | DNV-RP-C205 (2021) §7.1, §7.2, §7.4 Table 7-1; PIANC Report 121 (2014) §5.2 Table 5.2, Table 5.4; Wang (1975); Salvesen-Tuck-Faltinsen (1970) | 126 across 4 files (`tests/hydrodynamics/parametric_hull_analysis/`) | PRELIMINARY — pending R1/R2 validation |
| **passing_ship/** subpackage — Wang (1975) slender-body passing-ship forces (surge, sway, yaw, S1/S2 area, F/G kernels, finite-depth correction); calculator + ResultCache; YAML config + unit converter; CLI; visualisation; benchmark report | `digitalmodel/src/digitalmodel/hydrodynamics/passing_ship/` (formulations, calculator, configuration, visualization, input_schemas, exporters, force_time_history, benchmark_report) | Wang (1975); MathCAD reference benchmark | 235 across 10 files (`tests/hydrodynamics/passing_ship/`) | PRELIMINARY — pending R1/R2 validation |
| **planing_hull/** subpackage — 2D+t Wagner water-entry strip theory for heave/pitch RAO of high-speed planing vessels | `digitalmodel/src/digitalmodel/hydrodynamics/planing_hull/` (geometry, strip_model, solver) | Wagner water-entry strip theory (no explicit reference in docstring) | 26 (`tests/unit/hydrodynamics/test_planing_hull.py`) | PRELIMINARY — pending R1/R2 validation |

**Modules audited:** 18 top-level units (9 .py files + 9 subpackages) covering ~150 Python modules in aggregate.
**Total scoped tests:** ~2,615 test functions across 138 test files under `tests/hydrodynamics/` plus ~88 additional in `tests/marine_ops/`, `tests/unit/hydrodynamics/`, `tests/test_propeller_rudder_interaction.py`, `tests/docs/`.

---

## 2. Public API Signatures (high-traffic surfaces)

### `hydrodynamics/wave_spectra.py` — `class WaveSpectra`
- `.jonswap(hs, tp, gamma=3.3, freq_min=0.02, freq_max=2.0, n_points=100)`
- `.pierson_moskowitz(hs, tp, ...)` / `.bretschneider(...)` / `.issc(...)`
- `.generate_spectrum(params: WaveParameters)` (dispatcher)
- `.spectral_moment(frequencies, spectrum, n=0)` — generic `m_n = ∫ ω^n · S(ω) dω`
- `.significant_height_from_spectrum(...)`, `.zero_crossing_period_from_spectrum(...)`, `.peak_frequency_from_spectrum(...)`
- `.spectrum_statistics(...)` returns `{m0, m1, m2, m4, Hs_m, Tz_s, Tp_s, omega_p_rad_s, spectral_width}`

### `hydrodynamics/seakeeping.py`
- `compute_response_spectrum(rao_amplitudes, wave_spectrum) -> np.ndarray`
- `spectral_moments(frequencies, spectrum, orders=None) -> Dict[int, float]` (defaults `[0, 2, 4]`)
- `significant_amplitude(m0) -> float`  (`s_{1/3} = 2·√m0`)
- `motion_exceedance(m0, threshold) -> float`  (Rayleigh tail)
- `operability_analysis(rao_freqs, rao_amplitudes, scatter_diagram, criteria, spectrum_type="jonswap", gamma=3.3) -> Dict`

### `hydrodynamics/ocimf_loading.py` — `class OCIMFLoading`
- `.wind_load(vessel, wind_speed, wind_direction=0.0, air_density=None) -> {Fx, Fy, Mz}`
- `.current_load(vessel, current_speed, current_direction=0.0, water_density=None) -> {Fx, Fy, Mz}`
- `.combined_environmental_load(vessel, env)` ; `.estimate_wind_area(...)` ; `.newman_drift_force(...)`

### `hydrodynamics/coefficient_database.py` — `class CoefficientDatabase`
- `.store_matrix(vessel, freq, matrix, matrix_type)` / `.store(vessel, HydrodynamicMatrix)`
- `.get_matrix(vessel, freq, matrix_type, interpolate=True)` (linear interp across freq grid)
- `.get_matrices(...)`, `.get_frequencies(...)`, `.get_infinite_frequency_added_mass(...)`
- `.save_to_file(path)`, `.load_from_file(path)`, `.list_vessels()`
- `.check_symmetry(vessel, freq)`, `.check_positive_definite(...)`, `.summary(vessel)`

### `hydrodynamics/interpolator.py` — `class CoefficientsInterpolator`
- `.load_raos(RAOData)`, `.interpolate_rao_1d(...)`, `.interpolate_rao_2d(...)` (frequency × heading)
- `.interpolate_all_dofs(...)`, `.frequency_interpolation(...)`
- `.extract_rao_at_frequency(...)`, `.extract_rao_at_direction(...)`

### `hydrodynamics/propeller_rudder.py`
- `kt_from_poly(J, coeffs)` ; `soding_forces(...)` (primary)
- `actuator_disk_velocity(...)` ; `flat_plate_rudder_cl(alpha_deg, aspect_ratio)` ; `ad_flat_plate_forces(...)`

### `hydrodynamics/parametric_hull_analysis/` (selected)
- `encounter_frequency(omega, U, beta, h=None, ...)`, `wave_number(omega, h=None)`, `correct_rao_for_speed(rao, U, h=None)`
- `dnv_shallow_water_factor(h_over_T, dof)` — DNV-RP-C205 Table 7-1
- `pianc_bank_suction_force(speed, depth, midship_area, clearance, slope_type)` — PIANC 121 §5.2
- `pianc_bank_clearance_width(beam, slope_type)` — PIANC 121 Table 5.4
- `run_parametric_sweep(SweepConfig, HullCatalog)` ; `run_passing_ship_sweep(...)`
- `pianc_operability_check(results, max_sway_N, max_yaw_Nm) -> DataFrame` (binary `acceptable` flag)
- `operability_chart(results, threshold_sway_N, threshold_yaw_Nm, ...)`

### `hydrodynamics/passing_ship/` (selected)
- `s1_function(x, L)`, `s2_function(x, L)`, `ds1_dx(...)`, `ds2_dx(...)`
- `f_kernel(...)`, `g_kernel(...)`
- `calculate_surge_force_infinite(...)`, `calculate_sway_force_infinite(...)`, `calculate_yaw_moment_infinite(...)`
- `finite_depth_correction(...)`, `calculate_forces_with_depth(...)`
- `class PassingShipCalculator` (Wang 1975 facade)

### `hydrodynamics/planing_hull/`
- `class PlaningHullGeometry(length, beam, deadrise, chine_height, lcg)`
- `class PlaningStripModel`, `class PlaningMotionSolver`, `class PlaningRAO`
- `compute_rao(hull, speed, wave_freq, wave_steepness)`

### `hydrodynamics/diffraction/` (audit-relevant)
- `class OutputValidator` — `_validate_resonance()` (sharp-peak ratio + amplitude-limit checks; constants `_TRANSLATION_AMP_LIMIT=3.0 m/m`, `_ROTATION_AMP_LIMIT=15.0 deg/m`, `_SHARP_PEAK_RATIO=10.0×`)
- `compute_natural_periods(hydrostatics, added_mass_diagonal, frequencies_rad_s)` — `T_n = 2π·√((M_ii+A_ii(ω_n))/C_ii)` (heave, roll, pitch only)
- `_build_natural_periods_html(...)` — natural-period reporting in diffraction reports

### `hydrodynamics/capytaine/`
- `CapytaineSolver`, `run_bem_analysis(BodyConfig, WaveConditions, SolverConfig) -> BEMResult`
- `compute_rao(BEMResult)`, `compute_rao_manual(BEMResult, mass, stiffness, damping_extra)`
- Results helpers: `added_mass_table`, `excitation_force_table`, `export_netcdf`, `plot_*`

### `hydrodynamics/aqwa/` (router-facing)
- `class Aqwa` (router on `cfg["type"]`: preprocess / analysis / postprocess), `a_pre`, `a_post`, `mes_files`
- `class AqwaPreProcess`, `class AqwaPostProcess`, `class ViscousDampingDetermination` (lazy)
- LIS/DAT/AH1 parsers, RAO/natural-period extractors, EF server bridge, CLI

### `hydrodynamics/bemrosetta/`
- `AQWAParser`, `OrcaFlexConverter`, `is_bemrosetta_available()`, `BEMRosettaRunner`, `BEMRosettaError`/`ParserError`/`ConverterError`/`ValidationError`

### `hydrodynamics/hull_library/`
- Profile: `HullType`, `HullStation`, `HullProfile`, `ParametricRange`, `HullParametricSpace`
- Mesh: `MeshGeneratorConfig`, `HullMeshGenerator`, `coarsen_mesh`, `refine_mesh`, `generate_mesh_family`, `scale_mesh_uniform/parametric/to_target`, `export_scaled_gdf`, `export_mesh_family`, `compute_quality_metrics`, `convergence_summary`
- Catalog/registry: `HullCatalog`, `HullCatalogEntry`, `SeaStateDefinition`, `HullVariation`, `MotionResponse`, `PanelCatalog`, `PanelCatalogEntry`, `RaoReference`, `RaoRegistry`, `RAODatabase`, `RAODatabaseEntry`
- Lookup: `HullLookup`, `HullLookupTarget`, `HullMatch`, `get_hull_form`
- Plots: `per_hull_rao_plot`, `comparison_plot`, `parameter_sweep_plot`, `export_html`, `export_png`

---

## 3. Standards Coverage Snapshot

Codes/references cited in module docstrings or machine-readable `manifest.yaml` files (verbatim — R1 to validate revision currency):

| Code / Reference | Cited In (hydrodynamics) | Use |
|---|---|---|
| DNV-RP-C205 (2021) | `wave_spectra.py` §3.5.1/§3.5.2; `seakeeping.py` (general); `capytaine/manifest.yaml` §7.1, §7.2.5, §3.3, §2.3.1; `parametric_hull_analysis/manifest.yaml` §7.1/§7.2/§7.4; `models.py` (axis convention) | Wave spectra, BEM problem statement, RAO impedance, axis/density conventions, shallow-water factor table |
| DNV-RP-H103 | `coefficient_database.py` | Marine operations (general reference) |
| DNV-OS-C301 | `diffraction/report_computations.py:262` (MOU minimum freeboard 1.0 m) | Mobile offshore unit validation threshold |
| OCIMF MEG4 (Mooring Equipment Guidelines, 4th ed.) | `ocimf_loading.py` §3.2, §3.3 | Wind and current loads on tankers/VLCCs |
| OCIMF "Prediction of Wind and Current Loads on VLCCs" | `ocimf_loading.py` | Coefficient source |
| ISO 6954 | `diffraction/aqwa_converter.py`, `diffraction/benchmark_input_comparison.py` | Phase convention (AQWA lead vs OrcaFlex lag) |
| PIANC Report 121 (2014) §5.2, Tables 5.2/5.4 | `parametric_hull_analysis/shallow_water.py`, `models.py`, `manifest.yaml` | Bank suction, bank clearance widths |
| Wang (1975) | `passing_ship/formulations.py`, `passing_ship/calculator.py`, `passing_ship/benchmark_report.py`, `parametric_hull_analysis/passing_ship_sweep.py` | Slender-body passing-ship interaction |
| Salvesen, Tuck & Faltinsen (1970) | `parametric_hull_analysis/forward_speed.py` | Strip-theory forward-speed corrections |
| Faltinsen (1990), *Sea Loads on Ships and Offshore Structures* | `diffraction/report_builders_responses.py` | Diffraction reporting reference |
| Journée & Massie, *Offshore Hydromechanics* Ch.6 | `seakeeping.py` | Spectral motion analysis |
| PNA Vol III, *Motions in Waves* | `seakeeping.py` | Spectral methods |
| McTaggart (2005), DRDC TM 2005-071 §7-9 | `propeller_rudder.py` | Söding/Brix rudder forces |
| Carlton (2007), *Marine Propellers and Propulsion* | `propeller_rudder.py` | Propeller theory |
| Molland & Turnock (2007), *Marine Rudders and Control Surfaces* | `propeller_rudder.py` | Rudder hydrodynamics |
| Wagner water-entry strip theory | `planing_hull/__init__.py` (informal) | 2D+t planing motion solver |
| MathCAD reference benchmark | `passing_ship/benchmark_report.py` (validation only) | Tooling cross-check, not a formal standard |

**R1 must verify:** DNV-RP-C205 cited as 2021 in `parametric_hull_analysis/manifest.yaml` — confirm latest revision; DNV-OS-C301 currency (renamed/superseded?); OCIMF MEG4 vs. MEG-5 currency; PIANC 121 (2014) currency.
**R2 must source:** Wagner (citation absent in `planing_hull/`); Wang (1975) full bibliographic entry; Faltinsen 1990 ISBN/edition; Journée & Massie edition; PNA Vol III edition (Lewis 1989).

---

## 4. Overlap with In-Scope Modules (Drift Risk)

The preliminary inventory listed 12 in-scope modules. The audit confirms that `hydrodynamics/` contains parallel or overlapping implementations for several of them. **Each row below is a duplication that R6 must explicitly reconcile** (consolidate, choose-one, or formalise a façade).

| Capability | In-scope (preliminary) module | Overlapping hydrodynamics/ module | Drift Risk |
|---|---|---|---|
| Wave spectra (JONSWAP / PM / Bretschneider / ISSC) | `orcawave/wave_spectrum.py` — `pierson_moskowitz`, `jonswap`, `bretschneider`, `issc_spectrum`, `ochi_hubble`, `torsethaugen`, `generate_spectrum`, `compute_spectral_moments` | `hydrodynamics/wave_spectra.py` — `WaveSpectra.jonswap/.pierson_moskowitz/.bretschneider/.issc/.generate_spectrum/.spectral_moment` plus `_normalize_to_significant_height` Hs-scaling | **HIGH** — two independent JONSWAP/PM/Bretschneider implementations; the hydrodynamics version re-normalises to target Hs, the orcawave version does not document this step. Numerical results will diverge for any caller switching surfaces. `hydrodynamics/` is missing Ochi-Hubble and Torsethaugen; `orcawave/` lacks the Hs-renormalisation step. |
| Spectral moments (m0, m1, m2, m4) | `orcawave/wave_spectrum.py` — `compute_spectral_moments`, `SpectralMoments` (pydantic) | `hydrodynamics/seakeeping.py` — `spectral_moments(frequencies, spectrum, orders=None)`; **also** `hydrodynamics/wave_spectra.py:WaveSpectra.spectral_moment` (scalar n-th moment) | **MEDIUM** — three implementations: orcawave (pydantic-typed), hydrodynamics top-level (multi-order dict), hydrodynamics WaveSpectra method (single order). Trapezoidal integrator is shared in spirit; signatures and return types differ. |
| Response spectrum from RAO × wave spectrum | `orcawave/motion_statistics.py` — `compute_response_spectrum` returning `ResponseSpectrum` (pydantic) | `hydrodynamics/seakeeping.py` — `compute_response_spectrum(rao_amplitudes, wave_spectrum)` returning bare `np.ndarray` | **MEDIUM** — same physics (`|RAO|² · S_wave`); both names identical; one returns typed object, the other returns array. Risk: callers may bind to the wrong import path silently. |
| Significant amplitude / Rayleigh quantile / exceedance | `orcawave/motion_statistics.py` — `rayleigh_exceedance`, `rayleigh_quantile`, `short_term_statistics`, `ShortTermStatistics` | `hydrodynamics/seakeeping.py` — `significant_amplitude(m0)`, `motion_exceedance(m0, threshold)` | **MEDIUM** — formulas identical (`s_{1/3} = 2·√m0`, Rayleigh tail). orcawave bundles into a typed statistics object; hydrodynamics exposes scalar helpers. |
| Natural periods (heave / roll / pitch) | `naval_architecture/seakeeping.py` — `natural_roll_period`, `natural_heave_period`, `natural_pitch_period` (closed-form formulas) | `hydrodynamics/diffraction/report_computations.py` — `compute_natural_periods(hydrostatics, added_mass_diagonal, frequencies_rad_s)` (iterative, frequency-dependent A(ω)) **AND** `hydrodynamics/aqwa/aqwa_analysis_raos.py:get_natural_period_from_lis_file`/`get_natural_periods` (LIS-file extraction) **AND** `hydrodynamics/aqwa/aqwa_analysis_damping.py:240-255` (`natural_frequency_rad_s`/`natural_period_s` from damping fit) | **HIGH** — four computation paths for the same physical quantity: closed-form (naval_architecture), frequency-dependent iteration (diffraction.report_computations), LIS-file readback (aqwa), and damping-fit derivation (aqwa). No common interface or cross-check. |
| RAO interpolation across frequency / direction | `orcawave/rao_processing.py` — `interpolate_rao`, `combine_raos_multi_body`, `compare_raos` | `hydrodynamics/interpolator.py` — `CoefficientsInterpolator.interpolate_rao_1d/2d`, `frequency_interpolation`, `interpolate_all_dofs`, `extract_rao_at_frequency/direction` | **MEDIUM** — both surfaces own RAO interpolation; orcawave is functional with caller-supplied tables; hydrodynamics holds state (`load_raos`) and supports cubic→linear degradation. |
| 6×6 hydrodynamic matrices (added mass, damping; symmetry / PD checks) | `orcawave/hydro_coefficients.py` — `HydroMatrix6x6`, `interpolate_matrix_at_frequency`, `to_wamit_added_mass/damping`, `create_hydrostatic_restoring` | `hydrodynamics/coefficient_database.py` — `CoefficientDatabase` (vessel-keyed JSON store), `check_symmetry`, `check_positive_definite`, `get_infinite_frequency_added_mass` ; `hydrodynamics/models.py` — `HydrodynamicMatrix` (dataclass) with `is_symmetric`, `is_positive_definite`, `to_dict` | **HIGH** — `HydroMatrix6x6` (pydantic, orcawave) vs. `HydrodynamicMatrix` (dataclass, hydrodynamics.models) — same concept, distinct types. WAMIT conversion is orcawave-only; persistence is hydrodynamics-only. Callers must pick one. |
| Vessel parameter database / representative RAOs | `orcawave/vessel_database.py` — `VesselParameters`, `VesselRAOSet`, `ParametricHull`, `list_vessels`, `get_vessel`, `get_vessels_by_type`, `get_representative_raos`, `generate_parametric_hull` | `hydrodynamics/hull_library/` — full hull-form library: `HullCatalog`, `HullVariation`, `MotionResponse`, `HullLookup`, `RAODatabase`, `RAODatabaseEntry`, parametric `HullParametricSpace`, on-demand panel mesh, plus `hydrodynamics/models.py:get_vessel_type(vessel_type) -> VesselProperties` | **HIGH** — `orcawave/vessel_database.py` is a small static list; `hydrodynamics/hull_library/` is a generative library with mesh + RAO registry; `hydrodynamics/models.py:get_vessel_type` is a third lookup. These are not API-compatible. |
| Drift forces (mean + slowly-varying) | `orcawave/drift_forces.py` — `compute_mean_drift_force`, `newman_approximation`, `full_qtf_slowly_varying`, `compute_wind_current_drift` | `hydrodynamics/ocimf_loading.py:268` — `newman_drift_force(...)` (single Newman approximation entry) | **LOW** — small overlap; hydrodynamics provides only the OCIMF-context Newman entry. Acceptable; consider thin wrapper to orcawave once that surface stabilises. |
| MSI (motion sickness incidence) | `orcawave/motion_statistics.py` — `motion_sickness_incidence`, `MSIResult` (ISO 2631-1, McCauley) ; `naval_architecture/seakeeping.py` — `motion_sickness_incidence` | (none found in hydrodynamics/) | n/a — no triplication; the two existing MSI surfaces were already flagged in the preliminary inventory. |
| Wind/current load coefficients | (not in scope) | `hydrodynamics/ocimf_loading.py` — wind+current+combined loads | n/a — unique to hydrodynamics. R6 must decide whether OCIMF coverage is in-scope for the Hydrodynamics domain or belongs in a separate environmental-loading sweep. |
| VIV / VIM screening | `orcaflex/viv_screening.py` (in scope) | (none found in hydrodynamics/) | n/a — no overlap. |
| Crane-tip motion / DAF / sling tension | `orcaflex/installation_analysis.py` (in scope) | (none found in hydrodynamics/) | n/a — no overlap. |
| Pipelay dynamics | (not in scope; preliminary inventory does not include) | (none found in hydrodynamics/) | n/a — see GAP G4 below; implementation lives at `digitalmodel/orcaflex/pipelay_analysis.py` outside both audit perimeters. |

**Overlap count:** **8 distinct duplications** (rows marked HIGH/MEDIUM). Three are HIGH-drift (wave spectra, natural periods, hydro matrices) and require explicit reconciliation decisions in R6.

---

## 5. GAP Candidates Already Implemented?

The LinkedIn-source mapping doc (`docs/field-development/rao-hydrodynamics-mapping.md` per task brief) pre-identified four gap candidates G1–G4. Verdict after the extended audit:

### G1 — Resonance Safety Margin Checker — **PARTIAL** (data structures present, no risk-zone rule)
- **What exists:** `hydrodynamics/diffraction/output_validator.py:_validate_resonance()` flags two indicators: (a) sharp RAO peaks (ratio to neighbour-average > `_SHARP_PEAK_RATIO=10.0`), (b) excessive amplification (translation > `3.0 m/m`, rotation > `15.0 deg/m`). `hydrodynamics/diffraction/report_computations.py:compute_natural_periods` returns heave/roll/pitch natural periods. `hydrodynamics/aqwa/aqwa_analysis_raos.py` extracts natural periods from AQWA LIS files.
- **What's missing:** No module compares natural period `T_n` against expected sea-state peak period `T_p` to compute a safety margin (e.g., `|T_n - T_p| / T_p`) or classify a vessel into a risk zone (e.g., "avoid if within ±20%"). The components exist but no rules engine binds them together. **Verdict: PARTIAL — components present, integration absent.**

### G2 — Spectral Moment Calculations (m0, m1, m2) — **ALREADY IMPLEMENTED (in triplicate)**
- `hydrodynamics/wave_spectra.py:WaveSpectra.spectral_moment(frequencies, spectrum, n)` — single moment of arbitrary order.
- `hydrodynamics/wave_spectra.py:WaveSpectra.spectrum_statistics(...)` — returns `m0, m1, m2, m4` plus derived `Hs`, `Tz`, `Tp`, spectral width `ε = √(1 - m2²/(m0·m4))`.
- `hydrodynamics/seakeeping.py:spectral_moments(frequencies, spectrum, orders=None)` — multi-order dict, defaults `[0, 2, 4]`.
- Plus `orcawave/wave_spectrum.py:compute_spectral_moments` (in-scope). **Verdict: ALREADY IMPLEMENTED — three internal implementations exist; consolidation (not addition) is the work.**

### G3 — Operability Rules Engine (vessel-class go/no-go thresholds) — **PARTIAL**
- **What exists:**
  - `hydrodynamics/seakeeping.py:operability_analysis(...)` — sea-state-weighted operability percentage from a scatter diagram and a *single* significant-amplitude criterion (currently uses `next(iter(criteria.values()))` — accepts only one DOF).
  - `hydrodynamics/parametric_hull_analysis/passing_ship_sweep.py:pianc_operability_check(results, max_sway_N, max_yaw_Nm)` — binary `acceptable` flag on passing-ship sway+yaw force thresholds.
  - `hydrodynamics/parametric_hull_analysis/charts.py:operability_chart(...)` — green/red operability visualisation.
- **What's missing:** No vessel-class registry mapping (e.g., FPSO / drillship / OSV / heavy-lift) to a set of DOF-specific motion criteria (roll, pitch, heave, vertical acceleration at named locations, helideck, crane-tip). The operability engine accepts only one criterion at a time. **Verdict: PARTIAL — engine exists, vessel-class threshold library absent.**

### G4 — Pipelay Dynamics — **NOT IMPLEMENTED in hydrodynamics/** (lives elsewhere)
- No `pipelay`, `s-lay`, `j-lay`, `reel-lay`, `stinger`, `tensioner`, or `davit` references in `digitalmodel/src/digitalmodel/hydrodynamics/`.
- Pipelay implementation lives at `digitalmodel/src/digitalmodel/orcaflex/pipelay_analysis.py` (outside both the preliminary inventory's R5 scope and this extended scope), with supporting riser/stinger configuration under `digitalmodel/src/digitalmodel/solvers/orcaflex/` and `digitalmodel/src/digitalmodel/infrastructure/base_solvers/marine/`.
- **Verdict: still a GAP for the hydrodynamics package**, but an existing implementation exists in `orcaflex/`. R6 must decide whether pipelay belongs in the Hydrodynamics domain (and thus the gap is a *cross-package coverage* gap, not a true implementation gap) or in a separate Marine Operations domain.

---

## 6. Surprises / Findings to Flag

### Surprise 1: `hydrodynamics/diffraction/` is roughly 60 modules with 1,365 tests
The `diffraction/` subpackage alone outweighs the entire R5 in-scope surface (12 modules, 153 tests). It owns the AQWA ↔ OrcaWave conversion pipeline, OrcaFlex export, benchmark-correlation harness, and resonance/symmetry validators. Treating `hydrodynamics/` as "out of scope" effectively excluded the single largest hydrodynamics surface in the codebase.

### Surprise 2: Three independent natural-period computation paths
Closed-form (`naval_architecture/seakeeping.py`), frequency-dependent BEM iteration (`hydrodynamics/diffraction/report_computations.py`), and two AQWA-output extraction paths (`aqwa/aqwa_analysis_raos.py`, `aqwa/aqwa_analysis_damping.py`) all compute or read natural periods. No common interface. Risk: a caller switching from one path to another will get different numbers for the same vessel.

### Surprise 3: `wave_spectra.py` renormalises to target Hs; `orcawave/wave_spectrum.py` does not
`WaveSpectra._normalize_to_significant_height` rescales the discrete JONSWAP/PM/Bretschneider/ISSC spectrum so its integrated zeroth moment matches `Hs² / 16`. The `orcawave/` implementation returns the analytic spectrum without this discretisation correction. For coarse frequency grids, the two will report different m0 (and hence different `Hs_recovered = 4·√m0`).

### Surprise 4: `OutputValidator._validate_resonance` thresholds are hard-coded magic numbers
`_TRANSLATION_AMP_LIMIT = 3.0 m/m`, `_ROTATION_AMP_LIMIT = 15.0 deg/m`, `_SHARP_PEAK_RATIO = 10.0` — no docstring citation, no DNV/ISO source. Per the calc-citation-contract rule, these are operationally load-bearing for any go/no-go review of a diffraction result and should either be citation-grounded or marked convention-only with explicit caller override.

### Surprise 5: `propeller_rudder.py` lives at the hydrodynamics top level (not under `propulsion/`)
The module references three textbook standards (McTaggart, Carlton, Molland-Turnock) but no formal DNV/ISO code. It is the only resistance-/propulsion-adjacent module under `hydrodynamics/`. R6 should decide whether propeller-rudder interaction is a hydrodynamics surface or belongs under a future `propulsion/` package.

### Surprise 6: `parametric_hull_analysis/manifest.yaml` and `capytaine/manifest.yaml` exist
These two subpackages have machine-readable standards-traceability manifests (function → clause → equation). The rest of the hydrodynamics package does not. This is a pattern worth promoting per the patterns.md enforcement gradient — easy to migrate from prose docstrings to manifest validation in CI.

---

## 7. Test File Index (extended scope)

| Surface | Test path | Test count |
|---|---|---|
| top-level seakeeping helpers | `tests/hydrodynamics/test_seakeeping.py` | 20 |
| CLI | `tests/hydrodynamics/test_hydrodynamics_cli.py` | 15 |
| unit (models, spectra, db, interp) | `tests/hydrodynamics/test_hydrodynamics_unit.py` | 25 |
| shear flow loader | `tests/hydrodynamics/test_shear_flow_loader.py` | 28 |
| aqwa/ | `tests/hydrodynamics/aqwa/test_*.py` (14 files) | 33 |
| bemrosetta/ | `tests/hydrodynamics/bemrosetta/test_*.py` (10 files) | 358 |
| capytaine/ | `tests/hydrodynamics/capytaine/test_*.py` (3 files) | 29 |
| diffraction/ | `tests/hydrodynamics/diffraction/test_*.py` (59 files) | 1,365 |
| hull_library/ | `tests/hydrodynamics/hull_library/test_*.py` (24 files incl. `line_generator/`) | 428 |
| parametric_hull_analysis/ | `tests/hydrodynamics/parametric_hull_analysis/test_*.py` (4 files) | 126 |
| passing_ship/ | `tests/hydrodynamics/passing_ship/test_*.py` (10 files) | 235 |
| rao_analysis/ | `tests/hydrodynamics/rao_analysis/test_rao_analysis.py` | 1 |
| planing_hull/ | `tests/unit/hydrodynamics/test_planing_hull.py` | 26 |
| propeller_rudder | `tests/test_propeller_rudder_interaction.py` + `tests/docs/test_propeller_rudder_method_selection.py` | 36 + 26 |
| OCIMF | `tests/marine_ops/marine_engineering/environmental_loading/test_ocimf.py` (+ integration suite) | 26 + integration |

**Aggregate:** ~2,615 test functions across ~138 test files under `tests/hydrodynamics/` plus ~88 adjacent.

---

## 8. Recommended R6 Follow-ups (additive to preliminary §6)

1. **Decide which surface owns wave spectra** — `orcawave/wave_spectrum.py` (typed pydantic, no Hs-renorm, has Ochi-Hubble/Torsethaugen) vs. `hydrodynamics/wave_spectra.py` (class-based, Hs-renorm, simpler). Pick one canonical, deprecate the other or wire it as a façade.
2. **Reconcile the four natural-period paths** — closed-form, BEM-iteration, AQWA-LIS-readback, AQWA-damping-fit. At minimum, document which one is authoritative per use case.
3. **Promote calc-citation manifests** — `parametric_hull_analysis/manifest.yaml` and `capytaine/manifest.yaml` already exist. Extend the same machine-readable manifest pattern to `wave_spectra.py`, `seakeeping.py`, `ocimf_loading.py`, and `diffraction/output_validator.py` (so resonance amp limits become traceable to a DNV/ISO clause or are explicitly marked convention-only).
4. **Author a vessel-class motion-criteria library** to close GAP G3 — DOF-keyed thresholds per vessel class (FPSO, drillship, semi, OSV, heavy-lift), wired into `operability_analysis(...)`.
5. **Author a resonance safety-margin checker** to close GAP G1 — combines `compute_natural_periods(...)` with sea-state `T_p` and emits a margin + risk-zone classification (e.g., DNV-RP-C205 §3.5 narrow-band guidance).
6. **Decide pipelay domain ownership** (GAP G4) — the implementation in `orcaflex/pipelay_analysis.py` was missed by the preliminary inventory; either fold pipelay into the hydrodynamics audit or spawn a separate Marine Operations sweep.
7. **Decide propeller-rudder domain ownership** — move to a future `propulsion/` package or keep co-located.
8. **Treat `diffraction/` as its own audit lane** if it stays under hydrodynamics — 60 modules and 1,365 tests is too large for a single R6 reconciliation pass.

---

**End of extended inventory. Awaiting R1 (Standards) + R2 (Academic) before promoting to final R5 deliverable.**
