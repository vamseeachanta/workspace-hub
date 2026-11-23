# Offshore Hydrodynamics — Code Coverage Preliminary Inventory (R5)

**Issue:** [#2673](https://github.com/vamseeachanta/workspace-hub/issues/2673) (R5 Code Audit, parent [#2668](https://github.com/vamseeachanta/workspace-hub/issues/2668) — Domain Sweep: Offshore Hydrodynamics)
**Date:** 2026-05-12
**Audit author:** R5 subagent (Account 1)
**Scope:** Preliminary inventory of hydrodynamics-related modules in `digitalmodel`. Full audit (gaps, severity, standards-cross-check) deferred until R1 (Standards) and R2 (Academic) complete.

> **Status note:** All rows below carry `PRELIMINARY — pending R1/R2 validation`. The standards references column is captured verbatim from module docstrings; R1 will validate that the cited code IDs are current, in-print, and match the published revision frontmatter under `knowledge/wikis/*/standards/`. R2 will validate that textbook citations (PNA, Journée & Massie, Blevins, Todd, McCauley) point to defensible editions.

---

## 1. Inventory Table

| Component | Module Path | Standards / References (docstring) | Tests | Status |
|---|---|---|---|---|
| OrcaWave package facade | `digitalmodel/src/digitalmodel/orcawave/__init__.py` | (re-exports below) | n/a | PRELIMINARY — pending R1/R2 validation |
| RAO I/O, interpolation, multi-body combination, comparison | `digitalmodel/src/digitalmodel/orcawave/rao_processing.py` | (none in docstring; relies on caller-supplied tables) | 12 (`tests/orcawave/test_rao_processing.py`) | PRELIMINARY — pending R1/R2 validation |
| Added-mass / damping / excitation; WAMIT format conversion; hydrostatic restoring | `digitalmodel/src/digitalmodel/orcawave/hydro_coefficients.py` | WAMIT, AQWA, Nemoh format mentions (no formal code refs) | 10 (`tests/orcawave/test_hydro_coefficients.py`) | PRELIMINARY — pending R1/R2 validation |
| WAMIT GDF panel mesh I/O, quality metrics, waterplane / displaced volume | `digitalmodel/src/digitalmodel/orcawave/panel_mesh.py` | WAMIT GDF format (no formal code refs) | 11 (`tests/orcawave/test_panel_mesh.py`) | PRELIMINARY — pending R1/R2 validation |
| Wave spectra (JONSWAP, PM, Bretschneider, ISSC, Ochi-Hubble, Torsethaugen), spectral moments | `digitalmodel/src/digitalmodel/orcawave/wave_spectrum.py` | None inline; rao-hydrodynamics-mapping.md cites DNV-RP-H103 for spectral integration | 14 (`tests/orcawave/test_wave_spectrum.py`) | PRELIMINARY — pending R1/R2 validation |
| Response spectrum, short/long-term motion statistics, MSI | `digitalmodel/src/digitalmodel/orcawave/motion_statistics.py` | ISO 2631-1 (MSI); McCauley et al. (1976) | 13 (`tests/orcawave/test_motion_statistics.py`) | PRELIMINARY — pending R1/R2 validation |
| Mean / slowly-varying drift force, Newman approximation, full QTF, wind/current drift | `digitalmodel/src/digitalmodel/orcawave/drift_forces.py` | Newman (no formal code refs in docstring) | 11 (`tests/orcawave/test_drift_forces.py`) | PRELIMINARY — pending R1/R2 validation |
| Vessel database (FPSO/semi/drillship/barge/LNGC), parametric hull, representative RAOs | `digitalmodel/src/digitalmodel/orcawave/vessel_database.py` | None inline | 14 (`tests/orcawave/test_vessel_database.py`) | PRELIMINARY — pending R1/R2 validation |
| Natural periods (heave/roll/pitch), encounter frequency, simple heave RAO, MSI, significant motion | `digitalmodel/src/digitalmodel/naval_architecture/seakeeping.py` | PNA Vol III; USNA EN400 Ch.8; Journée & Massie; O'Hanlon & McCauley | 15 (`tests/naval_architecture/test_seakeeping.py`) | PRELIMINARY — pending R1/R2 validation |
| Hull form coefficients (Cb, Cp, Cm, Cwp), Froude, Series 60 regression, wetted-surface (Denny-Mumford), drilling-rig hull validation | `digitalmodel/src/digitalmodel/naval_architecture/hull_form.py` | USNA EN400 Ch.2; PNA Vol I; Todd Series 60 (DTMB 1712) | 19 (`tests/naval_architecture/test_hull_form.py`) | PRELIMINARY — pending R1/R2 validation |
| Crane-tip motion from vessel RAO, DAF, sling tension, splash-zone loads, weight management | `digitalmodel/src/digitalmodel/orcaflex/installation_analysis.py` | DNV-RP-H103 (now DNV-RP-N103) §4–§6; DNV-OS-H101 / DNV-ST-N001; API RP 2A-WSD; Noble Denton 0027/ND §7 | 17 (`tests/orcaflex/test_installation_analysis.py`) | PRELIMINARY — pending R1/R2 validation |
| VIV screening — Strouhal/Reynolds, reduced velocity, beam natural frequencies, response amplitude | `digitalmodel/src/digitalmodel/orcaflex/viv_screening.py` | DNV-RP-C205 (2019) §9 Tab.9-1 Fig.9-3; DNV-RP-F105 (2017) §4 Eq.4.3 §5; Blevins (1990) Tab.7-2 | 17 (`tests/orcaflex/test_viv_screening.py`) | PRELIMINARY — pending R1/R2 validation. Boundary with Domain 4 (VIV/Riser) — coordinate categorisation with R6. |

**Modules audited:** 12 (8 orcawave including `__init__`, 2 naval_architecture, 2 orcaflex)
**Total scoped tests:** 153 test functions across 11 test files (excluding the `__init__.py` facade)

---

## 2. Public API Signatures

### `orcawave/rao_processing.py`
- `class RAOEntry(BaseModel)` / `class RAOTable(BaseModel)` / `class RAOComparisonResult(BaseModel)`
- `amplitude_phase_to_complex(...)`, `complex_to_amplitude_phase(...)`
- `read_rao_csv(text)`, `rao_table_to_csv(table)`
- `interpolate_rao(...)`, `combine_raos_multi_body(...)`, `compare_raos(...)`

### `orcawave/hydro_coefficients.py`
- `HydroMatrix6x6`, `ExcitationForceVector`, `HydroCoefficients` (pydantic)
- `interpolate_matrix_at_frequency(...)`, `interpolate_excitation_at_frequency(...)`
- `to_wamit_added_mass`, `to_wamit_damping`, `from_wamit_added_mass`
- `create_hydrostatic_restoring(...)`

### `orcawave/panel_mesh.py`
- `PanelQuad`, `MeshQualityMetrics`, `MeshSummary`, `GDFMesh`
- `read_gdf(text)`, `write_gdf(mesh)`
- `compute_panel_quality(...)`, `compute_mesh_summary(...)`
- `compute_waterplane_area(...)`, `compute_displaced_volume(...)`

### `orcawave/wave_spectrum.py`
- `SpectrumParameters`, `SpectrumResult`, `SpectralMoments`
- `compute_spectral_moments(...)`, `spectral_periods(moments)`
- `pierson_moskowitz(...)`, `jonswap(...)`, `bretschneider(...)`, `issc_spectrum(...)`, `ochi_hubble(...)`, `torsethaugen(...)`
- `generate_spectrum(params)` (dispatcher)

### `orcawave/motion_statistics.py`
- `ResponseSpectrum`, `ShortTermStatistics`, `ScatterCell`, `LongTermResult`, `MSIResult`
- `compute_response_spectrum(...)`, `short_term_statistics(...)`
- `rayleigh_exceedance(...)`, `rayleigh_quantile(...)`
- `long_term_extreme(...)`, `motion_sickness_incidence(...)`

### `orcawave/drift_forces.py`
- `MeanDriftCoefficients`, `QTFMatrix`, `DriftForceResult`, `WindCurrentDrift`
- `compute_mean_drift_force(...)`, `newman_approximation(...)`
- `full_qtf_slowly_varying(...)`, `compute_wind_current_drift(...)`

### `orcawave/vessel_database.py`
- `VesselParameters`, `VesselRAOSet`, `ParametricHull`
- `list_vessels()`, `get_vessel(name)`, `get_vessels_by_type(vessel_type)`
- `get_representative_raos(vessel_type)`, `generate_parametric_hull(...)`

### `naval_architecture/seakeeping.py`
- `natural_roll_period(...)`, `natural_heave_period(...)`, `natural_pitch_period(...)`
- `encounter_frequency(...)`
- `simple_heave_rao(...)`
- `motion_sickness_incidence(...)`, `significant_motion(...)`

### `naval_architecture/hull_form.py`
- `class RigHullEstimate` / `class RigHullValidation` (dataclasses)
- `rig_type_to_hull_form(...)`, `estimate_rig_hull_dimensions(...)`, `classify_rig_hull_geometry(...)`
- `validate_drilling_rig_hull_form(...)`, `validate_drilling_rig_fleet(...)`, `summarize_drilling_rig_hull_validation(...)`
- Form-coefficient suite: `block_coefficient(...)`, `prismatic_coefficient(...)`, `midship_coefficient(...)`, `waterplane_coefficient(...)`, `displacement_from_cb(...)`, `froude_number(...)`, `wetted_surface_denny_mumford(...)`, `series_60_cr(...)`, `lcb_from_cb(...)`

### `orcaflex/installation_analysis.py`
- `VesselType(str, Enum)`, `LiftPhase(str, Enum)`
- `class VesselRAO(BaseModel)` with `crane_tip_heave(hs)`, `crane_tip_velocity(hs, tp)`
- `class DAFInput(BaseModel)` with `natural_period`, `calculate_daf(wave_period=10.0)`
- `class SlingConfig(BaseModel)` with `calculate_sling_tension(hook_load_kN)`
- `class SplashZoneInput(BaseModel)` with `calculate_splash_zone_loads()`
- `class WeightItem`, `class WeightManagement` with `total_dry_weight`, `total_submerged_weight`, `total_with_contingency`, `calculate_cog`, `generate_summary`

### `orcaflex/viv_screening.py`
- `VIVDirection(str, Enum)`, `BoundaryCondition(str, Enum)`
- `strouhal_number(reynolds)`
- `class VIVScreeningInput(BaseModel)` with `reynolds_number`, `st`, `vortex_shedding_frequency`, `stability_parameter`, `check_reduced_velocity(natural_freq)`
- `class BeamProperties(BaseModel)` with `moment_of_inertia`, `bending_stiffness`, `boundary_constants`, `natural_frequency(mode=1)`, `natural_frequencies(n_modes=5)`
- `class VIVScreeningResult(BaseModel)`
- `viv_screening(...)`, `estimate_response_amplitude(...)`

---

## 3. Standards Coverage Snapshot

Codes cited in module docstrings (verbatim — R1 to validate revision currency):

| Code ID | Cited In | Use |
|---|---|---|
| DNV-RP-H103 (now DNV-RP-N103) §4–§6 | `installation_analysis.py` | Crane-tip motion, DAF, splash-zone loads |
| DNV-OS-H101 / DNV-ST-N001 | `installation_analysis.py` | Marine operations general |
| API RP 2A-WSD | `installation_analysis.py` | Fixed-platform planning |
| Noble Denton 0027/ND §7 | `installation_analysis.py` | Marine lifting/lowering |
| DNV-RP-C205 (2019) §9 Tab.9-1 Fig.9-3 | `viv_screening.py` | VIV environmental loads |
| DNV-RP-F105 (2017) §4 Eq.4.3 §5 | `viv_screening.py` | Free-spanning pipeline VIV |
| ISO 2631-1 (Annex D) | `motion_statistics.py` | Motion sickness incidence |
| PNA Vol I | `hull_form.py` | Hull form coefficients |
| PNA Vol III | `seakeeping.py` | Motions in waves |
| USNA EN400 Ch.2 / Ch.8 | `hull_form.py`, `seakeeping.py` | Hull geometry, seakeeping |
| Journée & Massie | `seakeeping.py` | Offshore hydromechanics |
| Todd Series 60 (DTMB Report 1712) | `hull_form.py` | Resistance regression |
| Blevins (1990) Tab.7-2 | `viv_screening.py` | Flow-induced vibration |
| McCauley et al. (1976) / O'Hanlon & McCauley | `motion_statistics.py`, `seakeeping.py` | MSI formula |
| Newman (no edition cited) | `drift_forces.py` | QTF approximation |

**R1 must verify:** revision currency (DNV-RP-H103 → -N103 rename completeness in code; DNV-RP-C205 and -F105 latest revisions vs cited 2019/2017); Noble Denton 0027/ND revision; API RP 2A-WSD edition.

**R2 must source:** Newman edition (likely *Marine Hydrodynamics* 1977 — to be confirmed); McCauley vs O'Hanlon-McCauley citation reconciliation; PNA edition (Lewis 1989).

---

## 4. Surprises / Findings to Flag

### Surprise 1: A third RAO/seakeeping/spectrum surface exists outside R5 scope
`digitalmodel/src/digitalmodel/hydrodynamics/` is a sibling package to `orcawave/` and contains `seakeeping.py`, `wave_spectra.py`, `rao_analysis/`, `aqwa/`, `bemrosetta/`, `capytaine/`, `diffraction/`, `hull_library/`, `passing_ship/`, `planing_hull/`. The R5 issue scoped only `orcawave/`, `naval_architecture/seakeeping.py + hull_form.py`, and two `orcaflex/` files. **The `digitalmodel.hydrodynamics` package — which appears to be the larger and more recent surface (40+ test files under `tests/hydrodynamics/`) — is therefore NOT in the inventory above.** R6 should explicitly decide whether to:
- (a) treat `hydrodynamics/` as a separate-but-related audit (defer to next iteration), or
- (b) widen R5 scope retroactively before declaring the domain audit complete.
The risk of (a): `naval_architecture/seakeeping.py` (in scope) defines `motion_sickness_incidence` and `simple_heave_rao` while `hydrodynamics/seakeeping.py` (out of scope) defines `motion_exceedance`, `operability_analysis`, `significant_amplitude`, `spectral_moments`, `compute_response_spectrum` — strong functional overlap that may indicate parallel/competing implementations.

### Surprise 2: DAF wave_period default is hard-coded
`installation_analysis.py:132` — `DAFInput.calculate_daf(self, wave_period: float = 10.0)`. A 10-second default wave period is silently used if the caller omits the argument. Per the calc-citation-contract rule, this is a convention-only numeric (not standards-derived) but is operationally load-bearing for crane-lift go/no-go decisions. R6 should flag this for a follow-up: either require explicit `wave_period` or cite the convention.

### Surprise 3: `naval_architecture/hull_form.py` is a mixed surface
The module name and EN400/PNA citations suggest pure form-coefficient utility, but ~120 lines (`RigHullEstimate`, `validate_drilling_rig_hull_form`, `validate_drilling_rig_fleet`, `_matched_hull_family`) implement **drilling-rig fleet validation logic** — domain-specific business code unrelated to hull-form geometry textbook references. This is a candidate for split (geometry vs rig-fleet-rules) and may explain why test count (19) is high vs. line count (366). R6 should decide whether to keep co-located or extract.

### Boundary note: VIV
`orcaflex/viv_screening.py` is listed as "boundary with Domain 4 (VIV/Riser Dynamics)" in the issue. The module's standards depth (DNV-RP-C205, DNV-RP-F105, Blevins) and 332-line scope argue for moving it wholesale into the VIV domain when Domain 4 is launched — keeping a re-export shim in `orcaflex/` if any callers depend on the path.

---

## 5. Test File Index (scoped modules only)

| Module | Test path | Test count |
|---|---|---|
| orcawave/drift_forces.py | tests/orcawave/test_drift_forces.py | 11 |
| orcawave/hydro_coefficients.py | tests/orcawave/test_hydro_coefficients.py | 10 |
| orcawave/motion_statistics.py | tests/orcawave/test_motion_statistics.py | 13 |
| orcawave/panel_mesh.py | tests/orcawave/test_panel_mesh.py | 11 |
| orcawave/rao_processing.py | tests/orcawave/test_rao_processing.py | 12 |
| orcawave/vessel_database.py | tests/orcawave/test_vessel_database.py | 14 |
| orcawave/wave_spectrum.py | tests/orcawave/test_wave_spectrum.py | 14 |
| naval_architecture/seakeeping.py | tests/naval_architecture/test_seakeeping.py | 15 |
| naval_architecture/hull_form.py | tests/naval_architecture/test_hull_form.py | 19 |
| orcaflex/installation_analysis.py | tests/orcaflex/test_installation_analysis.py | 17 |
| orcaflex/viv_screening.py | tests/orcaflex/test_viv_screening.py | 17 |

Additional adjacent test directories observed (out of R5 scope, surfaced for R6):
- `tests/hydrodynamics/` (aqwa, bemrosetta, capytaine, diffraction, hull_library, parametric_hull_analysis, passing_ship, rao_analysis) — ~100+ test files
- `tests/marine_ops/installation/` and `tests/marine_ops/marine_engineering/` — RAO integration + crane-tip motion + go/no-go
- `tests/unit/hydrodynamics/` — planing_hull, rao_analysis, wave_spectra_extended

---

## 6. Recommended R6 follow-ups

1. **Decide scope for `digitalmodel.hydrodynamics` package** — fold into this audit or spawn separate sweep.
2. **Reconcile the two `motion_sickness_incidence` implementations** (orcawave/motion_statistics.py vs naval_architecture/seakeeping.py) — confirm whether one is a thin wrapper or a parallel implementation drift.
3. **Add citations sidecar** for standards-derived constants per `.claude/rules/calc-citation-contract.md`: DNV-RP-H103 section refs in `installation_analysis.py`, DNV-RP-C205/F105 in `viv_screening.py`, ISO 2631-1 in `motion_statistics.py`.
4. **Coordinate VIV module hand-off** with Domain 4 (VIV/Riser Dynamics) launch sequencing.
5. **Validate DAF default `wave_period=10.0`** — convention citation or require explicit arg.

---

**End of preliminary inventory. Awaiting R1 (Standards) + R2 (Academic) before promoting to final R5 deliverable.**
