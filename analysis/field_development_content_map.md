# Field Development Content Map
# Generated: 2026-04-04
# Scope: workspace-hub + digitalmodel + worldenergydata + aceengineer-website

## SUMMARY

The field development ecosystem spans FOUR repos with a clear split:
- **Code modules** (implemented, tested): Schematics, production engineering, subsea engineering, reservoir, economics
- **Reference data** (catalog/docs): 6 real-world field case studies, FEED org charts, data source coverage maps
- **Web calculators** (deployed): NPV/IRR/MIRR calculator with JS engine on aceengineer.com
- **Planning/gaps** (documented but not yet coded): Concept selection, hub-vs-standalone, wet/dry tree, facility sizing, production profiles, DCA

---

## 1. CODE MODULES (Implemented)

### 1.1 digitalmodel/src/digitalmodel/field_development/ (11 .py files, 3 classes, 18 functions)
**Purpose**: Field layout schematic generation (SVG/PNG)
**Key files**:
- `schematic_generator.py` — Top-level API: generate_field_schematic(config) -> output_path
  - Routes to correct schematic class by development_type
  - Supports: subsea_tieback, platform, fpso_spread
  - Example config: SOLVEIG_PHASE2_CONFIG (120m WD, 3 templates, 4 wells, FPSO host)
- `schematics/subsea_tieback.py` — SubseaTiebackSchematic: side-view with templates, flowlines, host
- `schematics/fpso_spread.py` — FpsoSpreadSchematic: FPSO + spread mooring + SPS
- `schematics/platform_standalone.py` — PlatformSchematic: jacket/fixed + conductors + satellite wells
- `schematics/renderer.py` — Common SVG/PNG save logic
- `schematics/elements/icons.py` — Patch factories (FPSO, platform, template, well symbols)
- `schematics/elements/annotations.py` — Scale bar, depth label, north arrow
- `schematics/elements/seabed.py` — Seabed line + water column depth computation
**Tests**: tests/field_development/test_field_development.py (184 lines), tests/test_field_development_schematic.py

### 1.2 digitalmodel/src/digitalmodel/production_engineering/ (8 .py files)
**Purpose**: Well performance analysis — IPR, VLP, Nodal Analysis
**Key files**:
- `ipr_models.py` — 4 IPR models: LinearIpr, VogelIpr, FetkovichIpr, CompositeIpr
  - flow_rate(pwf_psi) -> q (bopd); flowing_pressure(q) -> Pwf (psi)
- `vlp_correlations.py` — Hagedorn-Brown (1965), Beggs-Brill (1973) VLP correlations
  - P_wf = P_wh + ΔP_hydrostatic + ΔP_friction
  - TubingConfig, FluidProperties, FlowConditions data structures
- `nodal_solver.py` — Finds IPR/VLP intersection (operating point) with confidence bounds
  - Green/Amber/Red quality score -> ±5%/15%/30% uncertainty bands
- `gigo_detector.py` — Garbage-in-garbage-out input validation
- `nonlinearity_flags.py` — Flags nonlinear well behavior
- `reconciliation_workflow.py` — Production data reconciliation
- `test_quality_scorer.py` — Well test quality scoring

### 1.3 digitalmodel/src/digitalmodel/subsea/ (70+ .py files)
**Purpose**: Subsea engineering calculations
**Submodules**:
- `pipeline/` — Pipe sizing, pressure containment (DNV), lateral/upheaval/thermal buckling, free span VIV (DNV-RP-F105), on-bottom stability, pressure loss, API RP 1111 installation
  - `pipe_sizing.py` — PipeSizing class with section/system properties
  - `pipeline_pressure_dnv.py` — DNV pressure containment
  - `lateral_buckling.py`, `thermal_buckling.py`, `upheaval_buckling.py`
  - `free_span/` — 7 modules: span allowable length, natural frequency, fatigue damage, VIV response, onset screening, wave velocity, Weibull current
  - `pressure_loss.py` — Flowline pressure drop
