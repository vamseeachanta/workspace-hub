# Subsea Pipelines — Code Coverage Preliminary Inventory (R5)

**Issue:** [#2692](https://github.com/vamseeachanta/workspace-hub/issues/2692) (R5 Code Audit, parent [#2687](https://github.com/vamseeachanta/workspace-hub/issues/2687) — Domain Sweep: Subsea Pipelines)
**Date:** 2026-05-13
**Audit author:** R5 subagent
**Scope:** Preliminary inventory of subsea-pipeline-related modules in `digitalmodel` covering pipe sizing/wall-thickness, pressure containment, buckling (lateral / upheaval / thermal / propagation), on-bottom stability, free-spanning VIV/fatigue, pipelay installation, cathodic protection, and pipe cross-section + capacity. Full audit (gaps, severity, standards-cross-check) deferred until R1 (Standards) and R2 (Academic) complete.

> **Status note:** All rows below carry `PRELIMINARY — pending R1/R2 validation`. The standards references column is captured verbatim from module docstrings; R1 will validate that the cited code IDs are current, in-print, and match the published revision frontmatter under `knowledge/wikis/*/standards/`. R2 will validate that referenced textbooks (Bai & Bai 2014, Mousselli 1981) point to defensible editions.

> **Read-only audit:** no implementation changes made. Commit is deferred to the main session per R5 dispatch.

---

## 1. Inventory Table

### 1.1 Subsea Pipeline (`digitalmodel/subsea/pipeline/`)

| Component | Module Path | Standards / References (docstring) | Citation Emission | Tests | Status |
|---|---|---|---|---|---|
| Pipeline orchestrator / router (dispatches to LB/TB/UB/PL) | `digitalmodel/src/digitalmodel/subsea/pipeline/pipeline.py` | (none in docstring) | NONE | `tests/subsea/pipeline/test_pipeline.py` (1) | PRELIMINARY |
| Pipe sizing (OD/ID/WT derivation, section properties) | `digitalmodel/src/digitalmodel/subsea/pipeline/pipe_sizing.py` | (none in docstring) | NONE | (covered by engineering_validation/pipe_sizing/, 4 files) | PRELIMINARY |
| Pipeline pressure containment — DNV-ST-F101 + API RP 1111 (wall thickness, burst, MAOP, system pressure test) | `digitalmodel/src/digitalmodel/subsea/pipeline/pipeline_pressure.py` | DNV-ST-F101 (2021) Table 5-3, §5.2/5.3/5.4/5.6; API RP 1111 (2015) §4.3 | NONE — `GAMMA_SC`, `GAMMA_M`, `GAMMA_INC`, `ALPHA_U` are module-level constants with docstring citations but no `Citation` emission | `tests/subsea/pipeline/test_pipeline_pressure.py` (116) | PRELIMINARY — DNV constants ripe for citation pilot wiring (parallel to mooring case) |
| DNV-ST-F101 extended — collapse, propagating buckle, combined loading | `digitalmodel/src/digitalmodel/subsea/pipeline/pipeline_pressure_dnv.py` | DNV-ST-F101 §5.4.3 / §5.4.4 / §5.4.6 | NONE | (covered by `test_pipeline_pressure.py`) | PRELIMINARY |
| API RP 1111 internal pressure + combined loading + YAML wall-thickness sizing workflow | `digitalmodel/src/digitalmodel/subsea/pipeline/pipeline_pressure_workflow.py` | API RP 1111 §4.3.1 / §4.3.4 | NONE | (covered by `test_pipeline_pressure.py`) | PRELIMINARY |
| API RP 1111 S-lay installation bending strain (sagbend / overbend) | `digitalmodel/src/digitalmodel/subsea/pipeline/api_rp_1111_installation.py` | API RP 1111 (4th Ed., 2009) §6.2.1 | NONE | `tests/subsea/pipeline/test_api_rp_1111_installation.py` (7); `test_api_rp_1111.py` (9) | PRELIMINARY |
| Common buckling utilities (friction force, plotting glue) | `digitalmodel/src/digitalmodel/subsea/pipeline/buckling_common.py` | (none) | NONE | — | PRELIMINARY — used by LB/TB/UB |
| Lateral buckling analysis | `digitalmodel/src/digitalmodel/subsea/pipeline/lateral_buckling.py` | (none in docstring; method per Hobbs / Bai patterns implied) | NONE | `tests/subsea/pipeline/test_pipeline_lateral_buckling.py` (1) | PRELIMINARY — **only 1 test** vs. 332-line module |
| Thermal buckling analysis | `digitalmodel/src/digitalmodel/subsea/pipeline/thermal_buckling.py` | (none) | NONE | — (no dedicated test) | PRELIMINARY — **untested** |
| Upheaval buckling analysis | `digitalmodel/src/digitalmodel/subsea/pipeline/upheaval_buckling.py` | (none) | NONE | `tests/subsea/pipeline/test_pipeline_upheaval_buckling.py` (1) | PRELIMINARY |
| Pressure-loss / flow analysis (sympy-driven) | `digitalmodel/src/digitalmodel/subsea/pipeline/pressure_loss.py` | (none) | NONE | `tests/subsea/pipeline/test_pipeline_pressure_loss.py` (1) | PRELIMINARY |
| Free-span VIV fatigue (F105) — facade `FreespanVIVFatigue.assess()` | `digitalmodel/src/digitalmodel/subsea/pipeline/free_span/__init__.py` | DNV-RP-F105 (free-span VIV) | NONE | `tests/subsea/pipeline/test_free_span_f105.py` (41) | PRELIMINARY |
| Free-span natural frequency — F105 §6.8 (pinned/fixed/fixed-pinned C1, Ce IL/CF, Ca proximity correction) | `digitalmodel/src/digitalmodel/subsea/pipeline/free_span/span_natural_frequency.py` | DNV-RP-F105 §6.8 Eq. 6.8-1, Table 6-1, §6.8.2 Fig 6-3 | NONE | (covered above) | PRELIMINARY |
| Free-span data models (BoundaryConditionF105, EnvironmentType, PipeSpanInput, SpanVIVResult) | `digitalmodel/src/digitalmodel/subsea/pipeline/free_span/models.py` | DNV-RP-F105 | n/a | — | PRELIMINARY |
| Free-span bilinear S-N fallback (DNV-RP-C203 self-contained) | `digitalmodel/src/digitalmodel/subsea/pipeline/free_span/_bilinear_sn.py` | DNV-RP-C203 (2021) §2.4 Table 2-1 | NONE | — | PRELIMINARY — **duplicate of `digitalmodel.structural.fatigue` SN logic; on-purpose fallback (delegates when available)** |
| Pipe properties calculator (API STD 2RD section properties) | `digitalmodel/src/digitalmodel/subsea/pipeline/calculations/pipe_properties.py` | API STD 2RD | NONE | (covered by `tests/test_wall_thickness_api_std_2rd.py`) | PRELIMINARY |
| Stress calculations (API STD 2RD burst / collapse / utilisation) | `digitalmodel/src/digitalmodel/subsea/pipeline/calculations/stress_calculations.py` | API STD 2RD | NONE | (covered as above) | PRELIMINARY |

### 1.2 On-Bottom Stability

| Component | Module Path | Standards / References (docstring) | Citation Emission | Tests | Status |
|---|---|---|---|---|---|
| DNV-RP-F109 on-bottom stability (drag/lift/inertia, absolute + generalized stability) | `digitalmodel/src/digitalmodel/subsea/on_bottom_stability/dnv_rp_f109.py` | DNV-RP-F109 (Oct 2021) §4.3.1, §4.3.2, Tables 3-3 / 4-1 | NONE — `C_D`, `C_L`, `C_M`, `GAMMA_SC_NORMAL` are module-level constants | `tests/subsea/on_bottom_stability/test_dnv_rp_f109.py` (20) | PRELIMINARY |
| On-bottom stability — Morison-based simplified method (parallel impl in `geotechnical/`) | `digitalmodel/src/digitalmodel/geotechnical/on_bottom_stability.py` | DNV-RP-F109 | NONE | `tests/subsea/pipeline/test_on_bottom_stability.py` (16) + `tests/test_on_bottom_stability.py` (0) | PRELIMINARY — **DUPLICATE OBS implementation** (see §5 Finding 1) |

### 1.3 Pipelay / Installation (OrcaFlex namespace)

| Component | Module Path | Standards / References (docstring) | Citation Emission | Tests | Status |
|---|---|---|---|---|---|
| Pipelay pre-processing — S-lay/J-lay/Reel-lay geometry, stinger radius, overbend/sagbend stress, departure angle, lay rate vs sea state | `digitalmodel/src/digitalmodel/orcaflex/pipelay_analysis.py` | Bai & Bai (2014) Ch. 4-6; DNV-OS-F101; Mousselli (1981) | NONE | `tests/orcaflex/test_pipelay_analysis.py` (29) | PRELIMINARY |
| Installation analysis (crane-tip motion, DAF, sling, splash-zone) | `digitalmodel/src/digitalmodel/orcaflex/installation_analysis.py` | DNV-RP-H103/N103; DNV-OS-H101; API RP 2A-WSD; Noble Denton 0027/ND | NONE | `tests/orcaflex/test_installation_analysis.py` | PRELIMINARY — **also in Hydrodynamics R5 (#2673), boundary crossing** |
| OrcaFlex code-check engine (utilisation checks across DNV/API) | `digitalmodel/src/digitalmodel/orcaflex/code_check_engine.py` | (none surfaced) | NONE | `tests/orcaflex/test_code_check_engine.py` | PRELIMINARY — also boundary with Mooring R5 |
| Modular generator pipeline schema | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/pipeline.py` | n/a | n/a | (covered by `tests/solvers/orcaflex/modular_generator/`) | PRELIMINARY — config-only |
| Pipeline schematic renderer | `digitalmodel/src/digitalmodel/solvers/orcaflex/pipeline_schematic.py` | n/a | n/a | — | PRELIMINARY |
| Pipeline reporting renderer | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/pipeline.py` | n/a | n/a | — | PRELIMINARY |

### 1.4 Wall Thickness Design Codes (`structural/analysis/`)

| Component | Module Path | Standards / References (docstring) | Citation Emission | Tests | Status |
|---|---|---|---|---|---|
| Wall thickness analyser — dataclass + analyzer pattern (DesignCode/Geometry/Material/Loads/Factors/Result) | `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness.py` | DNV-ST-F101 (2021) §5 D401/D500/D600/D700; API RP 1111 (2015) §4.3 | NONE | `tests/test_wall_thickness.py` (58); `wall_thickness_codes/test_wall_thickness_core.py` (28) | PRELIMINARY |
| CodeStrategy Protocol + CODE_REGISTRY | `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/base.py` | n/a | n/a | `tests/test_wall_thickness_codes/test_code_registry.py` (6) | PRELIMINARY |
| DNV-ST-F101 strategy (edition-aware: 2007 OS-F101, 2021 ST-F101) | `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/dnv_st_f101.py` | DNV-ST-F101 (2021) / DNV-OS-F101 (2007/2010/2013); §5 D401/D500/D600/D700 | NONE | `wall_thickness_codes/test_dnv_st_f101.py` (20); `tests/test_wall_thickness_dnv_editions.py` (39) | PRELIMINARY |
| API RP 1111 strategy (edition-aware: 1999 3rd Ed, 2015 4th Ed) | `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/api_rp_1111.py` | API RP 1111 §4.3 (1999 / 2015) | NONE | `wall_thickness_codes/test_api_rp_1111.py` (14) | PRELIMINARY |
| API RP 2RD strategy | `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/api_rp_2rd.py` | API RP 2RD | NONE | `tests/test_wall_thickness_api_rp_2rd.py` (8) | PRELIMINARY |
| API STD 2RD strategy | `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/api_std_2rd.py` | API STD 2RD | NONE | `tests/test_wall_thickness_api_std_2rd.py` (9) | PRELIMINARY |
| ASME B31.4 strategy (liquid transport, F=0.72, Barlow burst) | `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/asme_b31_4.py` | ASME B31.4 (2019) S403.2.1/2/3 | NONE | `wall_thickness_codes/test_asme_b31_4.py` (7) | PRELIMINARY |
| ASME B31.8 strategy (gas transmission, Barlow + collapse + propagation) | `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/asme_b31_8.py` | ASME B31.8 | NONE | `test_wall_thickness_codes/test_asme_b31_8.py` (16) | PRELIMINARY |
| ISO 13623 strategy (pressure containment + elastic-plastic collapse + propagation) | `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/iso_13623.py` | ISO 13623 | NONE | `test_wall_thickness_codes/test_iso_13623.py` (16) | PRELIMINARY |
| PD 8010-2 strategy (UK offshore, single design factor) | `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/pd_8010_2.py` | PD 8010-2 | NONE | `test_wall_thickness_codes/test_pd_8010_2.py` (17) | PRELIMINARY |
| Wall thickness comparison (cross-code parametric) | `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_comparison.py` | (cross-code) | NONE | `tests/test_wall_thickness_comparison.py` (17); `test_wall_thickness_editions.py` (19) | PRELIMINARY |
| Wall thickness reporting / lookup / parametric / phases | `wall_thickness_lookup.py`, `wall_thickness_interactive_report.py`, `wall_thickness_mt_report.py`, `wall_thickness_parametric.py`, `wall_thickness_phases.py` | n/a | n/a | (18 + 16 + 21 + 23 + 45) | PRELIMINARY |

### 1.5 Pipe Cross-Section + Capacity (`structural/pipe_*`)

| Component | Module Path | Standards / References (docstring) | Citation Emission | Tests | Status |
|---|---|---|---|---|---|
| Multi-layer coated pipe cross-section (steel + LPP + concrete; weight, buoyancy, section properties) | `digitalmodel/src/digitalmodel/structural/pipe_cross_section/calculator.py` | DNV-ST-F101; API 5L; ISO 21809 (mentioned in module docstring; no inline §-refs) | NONE | `tests/structural/pipe_cross_section/test_pipe_calculator.py` (28) | PRELIMINARY |
| Pipe cross-section schema + visualization + CLI | `models.py`, `cli.py`, `visualization.py` | — | n/a | — | PRELIMINARY |
| Subsea cross-section schema (pydantic v2, Citation-friendly fields: `code_id`, `source_type`) | `digitalmodel/src/digitalmodel/subsea/cross_sections/schema.py` | Schema only — supports `wiki`/`standard`/`vendor_catalogue`/`project_assumption`/`calculation` | n/a (schema field) | `tests/subsea/cross_sections/test_schema.py` etc. (32) | PRELIMINARY — **schema is citation-aware but no module uses it for emission yet** |
| Pipe capacity orchestrator (router) | `digitalmodel/src/digitalmodel/structural/pipe_capacity/pipe_capacity.py` | n/a | n/a | — | PRELIMINARY |
| Pipe capacity (top-level PascalCase, modern entry) | `digitalmodel/src/digitalmodel/structural/pipe_capacity/PipeCapacity.py` | ASME B31, DNV-OS-F101 (via custom subpackage) | NONE | (covered by infrastructure/unit/test_pipe_capacity_codes.py — 7; test_pipe_capacity_dnv.py — 5) | PRELIMINARY — **DUPLICATE name vs `pipe_capacity.py` and `common/PipeCapacity.py`** |
| Pipe capacity common (subordinate copy) | `digitalmodel/src/digitalmodel/structural/pipe_capacity/common/PipeCapacity.py` | (same scope) | NONE | `tests/structural/pipe_capacity/test_pipe_capacity_common.py` (103) | PRELIMINARY — **third copy** |
| Pipe capacity custom DNVWallThickness | `digitalmodel/src/digitalmodel/structural/pipe_capacity/custom/PipeCapacity.py` | DNV-OS-F101, DNV-OS-F201 (parsed from code string) | NONE | `tests/structural/pipe_capacity/test_pipe_capacity_custom.py` (108) | PRELIMINARY — **fourth copy** |
| Asset-integrity custom PipeCapacity (yet another) | `digitalmodel/src/digitalmodel/asset_integrity/custom/PipeCapacity.py` | (same scope) | NONE | — | PRELIMINARY — **fifth copy** (see §5 Finding 2) |
| Pipeline integrity skill (hoop stress + FFS Level 1) | `digitalmodel/src/digitalmodel/asset_integrity/pipeline_skill.py` | API 5L PSL2 / ISO 3183 SMYS table; API 579-1 (via `rsf_calculations`) | NONE | `tests/asset_integrity/test_pipeline_skill.py` (29) | PRELIMINARY |
| API STD 2RD analyser (specialised) | `digitalmodel/src/digitalmodel/specialized/api_analysis/apistd2rd.py` | API STD 2RD | NONE | — | PRELIMINARY |

### 1.6 Cathodic Protection (`digitalmodel/cathodic_protection/` — 16 modules, all calc-relevant)

| Component | Module Path | Standards / References (docstring) | Citation Emission | Tests | Status |
|---|---|---|---|---|---|
| Package facade (re-exports 100+ symbols across 14 submodules) | `digitalmodel/src/digitalmodel/cathodic_protection/__init__.py` | (delegated) | n/a | — | PRELIMINARY |
| API RP 1632 — buried/USTs galvanic CP (anode driving voltage, Dwight resistance, anode life) | `cathodic_protection/api_rp_1632.py` | API RP 1632 (1996, 3rd Ed.) §4.2/§6.3/§6.4 | NONE | `tests/cathodic_protection/test_api_rp_1632.py` (16) | PRELIMINARY |
| ISO 15589-2 — offshore pipeline galvanic CP (T-dep current density, coating breakdown, pipeline demand, anode resistance, mass) | `cathodic_protection/iso_15589_2.py` | ISO 15589-2 (2004) §5.2/§8.4/§8.5, Table 1, Table 3 | NONE | `tests/cathodic_protection/test_iso_15589_2.py` (20) | PRELIMINARY |
| DNV-RP-B401 — offshore CP design (current demand, coating breakdown, anode mass / resistance / output, protected length) | `cathodic_protection/dnv_rp_b401.py` | DNV-RP-B401 (2005/2017) §5.4.1, §10.4, Table 10-1/10-6; DNV-RP-F103 | NONE | `tests/cathodic_protection/test_dnv_rp_b401_doc_verified.py` (36); `specialized/test_cathodic_protection_b401.py` (59); `test_sacrificial_anode_b401.py` (55) | PRELIMINARY — **largest test surface in the domain (150 tests)** |
| Pipeline CP (NACE SP0169 + ISO 15589-1 buried/submerged pipeline) | `cathodic_protection/pipeline_cp.py` | NACE SP0169 (2013); ISO 15589-1 (2015); NACE SP0502 | NONE | `test_pipeline_cp.py` (6); `test_pipeline_cp_design.py` (13) | PRELIMINARY |
| Marine structure CP (offshore platforms, jackets, monopiles — zone-based) | `cathodic_protection/marine_structure_cp.py` | DNV-RP-B401 (2017) §7; NACE SP0176; ISO 12473 (2006) | NONE | `test_marine_structure_cp.py` (5); `test_marine_cp.py` (11) | PRELIMINARY |
| Marine CP zone design (seawater current density by T + depth, calcareous deposit correction) | `cathodic_protection/marine_cp.py` | DNV-RP-B401 (2017) §7 Table 10-1, §10.4 | NONE | (covered above) | PRELIMINARY |
| ICCP design (rectifier sizing, anode bed deep-well / shallow, cable sizing) | `cathodic_protection/iccp_design.py` | NACE SP0169 §9; NACE TM0497; API RP 1632 §7 | NONE | `test_iccp_design.py` (6) | PRELIMINARY |
| Fuel system CP (impressed current for data-centre gen fuel piping) | `cathodic_protection/fuel_system_cp.py` | API RP 1632 (extended to ICCP) | NONE | `test_fuel_system_cp.py` (22) | PRELIMINARY — **non-subsea, but in the same package — keep an eye on scope creep** |
| Coating breakdown (3LPE, FBE, coal tar, concrete; initial / mean / final factors) | `cathodic_protection/coating.py` | DNV-RP-B401 (2017) §10.7 Tables 10-2 / 10-4; ISO 15589-2; NACE SP0169 | NONE | `test_coating.py` (6) | PRELIMINARY |
| Corrosion rate (de Waard-Milliams CO₂; Norsok M-506; galvanic; pitting) | `cathodic_protection/corrosion_rate.py` | de Waard & Milliams 1975; NORSOK M-506 (2005); NACE MR0175 / ISO 15156; DNV-RP-B101 | NONE | `test_corrosion_rate.py` (8) | PRELIMINARY |
| Anode sizing (stand-off / bracelet / flush; McCoy + Dwight resistance) | `cathodic_protection/anode_sizing.py` | DNV-RP-B401 (2017) §5-7, §10; DNV-RP-F103 (2016); McCoy 1974; Dwight 1936 | NONE | `test_anode_sizing.py` (15) | PRELIMINARY |
| Anode depletion tracking + remaining-life + inspection intervals | `cathodic_protection/anode_depletion.py` | DNV-RP-B401 (2017) §7.7 / §10.8; ISO 15589-2 §8.5; NACE SP0176 | NONE | `test_anode_depletion.py` (6) + `test_anode_depletion_new.py` (8) | PRELIMINARY — **shadow test pair** (`_new` suffix, both keep) |
| CP monitoring (reference electrodes, data logger, alarms) | `cathodic_protection/cp_monitoring.py` | NACE TM0497 (2018); DNV-RP-B401 §12; ISO 13174 (2012); NACE SP0169 §10 | NONE | `test_cp_monitoring.py` (7) | PRELIMINARY |
| CP survey (CIS / DCVG / ACVG potential mapping, attenuation curves) | `cathodic_protection/cp_survey.py` | NACE SP0207; NACE TM0497; NACE SP0502 | NONE | `test_cp_survey.py` (7) | PRELIMINARY |
| CP reporting (compliance, remaining life, recommendations) | `cathodic_protection/cp_reporting.py` | NACE SP0169; DNV-RP-B401 §12; API RP 1632 | NONE | `test_cp_reporting.py` (8) | PRELIMINARY |
| Stray current (AC/DC interference, drainage bonds, polarization cells) | `cathodic_protection/stray_current.py` | NACE SP0169 §9; EN 50162 (2004); EN 15280 (2013); ISO 18086 (2019) | NONE | `test_stray_current.py` (6) | PRELIMINARY |

### 1.7 Cathodic Protection — Parallel Implementations Elsewhere

| Component | Module Path | Standards / References | Notes |
|---|---|---|---|
| Router-based CP (config-driven `cfg["inputs"]["calculation_type"]`) | `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cathodic_protection.py` | DNV-RP-B401 2021; DNV-RP-F103 2010/2019; ABS Ships/Offshore 2018 | **Parallel CP implementation surface** — not deprecated; co-exists with `digitalmodel.cathodic_protection`. See §5 Finding 3. Tests: `specialized/cathodic_protection/test_dnv_pipeline_variants.py` (13); `test_dnv_pipeline_variants_wrk271.py` (10); `test_dnv_f103_2010_calcs.py` (13); `test_abs_offshore_2018.py` (8); `test_abs_ship_variants.py` (13); `test_abs_ship_variants_wrk271.py` (10) |
| B401-2021 fixed platform CP (current densities by zone+T, coating breakdown, anode resistance §3.3/3.4/4.9) | `infrastructure/base_solvers/hydrodynamics/cp_DNV_RP_B401_2021.py` | DNV-RP-B401 (May 2021) §3.3 Table 3-1, §3.4.6, §4.9 | Duplicates `cathodic_protection/dnv_rp_b401.py` for 2021 edition |
| DNV-RP-F103 (2010 + 2019 variants, router-dispatched) | `infrastructure/base_solvers/hydrodynamics/cp_DNV_RP_F103_2010.py` | DNV-RP-F103 (2010, 2019) | **Only 2010 explicit; 2019 is a method stub** |
| Sacrificial anode b401 standalone fns (Dwight + bracelet resistance) | `infrastructure/base_solvers/hydrodynamics/cp_sacrificial_anode_b401.py` | DNV-RP-B401 (all editions, core equations) | Standalone; parallel to `dnv_rp_b401.py` |
| ASTM G42 cathodic disbonding (elevated T, Arrhenius correction) | `infrastructure/base_solvers/hydrodynamics/cp_astm_g42.py` | ASTM G42 (1996) §10, §11 | Tests: `test_astm_g42.py` (19) |
| ASTM G80 cathodic disbonding (ambient T) | `infrastructure/base_solvers/hydrodynamics/cp_astm_g80.py` | ASTM G80 (1998) §10.1, §10.2 | Tests: `test_astm_g80.py` (19) |
| **Deprecation shim** (CathodicProtection moved → base_solvers/hydrodynamics) | `infrastructure/common/cathodic_protection.py` | n/a | Warns on import |

### 1.8 Adjacent / Boundary modules (included for completeness; partially in scope)

| Component | Module Path | Notes |
|---|---|---|
| Pipe properties (config-driven, used by Pipeline router) | `infrastructure/base_solvers/marine/pipe_properties.py` | Section + system + coating + buoyancy properties; assetutilities-backed |
| Pipeline validation framework (range / matrix / units / time series validators) | `infrastructure/validation/pipeline.py` | **Misleading name** — this is a *validation pipeline* (Validator framework), not a *subsea pipeline*. Confusing colocation. |
| Plate buckling — infrastructure consolidated module | `infrastructure/calculations/plate_buckling.py` | DNV-RP-C201 |
| Plate buckling — base_solvers structural pkg | `infrastructure/base_solvers/structural/plate_buckling.py`, `buckling/elastic_buckling.py` | Eigenvalue elastic buckling solver |
| Plate buckling — legacy stiffener buckling cal | `structural/plate_capacity/StiffnerBuckling_Cal/` (incl. Draft1/Draft2 versions, z_superseded/) | **3 versions on disk + z_superseded/ folder — see §5 Finding 4** |
| Code-check / VIV screening (boundary with VIV/Riser domain) | `orcaflex/code_check_engine.py`, `orcaflex/viv_screening.py` | Cross-domain — primarily Hydrodynamics R5 (#2673) |
| Subsea VIV analysis (legacy + current) | `subsea/viv_analysis/{viv_analysis.py, viv_analysis_legacy.py, viv_tubular_members.py, fatigue.py, cli.py}` | **Live + legacy file pair** |
| Catenary riser (subsea pkg) | `subsea/catenary_riser/{cli.py, models.py}` (plus `legacy/`) | Cross-domain with Mooring R5 |

---

**Modules audited:** **77 calc-relevant modules** across 7 packages:
- `subsea/pipeline/*` (17 files), `subsea/on_bottom_stability/` (2 files), `subsea/cross_sections/` (3 files), `subsea/viv_analysis/` (5 files), `subsea/catenary_riser/` (3 files)
- `cathodic_protection/*` (16 files, incl. facade)
- `structural/analysis/wall_thickness*` + `wall_thickness_codes/*` (11 files: core analyser + 8 code strategies + 2 reporting)
- `structural/pipe_capacity/{pipe_capacity, PipeCapacity, common/PipeCapacity, custom/PipeCapacity}` (5 files — **see Finding 2**)
- `structural/pipe_cross_section/` (4 files)
- `orcaflex/{pipelay_analysis, installation_analysis, code_check_engine}` (3 files)
- `geotechnical/{on_bottom_stability, anchors}` (2 files), `geotechnical/scour.py`
- `infrastructure/base_solvers/hydrodynamics/{cathodic_protection, cp_DNV_RP_B401_2021, cp_DNV_RP_F103_2010, cp_sacrificial_anode_b401, cp_astm_g42, cp_astm_g80}` (6 files) + deprecation shim (1)
- `asset_integrity/{pipeline_skill, custom/PipeCapacity}` (2 files), `specialized/api_analysis/apistd2rd.py` (1)

**Total scoped tests:** **109 test files**, **~1,730 test functions** (indented `def test_` count under `tests/{cathodic_protection, specialized/cathodic_protection, subsea/{pipeline, on_bottom_stability, cross_sections, viv_analysis, catenary_riser, mooring_analysis}, structural/{analysis/wall_thickness_codes, pipe_capacity, pipe_cross_section}, test_wall_thickness*, test_wall_thickness_codes/, test_on_bottom_stability, asset_integrity, infrastructure/unit/test_pipe_capacity*, engineering_validation/pipe_sizing, orcaflex/test_pipelay_analysis, marine_ops/marine_engineering/test_cathodic_protection_dnv, benchmarks/test_wall_thickness_benchmarks + test_cp_benchmarks}/`).

Highlight: cathodic protection alone contributes ~500 test functions (`test_cathodic_protection_b401.py` 59, `test_sacrificial_anode_b401.py` 55, `test_dnv_rp_b401_doc_verified.py` 36, `test_fuel_system_cp.py` 22, `test_iso_15589_2.py` 20, `test_anode_sizing.py` 15, `test_api_rp_1632.py` 16, plus 30+ smaller files).

---

## 2. Citation Contract Compliance Check

Per `.claude/rules/calc-citation-contract.md` (pilot reference is **mooring**, not pipelines — but the contract applies domain-wide once pilot lands).

**Findings for Subsea Pipelines:**

1. `grep -rn "from digitalmodel.citations\|import.*Citation" digitalmodel/src/digitalmodel/{subsea,cathodic_protection,geotechnical,structural,orcaflex,infrastructure}` returns **zero matches**. Not a single pipeline-domain module emits citations. The Subsea Pipelines surface is **larger** than Mooring (77 modules vs. ~20) and carries **more standards-derived constants** — DNV-ST-F101 safety class factors, DNV-RP-F109 hydrodynamic coefficients, DNV-RP-F105 boundary-condition constants C1, DNV-RP-B401 / API RP 1632 / ISO 15589-2 anode parameters, ASME B31.4/B31.8 design factors, API RP 1111 (1999 vs 2015 edition) factors.

2. The `subsea.cross_sections.schema` module (`schema.py`) defines a **citation-aware Pydantic schema** with `source_type` field accepting `wiki | standard | vendor_catalogue | project_assumption | calculation` — but it is currently **input metadata only**, not wired to emit `digitalmodel.citations.Citation` instances. This is a near-term opportunity for the citation rollout once the mooring pilot is fixed.

3. The DNV constants in `subsea/pipeline/pipeline_pressure.py` (`GAMMA_SC`, `GAMMA_M`, `GAMMA_INC`, `ALPHA_U`, `DF_COLLAPSE`) and `subsea/on_bottom_stability/dnv_rp_f109.py` (`C_D_*`, `C_L_*`, `C_M_*`, `GAMMA_SC_NORMAL`) are **structurally identical to the mooring `safety_factor_intact = 1.67` pattern** flagged in the mooring R5 deliverable (#2681). Same defect class, larger surface area.

**Recommendation (defer to R6 / main session):** when the mooring pilot is fixed (workspace-hub#2685), file a parallel citation rollout for pipelines starting with DNV-ST-F101 §5 Table 5-3 (`GAMMA_SC`) and DNV-RP-F109 Tables 3-3/4-1.

---

## 3. Standards Coverage Snapshot

Codes cited in module docstrings (verbatim — R1 to validate revision currency):

| Code ID | Cited In | Use |
|---|---|---|
| **DNV-ST-F101 (2021)** | `pipeline_pressure.py`, `pipeline_pressure_dnv.py`, `wall_thickness_codes/dnv_st_f101.py`, `pipe_cross_section/calculator.py`, `orcaflex/pipelay_analysis.py` | Wall thickness, burst, collapse, propagation, combined loading |
| **DNV-OS-F101 (2007/2010/2013)** | `wall_thickness_codes/dnv_st_f101.py` (edition-keyed) | Pre-2017 renumbering |
| **DNV-RP-F105** | `subsea/pipeline/free_span/{__init__,span_natural_frequency,models}.py`; `orcaflex/viv_screening.py` (Hydro R5) | Free-spanning pipeline VIV, fatigue, natural frequency |
| **DNV-RP-F109 (Oct 2021)** | `subsea/on_bottom_stability/dnv_rp_f109.py`; `geotechnical/on_bottom_stability.py` | On-bottom stability, absolute + generalized |
| **DNV-RP-F103 (2010 / 2016 / 2019)** | `anode_sizing.py`, `dnv_rp_b401.py`, `cp_DNV_RP_F103_2010.py` | CP of submarine pipelines |
| **DNV-RP-B401 (2017 / 2021)** | `cathodic_protection/{anode_sizing,coating,marine_cp,marine_structure_cp,anode_depletion,cp_monitoring,cp_reporting,dnv_rp_b401}.py`; `infrastructure/base_solvers/.../cp_DNV_RP_B401_2021.py`; `cp_sacrificial_anode_b401.py` | CP design (current density, coating breakdown, anode mass / resistance / output) |
| **DNV-RP-C203 (2021)** | `subsea/pipeline/free_span/_bilinear_sn.py` (fallback) | Bilinear S-N curve for free-span fatigue |
| **DNV-RP-B101** | `cathodic_protection/corrosion_rate.py` | Corrosion protection FPSO/FSU |
| **API RP 1111 (3rd Ed. 1999 / 4th Ed. 2015)** | `pipeline_pressure.py`, `pipeline_pressure_workflow.py`, `api_rp_1111_installation.py`, `wall_thickness_codes/api_rp_1111.py` | Burst, collapse, propagating buckle, S-lay strain limits |
| **API RP 1632 (1996, 3rd Ed.)** | `cathodic_protection/api_rp_1632.py`; `fuel_system_cp.py`; `iccp_design.py`; `cp_reporting.py` | Buried/UST galvanic + ICCP CP |
| **API STD 2RD** | `subsea/pipeline/calculations/{pipe_properties,stress_calculations}.py`; `specialized/api_analysis/apistd2rd.py`; `wall_thickness_codes/api_std_2rd.py` | High-collapse-resistance pipe |
| **API RP 2RD** | `wall_thickness_codes/api_rp_2rd.py` | Riser/pipeline design |
| **API 5L PSL2** | `asset_integrity/pipeline_skill.py` | SMYS material grade table (X52..X100) |
| **API 579-1** | `asset_integrity/pipeline_skill.py` (via `rsf_calculations`) | Fitness-for-Service Level 1 |
| **ASME B31.4 (2019)** | `wall_thickness_codes/asme_b31_4.py` | Liquid transportation pipeline (F=0.72) |
| **ASME B31.8** | `wall_thickness_codes/asme_b31_8.py` | Gas transmission pipeline |
| **ISO 13623** | `wall_thickness_codes/iso_13623.py` | International pipeline transportation |
| **ISO 15589-1 (2015) / -2 (2004)** | `cathodic_protection/{iso_15589_2,pipeline_cp}.py` | CP of on-land / offshore pipelines |
| **ISO 21809** | `structural/pipe_cross_section/calculator.py` (mentioned) | External coatings |
| **ISO 3183** | `asset_integrity/pipeline_skill.py` | Linepipe material |
| **PD 8010-2** | `wall_thickness_codes/pd_8010_2.py` | UK offshore pipeline |
| **NACE SP0169 (2013)** | `pipeline_cp.py`, `iccp_design.py`, `coating.py`, `cp_monitoring.py`, `cp_survey.py`, `cp_reporting.py`, `stray_current.py` | UG/submerged external corrosion |
| **NACE SP0176** | `marine_structure_cp.py`, `marine_cp.py`, `anode_depletion.py` | Submerged offshore steel |
| **NACE SP0207 / SP0502** | `cp_survey.py`, `pipeline_cp.py` | CIS/DCVG surveys |
| **NACE TM0497 (2018)** | `iccp_design.py`, `cp_monitoring.py`, `cp_survey.py` | CP measurement techniques |
| **NACE MR0175 / ISO 15156** | `corrosion_rate.py` | H₂S service |
| **NORSOK M-506 (2005)** | `corrosion_rate.py` | CO₂ corrosion rate |
| **ASTM G42 (1996) / G80 (1998)** | `cp_astm_g42.py`, `cp_astm_g80.py` | Cathodic disbonding tests |
| **EN 50162 (2004) / EN 15280 (2013)** | `stray_current.py` | DC/AC stray current |
| **ISO 12473 (2006), ISO 13174 (2012), ISO 18086 (2019)** | `marine_structure_cp.py`, `cp_monitoring.py`, `stray_current.py` | Seawater CP, port structures, AC corrosion |
| **ABS Guidance Notes (Ships 2018, Offshore 2018)** | `infrastructure/base_solvers/.../cathodic_protection.py` | CP design |
| **Bai & Bai (2014) — Subsea Pipeline Design** | `orcaflex/pipelay_analysis.py` | Pipelay Ch. 4-6 |
| **Mousselli (1981) — Offshore Pipeline Design** | `orcaflex/pipelay_analysis.py` | Pipelay reference |
| **McCoy (1974), Dwight (1936)** | `anode_sizing.py` | Anode resistance formulas |
| **de Waard & Milliams (1975)** | `corrosion_rate.py` | CO₂ corrosion |

**R1 must verify:** revision currency for DNV-ST-F101 (2021 vs latest), DNV-RP-F105 (2017 vs latest), DNV-RP-F109 (Oct 2021 vs latest), DNV-RP-B401 (2017 — 2021 edition coverage in `cp_DNV_RP_B401_2021.py` parallel impl), API RP 1111 (2015 4th vs latest), API RP 1632 (1996 — likely superseded), ISO 15589-2 (2004 — newer revision exists), ASME B31.4 (2019 currency vs latest), NACE SP0169 (2013 currency).

**R2 must source:** Bai & Bai 2014 edition (1st? 2nd?), Mousselli 1981 (out of print — alternative modern reference?), Faltinsen/Newman-style background for installation analysis.

---

## 4. Test Coverage Highlights & Gaps

**Strong coverage clusters (>20 tests each):**
- `tests/test_wall_thickness.py` (58), `test_wall_thickness_phases.py` (45), `test_wall_thickness_dnv_editions.py` (39), `test_wall_thickness_core.py` (28), `test_wall_thickness_parametric.py` (23), `test_wall_thickness_mt_report.py` (21), `test_wall_thickness_dnv_st_f101.py` (20), `test_wall_thickness_editions.py` (19), `test_wall_thickness_lookup.py` (18), `test_wall_thickness_comparison.py` (17), `test_wall_thickness_pd_8010_2.py` (17), `test_wall_thickness_interactive_report.py` (16), `test_wall_thickness_asme_b31_8.py` (16), `test_wall_thickness_iso_13623.py` (16), `test_api_rp_1111.py` (14) — **wall-thickness surface is very well exercised**
- `test_cathodic_protection_b401.py` (59), `test_sacrificial_anode_b401.py` (55), `test_dnv_rp_b401_doc_verified.py` (36), `test_fuel_system_cp.py` (22), `test_iso_15589_2.py` (20), `test_astm_g42.py` (19), `test_astm_g80.py` (19), `test_anode_sizing.py` (15) — **CP surface is very well exercised (>270 tests)**
- `test_pipeline_pressure.py` (116) — **deep coverage of DNV-ST-F101 pressure containment**
- `test_pipe_capacity_common.py` (103), `test_pipe_capacity_custom.py` (108) — **but covering duplicated implementations** (see Finding 2)
- `test_free_span_f105.py` (41) — DNV-RP-F105 well covered
- `test_pipeline_skill.py` (29), `test_pipe_calculator.py` (28) — solid integration coverage

**Gap clusters:**
- `thermal_buckling.py` — **0 dedicated tests** (only the orchestrator `test_pipeline.py` smoke test exercises it indirectly)
- `lateral_buckling.py` — **only 1 test** (`test_pipeline_lateral_buckling.py:1`) vs. multi-hundred-line module with Hobbs-style plotting code
- `upheaval_buckling.py` — **1 test** (smoke only)
- `pressure_loss.py` — **1 test** (smoke only)
- `subsea/pipeline/pipeline.py` orchestrator — **1 smoke test** with patched engine (does not exercise real routing)
- `orcaflex/code_check_engine.py` — **0 def test_** in `test_code_check_engine.py` (file exists but no scoped test functions found — verify with pytest collection in R6)
- `geotechnical/scour.py` — present but **no test file found**
- `subsea/cross_sections/` schema is well tested (32) but no code module **uses** the citation-aware fields yet

---

## 5. Critical Findings

### Finding 1 — HIGH — Duplicate on-bottom stability implementations
`digitalmodel/src/digitalmodel/subsea/on_bottom_stability/dnv_rp_f109.py` (273 lines, NamedTuple-based) and `digitalmodel/src/digitalmodel/geotechnical/on_bottom_stability.py` (dataclass-based) **both implement DNV-RP-F109 OBS** with overlapping API: `submerged_weight`, `drag_force_per_meter`, `lift_force_per_meter`, `inertia_force_per_meter`, `lateral_stability_check`. The tests live in **three** locations: `tests/subsea/on_bottom_stability/test_dnv_rp_f109.py` (20), `tests/subsea/pipeline/test_on_bottom_stability.py` (16), and `tests/test_on_bottom_stability.py` (0 — empty/dead). The two implementations use different dataclass shapes (`NamedTuple` vs `@dataclass`) and different default coefficients (e.g., `DEFAULT_CL = 0.9` vs `C_L_SMOOTH = 0.9` / `C_L_ROUGH = 1.0`). Reviewers cannot tell which is canonical. **Same pattern as the catenary-solver finding from Mooring R5 (#2681).**

### Finding 2 — HIGH — Five-way duplicate `PipeCapacity` class
Five separate files named `PipeCapacity.py` (case-sensitive) co-exist in src/:
1. `structural/pipe_capacity/PipeCapacity.py` — top-level
2. `structural/pipe_capacity/common/PipeCapacity.py` — "common"
3. `structural/pipe_capacity/custom/PipeCapacity.py` — "custom" w/ `DNVWallThickness`
4. `asset_integrity/custom/PipeCapacity.py` — fifth in different package
5. `structural/pipe_capacity/pipe_capacity.py` — snake-case orchestrator that imports from `common/pipe_components.PipeComponents` (a sixth name variant)
Tests cover only 2 of the 5 (`test_pipe_capacity_common.py` 103, `test_pipe_capacity_custom.py` 108). Imports inside the copies are inconsistent: one imports `common.update_deep`, another `digitalmodel.infrastructure.utils.update_deep`, another `assetutilities.common.update_deep` — at least two are unreachable from a fresh install. **Worse than the mooring catenary 5-variant case (which at least all sat in one directory).**

### Finding 3 — HIGH — Parallel cathodic protection surface (router-based vs functional)
Two independent CP implementations co-exist with no clear deprecation path:
- **Modern functional surface** at `digitalmodel/cathodic_protection/*` — 16 modules, ~135 public functions/classes, 270+ tests, citation-friendly docstring conventions. This is what the package `__init__.py` exports.
- **Router-based surface** at `digitalmodel/infrastructure/base_solvers/hydrodynamics/{cathodic_protection.py, cp_DNV_RP_B401_2021.py, cp_DNV_RP_F103_2010.py, cp_sacrificial_anode_b401.py}` — class-based router dispatching on `cfg["inputs"]["calculation_type"]`, 130+ tests under `tests/specialized/cathodic_protection/`.

Both implement DNV-RP-B401, with the router version explicitly carrying a **2021 edition file** and the functional version carrying a **2017** signature. The 2021 vs 2017 edition split is not coordinated. **`infrastructure/common/cathodic_protection.py` is a deprecation shim** pointing at the router version, which means the router version is being treated as canonical even though the functional package is what `cathodic_protection/__init__.py` exposes. This is contradictory and an active source of agent confusion. **The duplicate-edition shadow files mirror the catenary `_v2/_fixed/_final` pattern from Mooring R5 — same defect class, applied to edition tracking instead of file naming.**

### Finding 4 — MED — Legacy / shadow / superseded buckling code
`structural/plate_capacity/StiffnerBuckling_Cal/` contains `StiffnerBuckling_Cal(Draft1).py`, `StiffnerBuckling_Cal(Draft2).py`, `StiffnerBuckling_Cal.py`, **plus** `structural/plate_capacity/z_superseded/{Rev1.py, Rev2.py, parameters_Col_All.py}`. Parentheses in filenames cause shell-quoting fragility. Bracketed `legacy/` directories also exist at `subsea/{catenary_riser,vertical_riser}/legacy/` and `subsea/viv_analysis/viv_analysis_legacy.py`. These are **not pipeline-specific** but they shadow the same surface (`pipe_capacity`, `viv_analysis`) and would all need consolidation if a citation-emission rollout touches plate buckling. Plus shadow files at top level: `marine_analysis/aqwa_reader_fixed.py`, `solvers/orcaflex/{opp_time_series_v2.py, opp_summary_superseded.py, orcaflex_optimized_parallel_v2.py}`, `structural/fatigue_apps/load_scaling_efficient_v2.py`.

### Finding 5 — MED — Pipeline-engineering modules carry zero citation emission
Per §2 above: `grep -rn "from digitalmodel.citations\|import.*Citation" digitalmodel/src/digitalmodel/{subsea,cathodic_protection,geotechnical,structural,orcaflex,infrastructure}` returns **zero** matches. The Subsea Pipelines surface alone has ~30 standards-derived constants (DNV-ST-F101 GAMMA_SC, GAMMA_M, GAMMA_INC, ALPHA_U, DF_COLLAPSE; DNV-RP-F109 C_D/C_L/C_M for smooth/rough × GAMMA_SC_NORMAL; DNV-RP-F105 C1 × 3 boundary conditions × Ce_IL × Ce_CF; DNV-RP-B401 ANODE_CAPACITY_ALZNI/ZN/MG × UTILIZATION_FACTOR_STANDOFF/FLUSH/BRACELET; API RP 1111 design factors per edition; ASME B31.4/B31.8 F/E/T factors). Risk is the same as Mooring R5 §2 Finding: standards updates (e.g., DNV-RP-B401 2017→2021 edition migration, already partially landed in the parallel implementation) require coordinated edits in multiple locations with no test enforcing consistency. **Citation rollout for pipelines is contingent on mooring pilot fix (#2685) landing first.**

---

## 6. Follow-on Pointers (for R6 / main-session triage)

- File issue: "On-bottom stability — consolidate `subsea/on_bottom_stability/dnv_rp_f109.py` and `geotechnical/on_bottom_stability.py`; pick canonical, depreciate the other." Severity HIGH.
- File issue: "Five-way duplicate `PipeCapacity.py` — consolidate to single canonical class with strategy-pattern dispatch (mirrors `wall_thickness_codes/CODE_REGISTRY` which already works)." Severity HIGH.
- File issue: "Parallel cathodic protection surfaces — decide between functional package (`digitalmodel.cathodic_protection.*`) and router-based (`infrastructure.base_solvers.hydrodynamics.cathodic_protection.CathodicProtection`); reconcile 2017 vs 2021 DNV-RP-B401 edition tracking; remove deprecation shim's contradiction." Severity HIGH.
- File issue: "Pipeline buckling tests sparse — `thermal_buckling.py` has 0 dedicated tests; `lateral_buckling.py` and `upheaval_buckling.py` each have 1 smoke test; close the gap before any plan touches these modules." Severity MED.
- File issue: "Plan citation-emission rollout for Subsea Pipelines — DNV-ST-F101 GAMMA_SC + DNV-RP-F109 C_D/C_L/C_M as v1 targets; contingent on mooring pilot fix #2685." Severity MED.
- File issue: "Legacy file cleanup — `_v2/_fixed/_final/_legacy/_superseded/Draft1/Draft2/Rev1/Rev2/(Draft1).py` patterns across pipeline-adjacent code." Severity LOW.
- Update `.claude/rules/calc-citation-contract.md` to acknowledge pipeline domain is OUT of scope until mooring pilot lands (already covered, but worth a forward-link from this doc).

---

**End of preliminary inventory. Awaiting R1 (Standards) + R2 (Academic) before promoting to final R5 deliverable.**