- `catenary_riser/` — Catenary equations, lazy wave, effective weight, simple catenary
- `mooring_analysis/` — Catenary mooring, designer, OrcaFlex generator
- `viv_analysis/` — VIV screening, fatigue, frequency calculator, vortex shedding, tubular members
- `vertical_riser/` — Riser stack-up components
- `on_bottom_stability/` — DNV-RP-F109

### 1.4 digitalmodel/src/digitalmodel/reservoir/ (2 .py files)
**Purpose**: Petrophysical analysis
- `stratigraphic.py` — Multi-well cross-section plotting (GR, RT, RHOB/NPHI, facies tracks)

### 1.5 digitalmodel/src/digitalmodel/marine_ops/reservoir/ (5 .py files)
**Purpose**: Reservoir modeling and production forecasting
- `modeling.py` — ReservoirModel with depletion simulation, recovery_factor calculation
  - ProductionForecast class with Arps decline curve analysis (exponential, hyperbolic, harmonic)
- `properties.py` — PVT properties, irreducible water saturation
- `analysis.py` — Reservoir analysis workflows

### 1.6 digitalmodel/src/digitalmodel/well/ (7 .py files)
**Purpose**: Well engineering
- `drilling/hydraulics.py` — Drilling hydraulics
- `drilling/rop_models.py` — Rate of penetration models
- `drilling/dysfunction_detector.py` — Drilling dysfunction detection
- `tubulars/design_envelope.py` — Tubular design envelope

### 1.7 worldenergydata/src/worldenergydata/economics/ (3 .py files)
**Purpose**: Field development economics — NPV, MIRR, carbon cost sensitivity
**Key files**:
- `dcf.py` — Core DCF engine
  - CashFlowSchedule dataclass (years, capex, revenue, opex, carbon_cost, emission_tco2)
  - calculate_npv() -> NPVResult (npv, discount_rate, net/discounted CFs)
  - calculate_mirr() -> MIRRResult (mirr, finance_rate, reinvestment_rate, PV/FV)
  - build_cash_flow_schedule() — assembles schedule from production profile
- `carbon.py` — Carbon cost sensitivity
  - carbon_npv_curve() — NPV sweep over carbon price range
  - breakeven_carbon_price() — Solve for NPV=0 carbon price
  - tornado_sensitivity() — Per-parameter swing analysis for tornado charts

### 1.8 worldenergydata/src/worldenergydata/sodir/npv_norway.py (604 lines)
**Purpose**: Norwegian petroleum fiscal regime NPV
- NorwegianFinancialParameters: petroleum tax (78%), corporate (22%), special (56%)
- Uplift rate (5.6% over 4 years), linear depreciation over 6 years
- Oil/gas price assumptions, working interest, net revenue interest

### 1.9 worldenergydata/src/worldenergydata/lower_tertiary/npv.py (219 lines)
**Purpose**: Lower Tertiary field-level NPV with FDAS lease mappings
- load_lease_mapping() — FDAS lease mapping with normalized lease numbers
- load_field_inputs() — Modular field configurations

### 1.10 worldenergydata/src/worldenergydata/drilling/batch_economics/economics.py (256 lines)
**Purpose**: Batch drilling economics
- BatchDrillingEconomics class
- Wright learning curve, mobilization amortization, batch vs standalone NPV, break-even well count

### 1.11 aceengineer-website/assets/js/npv-calculator-engine.js (279 lines)
**Purpose**: Client-side NPV calculator for aceengineer.com website
- calcDeclineProduction (exponential decline)
- calcAnnualRevenue (with royalty and price escalation)
- calcAnnualOpex (with escalation)
- calcNPV, calcIRR, calcMIRR, calcPayback
- buildYearlyCashflows
- Pure JS, no DOM deps, unit-testable

---

## 2. REFERENCE DATA & CATALOGS

### 2.1 Field Development Case Study Catalog (6 entries)
Location: digitalmodel/docs/domains/references/field_development/catalog/
Schema: catalog_schema.yaml (defines 20+ fields: id, name, operator, basin, water_depth, development_type, reserves, capex, npv_assumptions, etc.)
Index: catalog_index.yaml (with by_basin, by_development_type, by_field_type, by_operator lookups)

| Field | Basin | Type | WD(m) | CAPEX($B) | Reserves(MMboe) | Peak(kboe/d) |
|-------|-------|------|-------|-----------|-----------------|-------------|
| Solveig Phase 2 | NCS | subsea_tieback | 115 | 0.6 | 39 | - |
| Johan Sverdrup Ph1 | NCS | fixed_platform | 120 | 11.5 | 2700 | 535 |
| Mad Dog Phase 2 | GoM | semi_submersible | 1340 | 9.0 | 140 | 140 |
| Jack/St. Malo | GoM | SPAR | 2134 | 7.5 | 500 | 94 |
| Liza Phase 2 | Guyana | FPSO | 1650 | 6.0 | 600 | 220 |
| Vito | GoM | semi_submersible | 1219 | 1.7 | 300 | 100 |

### 2.2 FEED Organization Chart
- `feed.puml` — PlantUML WBS for FEED project structure
  - Workstreams: Wellhead Platform, SURF, Company Documentation, FPSO
  - FPSO team: Hull & Mooring, Naval Architect, Process, E&I, Topsides/Turret interface

### 2.3 Data Source Coverage Map
- `data-source-coverage.md` — Multi-basin data availability tracking
  - Done: BSEE (GoM)
  - Pending: NPD/Sodir (NCS), NSTA (UKCS), ANP (Brazil), EIA (US non-GoM), C-NLOER (Canada)
  - Watch list: Guyana, Suriname, Namibia, Falklands
  - Dead ends: Australia NOPTA, Angola ANPG, IEA MODS

### 2.4 Supporting Reference Docs
- `aker-bp-solveig-phase2-2026.md` — Detailed Solveig Phase 2 case study
- `development-value-drivers.jpg` — Field development value driver diagram
- `revive_old_wells.md` — Well revitalization process reference
- `minimum_facilities.md` — Minimum facilities concept (stub)

### 2.5 OrcaFlex Templates for Subsea Architecture
- `templates/umbilicals/umbilical_hybrid/` — Umbilical base model (800m WD), deep water (1200m) and steel tube variations
- `templates/pipelines/pipeline_hybrid/` — Pipeline base model (500m WD, 16" X65), 12" flowline case
- `templates/subsea/jumper_hybrid/` — Jumper base model
- `templates/platforms/tlp_hybrid/` — Mini TLP variation

### 2.6 Reservoir Analysis Example Config
- `examples/domains/input_files/reservoir_analysis/field_example_basic.yml`
  - Permian Basin unconventional shale well configuration
  - Log curves (GR, RHOB, NPHI, RT), stratigraphy, log analysis, volumetrics
  - Recovery factors: primary 8%, secondary 12%, enhanced 15%

### 2.7 Client Project FDAS Data (Historical)
- `client_projects/energy_fdas/` — Cascade/Chinook field development visualizations
  - Production profiles, well paths, east-north plots
- `client_projects/energy_bsee/` — BigFoot, Jack, St. Malo, Stones, Julia
  - Field development production & well plots

---

## 3. PLANNING & CAPABILITY GAPS (Documented but NOT Coded)

### 3.1 Capability Tiers (.planning/architecture/capability-tiers.yaml)
- worldenergydata key gaps:
  - WRK-317: Plotly Dash dashboard for BSEE/FDAS
  - WRK-318: Arps decline curve production forecasting module
  - WRK-319: Real-time EIA/IEA feed ingestion
  - WRK-321: MIRR/NPV with carbon cost sensitivity (partially implemented)
  - No field development screening capability
  - No cross-source synthesis layer
  - No unified query API

### 3.2 Pre-FEED Workflow (.planning/architecture/workflow-patterns.yaml)
- Pre-FEED feasibility assessment workflow defined:
  - Deepwater rigid pipeline system: wall thickness, collapse check, weather window
  - Produces pre-FEED calculation package
  - Referenced in agent-vision.md as autonomous agent workflow

### 3.3 NPV Calculator References (.planning/milestones/)
- npv-field-development calculator deployed on aceengineer.com
- Cross-repo dependency: worldenergydata economics <-> digitalmodel field_development
- WRK-080: NPV blog post, WRK-081: NPV calculator defaults

### 3.4 Skills Knowledge Graph (.planning/skills/skills-knowledge-graph.yaml)
- "Offshore field development economic analysis" listed as skill

---

## 4. CONTENT THAT DOES NOT EXIST AS CODE (Referenced but Unimplemented)

| Topic | Status | Where Referenced |
|-------|--------|------------------|
| Concept selection (FPSO vs TLP vs SPAR vs semi vs fixed) | NOT CODED — schematic routing only | schematic_generator.py routing logic |
| Hub vs standalone analysis | NOT CODED | catalog contains both patterns |
| Wet tree vs dry tree comparison | NOT CODED | Not found anywhere |
| Flowline routing optimization | NOT CODED | OrcaFlex pipeline templates exist |
| Umbilical sizing calculations | NOT CODED — templates only | OrcaFlex umbilical templates |
| Production profiles / plateau rates | PARTIAL — Arps decline in marine_ops | modeling.py ProductionForecast |
| Reserves estimation / volumetrics | PARTIAL — example config only | field_example_basic.yml |
| Recovery factors | PARTIAL — calculated in depletion model | modeling.py |
| Facility sizing | NOT CODED | minimum_facilities.md (stub) |
| Topsides design | NOT CODED — FEED org chart only | feed.puml |
| CAPEX breakdown models | NOT CODED — catalog has totals only | catalog entries |
| OPEX estimation | PARTIAL — opex arrays in DCF | dcf.py CashFlowSchedule |
| FDP (Field Development Plan) document generation | NOT CODED | Referenced in planning |
| Tieback distance optimization | NOT CODED — distance is input only | catalog_schema.yaml tieback_distance_km |
| DCA (Decline Curve Analysis) | PARTIAL — basic Arps in marine_ops | modeling.py arps_decline_analysis |
| Cross-basin field development screening | NOT CODED | capability-tiers.yaml key gap |

---

## 5. ARCHITECTURE SUMMARY

```
IMPLEMENTED CODE                           REFERENCE DATA / DOCS
==================                         =====================

digitalmodel/field_development/            catalog/ (6 field studies)
  - Schematic SVG/PNG generator             - Solveig, Sverdrup, Mad Dog
  - SubseaTieback, Platform, FPSO           - Jack/StMalo, Liza, Vito
  - Elements: icons, annotations, seabed    - Schema + index + lookups

digitalmodel/production_engineering/       feed.puml (FEED org chart)
  - IPR: Vogel, Fetkovich, Linear, Comp   data-source-coverage.md
  - VLP: Hagedorn-Brown, Beggs-Brill      development-value-drivers.jpg
  - Nodal analysis solver
  - Quality scoring

digitalmodel/subsea/                       OrcaFlex templates
  - Pipeline: sizing, pressure, buckling    - Flowline, umbilical, jumper, TLP
  - Free span: F105 VIV analysis
  - Catenary riser, mooring, VIV

worldenergydata/economics/                 aceengineer-website
  - DCF: NPV + MIRR                        - npv-field-development.html
  - Carbon cost sensitivity                 - npv-calculator-engine.js
  - Norwegian fiscal regime
  - Lower Tertiary NPV + FDAS

worldenergydata/drilling/batch_economics/  Client FDAS data (historical)
  - Learning curve, break-even              - Cascade/Chinook, BigFoot, Jack
```
