     1|# Field Development Content Map
     2|# Generated: 2026-04-04
     3|# Scope: workspace-hub + digitalmodel + worldenergydata + aceengineer-website
     4|
     5|## SUMMARY
     6|
     7|The field development ecosystem spans FOUR repos with a clear split:
     8|- **Code modules** (implemented, tested): Schematics, production engineering, subsea engineering, reservoir, economics
     9|- **Reference data** (catalog/docs): 6 real-world field case studies, FEED org charts, data source coverage maps
    10|- **Web calculators** (deployed): NPV/IRR/MIRR calculator with JS engine on aceengineer.com
    11|- **Planning/gaps** (documented but not yet coded): Concept selection, hub-vs-standalone, wet/dry tree, facility sizing, production profiles, DCA
    12|
    13|---
    14|
    15|## 1. CODE MODULES (Implemented)
    16|
    17|### 1.1 digitalmodel/src/digitalmodel/field_development/ (11 .py files, 3 classes, 18 functions)
    18|**Purpose**: Field layout schematic generation (SVG/PNG)
    19|**Key files**:
    20|- `schematic_generator.py` — Top-level API: generate_field_schematic(config) -> output_path
    21|  - Routes to correct schematic class by development_type
    22|  - Supports: subsea_tieback, platform, fpso_spread
    23|  - Example config: SOLVEIG_PHASE2_CONFIG (120m WD, 3 templates, 4 wells, FPSO host)
    24|- `schematics/subsea_tieback.py` — SubseaTiebackSchematic: side-view with templates, flowlines, host
    25|- `schematics/fpso_spread.py` — FpsoSpreadSchematic: FPSO + spread mooring + SPS
    26|- `schematics/platform_standalone.py` — PlatformSchematic: jacket/fixed + conductors + satellite wells
    27|- `schematics/renderer.py` — Common SVG/PNG save logic
    28|- `schematics/elements/icons.py` — Patch factories (FPSO, platform, template, well symbols)
    29|- `schematics/elements/annotations.py` — Scale bar, depth label, north arrow
    30|- `schematics/elements/seabed.py` — Seabed line + water column depth computation
    31|**Tests**: tests/field_development/test_field_development.py (184 lines), tests/test_field_development_schematic.py
    32|
    33|### 1.2 digitalmodel/src/digitalmodel/production_engineering/ (8 .py files)
    34|**Purpose**: Well performance analysis — IPR, VLP, Nodal Analysis
    35|**Key files**:
    36|- `ipr_models.py` — 4 IPR models: LinearIpr, VogelIpr, FetkovichIpr, CompositeIpr
    37|  - flow_rate(pwf_psi) -> q (bopd); flowing_pressure(q) -> Pwf (psi)
    38|- `vlp_correlations.py` — Hagedorn-Brown (1965), Beggs-Brill (1973) VLP correlations
    39|  - P_wf = P_wh + ΔP_hydrostatic + ΔP_friction
    40|  - TubingConfig, FluidProperties, FlowConditions data structures
    41|- `nodal_solver.py` — Finds IPR/VLP intersection (operating point) with confidence bounds
    42|  - Green/Amber/Red quality score -> ±5%/15%/30% uncertainty bands
    43|- `gigo_detector.py` — Garbage-in-garbage-out input validation
    44|- `nonlinearity_flags.py` — Flags nonlinear well behavior
    45|- `reconciliation_workflow.py` — Production data reconciliation
    46|- `test_quality_scorer.py` — Well test quality scoring
    47|
    48|### 1.3 digitalmodel/src/digitalmodel/subsea/ (70+ .py files)
    49|**Purpose**: Subsea engineering calculations
    50|**Submodules**:
    51|- `pipeline/` — Pipe sizing, pressure containment (DNV), lateral/upheaval/thermal buckling, free span VIV (DNV-RP-F105), on-bottom stability, pressure loss, API RP 1111 installation
    52|  - `pipe_sizing.py` — PipeSizing class with section/system properties
    53|  - `pipeline_pressure_dnv.py` — DNV pressure containment
    54|  - `lateral_buckling.py`, `thermal_buckling.py`, `upheaval_buckling.py`
    55|  - `free_span/` — 7 modules: span allowable length, natural frequency, fatigue damage, VIV response, onset screening, wave velocity, Weibull current
    56|  - `pressure_loss.py` — Flowline pressure drop
    57|- `catenary_riser/` — Catenary equations, lazy wave, effective weight, simple catenary
    58|- `mooring_analysis/` — Catenary mooring, designer, OrcaFlex generator
    59|- `viv_analysis/` — VIV screening, fatigue, frequency calculator, vortex shedding, tubular members
    60|- `vertical_riser/` — Riser stack-up components
    61|- `on_bottom_stability/` — DNV-RP-F109
    62|
    63|### 1.4 digitalmodel/src/digitalmodel/reservoir/ (2 .py files)
    64|**Purpose**: Petrophysical analysis
    65|- `stratigraphic.py` — Multi-well cross-section plotting (GR, RT, RHOB/NPHI, facies tracks)
    66|
    67|### 1.5 digitalmodel/src/digitalmodel/marine_ops/reservoir/ (5 .py files)
    68|**Purpose**: Reservoir modeling and production forecasting
    69|- `modeling.py` — ReservoirModel with depletion simulation, recovery_factor calculation
    70|  - ProductionForecast class with Arps decline curve analysis (exponential, hyperbolic, harmonic)
    71|- `properties.py` — PVT properties, irreducible water saturation
    72|- `analysis.py` — Reservoir analysis workflows
    73|
    74|### 1.6 digitalmodel/src/digitalmodel/well/ (7 .py files)
    75|**Purpose**: Well engineering
    76|- `drilling/hydraulics.py` — Drilling hydraulics
    77|- `drilling/rop_models.py` — Rate of penetration models
    78|- `drilling/dysfunction_detector.py` — Drilling dysfunction detection
    79|- `tubulars/design_envelope.py` — Tubular design envelope
    80|
    81|### 1.7 worldenergydata/src/worldenergydata/economics/ (3 .py files)
    82|**Purpose**: Field development economics — NPV, MIRR, carbon cost sensitivity
    83|**Key files**:
    84|- `dcf.py` — Core DCF engine
    85|  - CashFlowSchedule dataclass (years, capex, revenue, opex, carbon_cost, emission_tco2)
    86|  - calculate_npv() -> NPVResult (npv, discount_rate, net/discounted CFs)
    87|  - calculate_mirr() -> MIRRResult (mirr, finance_rate, reinvestment_rate, PV/FV)
    88|  - build_cash_flow_schedule() — assembles schedule from production profile
    89|- `carbon.py` — Carbon cost sensitivity
    90|  - carbon_npv_curve() — NPV sweep over carbon price range
    91|  - breakeven_carbon_price() — Solve for NPV=0 carbon price
    92|  - tornado_sensitivity() — Per-parameter swing analysis for tornado charts
    93|
    94|### 1.8 worldenergydata/src/worldenergydata/sodir/npv_norway.py (604 lines)
    95|**Purpose**: Norwegian petroleum fiscal regime NPV
    96|- NorwegianFinancialParameters: petroleum tax (78%), corporate (22%), special (56%)
    97|- Uplift rate (5.6% over 4 years), linear depreciation over 6 years
    98|- Oil/gas price assumptions, working interest, net revenue interest
    99|
   100|### 1.9 worldenergydata/src/worldenergydata/lower_tertiary/npv.py (219 lines)
   101|**Purpose**: Lower Tertiary field-level NPV with FDAS lease mappings
   102|- load_lease_mapping() — FDAS lease mapping with normalized lease numbers
   103|- load_field_inputs() — Modular field configurations
   104|
   105|### 1.10 worldenergydata/src/worldenergydata/drilling/batch_economics/economics.py (256 lines)
   106|**Purpose**: Batch drilling economics
   107|- BatchDrillingEconomics class
   108|- Wright learning curve, mobilization amortization, batch vs standalone NPV, break-even well count
   109|
   110|### 1.11 aceengineer-website/assets/js/npv-calculator-engine.js (279 lines)
   111|**Purpose**: Client-side NPV calculator for aceengineer.com website
   112|- calcDeclineProduction (exponential decline)
   113|- calcAnnualRevenue (with royalty and price escalation)
   114|- calcAnnualOpex (with escalation)
   115|- calcNPV, calcIRR, calcMIRR, calcPayback
   116|- buildYearlyCashflows
   117|- Pure JS, no DOM deps, unit-testable
   118|
   119|---
   120|
   121|## 2. REFERENCE DATA & CATALOGS
   122|
   123|### 2.1 Field Development Case Study Catalog (6 entries)
   124|Location: digitalmodel/docs/domains/references/field_development/catalog/
   125|Schema: catalog_schema.yaml (defines 20+ fields: id, name, operator, basin, water_depth, development_type, reserves, capex, npv_assumptions, etc.)
   126|Index: catalog_index.yaml (with by_basin, by_development_type, by_field_type, by_operator lookups)
   127|
   128|| Field | Basin | Type | WD(m) | CAPEX($B) | Reserves(MMboe) | Peak(kboe/d) |
   129||-------|-------|------|-------|-----------|-----------------|-------------|
   130|| Solveig Phase 2 | NCS | subsea_tieback | 115 | 0.6 | 39 | - |
   131|| Johan Sverdrup Ph1 | NCS | fixed_platform | 120 | 11.5 | 2700 | 535 |
   132|| Mad Dog Phase 2 | GoM | semi_submersible | 1340 | 9.0 | 140 | 140 |
   133|| Jack/St. Malo | GoM | SPAR | 2134 | 7.5 | 500 | 94 |
   134|| Liza Phase 2 | Guyana | FPSO | 1650 | 6.0 | 600 | 220 |
   135|| Vito | GoM | semi_submersible | 1219 | 1.7 | 300 | 100 |
   136|
   137|### 2.2 FEED Organization Chart
   138|- `feed.puml` — PlantUML WBS for FEED project structure
   139|  - Workstreams: Wellhead Platform, SURF, Company Documentation, FPSO
   140|  - FPSO team: Hull & Mooring, Naval Architect, Process, E&I, Topsides/Turret interface
   141|
   142|### 2.3 Data Source Coverage Map
   143|- `data-source-coverage.md` — Multi-basin data availability tracking
   144|  - Done: BSEE (GoM)
   145|  - Pending: NPD/Sodir (NCS), NSTA (UKCS), ANP (Brazil), EIA (US non-GoM), C-NLOER (Canada)
   146|  - Watch list: Guyana, Suriname, Namibia, Falklands
   147|  - Dead ends: Australia NOPTA, Angola ANPG, IEA MODS
   148|
   149|### 2.4 Supporting Reference Docs
   150|- `aker-bp-solveig-phase2-2026.md` — Detailed Solveig Phase 2 case study
   151|- `development-value-drivers.jpg` — Field development value driver diagram
   152|- `revive_old_wells.md` — Well revitalization process reference
   153|- `minimum_facilities.md` — Minimum facilities concept (stub)
   154|
   155|### 2.5 OrcaFlex Templates for Subsea Architecture
   156|- `templates/umbilicals/umbilical_hybrid/` — Umbilical base model (800m WD), deep water (1200m) and steel tube variations
   157|- `templates/pipelines/pipeline_hybrid/` — Pipeline base model (500m WD, 16" X65), 12" flowline case
   158|- `templates/subsea/jumper_hybrid/` — Jumper base model
   159|- `templates/platforms/tlp_hybrid/` — Mini TLP variation
   160|
   161|### 2.6 Reservoir Analysis Example Config
   162|- `examples/domains/input_files/reservoir_analysis/field_example_basic.yml`
   163|  - Permian Basin unconventional shale well configuration
   164|  - Log curves (GR, RHOB, NPHI, RT), stratigraphy, log analysis, volumetrics
   165|  - Recovery factors: primary 8%, secondary 12%, enhanced 15%
   166|
   167|### 2.7 Client Project FDAS Data (Historical)
   168|- `client_projects/energy_fdas/` — Cascade/Chinook field development visualizations
   169|  - Production profiles, well paths, east-north plots
   170|- `client_projects/energy_bsee/` — BigFoot, Jack, St. Malo, Stones, Julia
   171|  - Field development production & well plots
   172|
   173|---
   174|
   175|## 3. PLANNING & CAPABILITY GAPS (Documented but NOT Coded)
   176|
   177|### 3.1 Capability Tiers (.planning/architecture/capability-tiers.yaml)
   178|- worldenergydata key gaps:
   179|  - WRK-317: Plotly Dash dashboard for BSEE/FDAS
   180|  - WRK-318: Arps decline curve production forecasting module
   181|  - WRK-319: Real-time EIA/IEA feed ingestion
   182|  - WRK-321: MIRR/NPV with carbon cost sensitivity (partially implemented)
   183|  - No field development screening capability
   184|  - No cross-source synthesis layer
   185|  - No unified query API
   186|
   187|### 3.2 Pre-FEED Workflow (.planning/architecture/workflow-patterns.yaml)
   188|- Pre-FEED feasibility assessment workflow defined:
   189|  - Deepwater rigid pipeline system: wall thickness, collapse check, weather window
   190|  - Produces pre-FEED calculation package
   191|  - Referenced in agent-vision.md as autonomous agent workflow
   192|
   193|### 3.3 NPV Calculator References (.planning/milestones/)
   194|- npv-field-development calculator deployed on aceengineer.com
   195|- Cross-repo dependency: worldenergydata economics <-> digitalmodel field_development
   196|- WRK-080: NPV blog post, WRK-081: NPV calculator defaults
   197|
   198|### 3.4 Skills Knowledge Graph (.planning/skills/skills-knowledge-graph.yaml)
   199|- "Offshore field development economic analysis" listed as skill
   200|
   201|---
   202|
   203|## 4. CONTENT THAT DOES NOT EXIST AS CODE (Referenced but Unimplemented)
   204|
   205|| Topic | Status | Where Referenced |
   206||-------|--------|------------------|
   207|| Concept selection (FPSO vs TLP vs SPAR vs semi vs fixed) | NOT CODED — schematic routing only | schematic_generator.py routing logic |
   208|| Hub vs standalone analysis | NOT CODED | catalog contains both patterns |
   209|| Wet tree vs dry tree comparison | NOT CODED | Not found anywhere |
   210|| Flowline routing optimization | NOT CODED | OrcaFlex pipeline templates exist |
   211|| Umbilical sizing calculations | NOT CODED — templates only | OrcaFlex umbilical templates |
   212|| Production profiles / plateau rates | PARTIAL — Arps decline in marine_ops | modeling.py ProductionForecast |
   213|| Reserves estimation / volumetrics | PARTIAL — example config only | field_example_basic.yml |
   214|| Recovery factors | PARTIAL — calculated in depletion model | modeling.py |
   215|| Facility sizing | NOT CODED | minimum_facilities.md (stub) |
   216|| Topsides design | NOT CODED — FEED org chart only | feed.puml |
   217|| CAPEX breakdown models | NOT CODED — catalog has totals only | catalog entries |
   218|| OPEX estimation | PARTIAL — opex arrays in DCF | dcf.py CashFlowSchedule |
   219|| FDP (Field Development Plan) document generation | NOT CODED | Referenced in planning |
   220|| Tieback distance optimization | NOT CODED — distance is input only | catalog_schema.yaml tieback_distance_km |
   221|| DCA (Decline Curve Analysis) | PARTIAL — basic Arps in marine_ops | modeling.py arps_decline_analysis |
   222|| Cross-basin field development screening | NOT CODED | capability-tiers.yaml key gap |
   223|
   224|---
   225|
   226|## 5. ARCHITECTURE SUMMARY
   227|
   228|```
   229|IMPLEMENTED CODE                           REFERENCE DATA / DOCS
   230|==================                         =====================
   231|
   232|digitalmodel/field_development/            catalog/ (6 field studies)
   233|  - Schematic SVG/PNG generator             - Solveig, Sverdrup, Mad Dog
   234|  - SubseaTieback, Platform, FPSO           - Jack/StMalo, Liza, Vito
   235|  - Elements: icons, annotations, seabed    - Schema + index + lookups
   236|
   237|digitalmodel/production_engineering/       feed.puml (FEED org chart)
   238|  - IPR: Vogel, Fetkovich, Linear, Comp   data-source-coverage.md
   239|  - VLP: Hagedorn-Brown, Beggs-Brill      development-value-drivers.jpg
   240|  - Nodal analysis solver
   241|  - Quality scoring
   242|
   243|digitalmodel/subsea/                       OrcaFlex templates
   244|  - Pipeline: sizing, pressure, buckling    - Flowline, umbilical, jumper, TLP
   245|  - Free span: F105 VIV analysis
   246|  - Catenary riser, mooring, VIV
   247|
   248|worldenergydata/economics/                 aceengineer-website
   249|  - DCF: NPV + MIRR                        - npv-field-development.html
   250|  - Carbon cost sensitivity                 - npv-calculator-engine.js
   251|  - Norwegian fiscal regime
   252|  - Lower Tertiary NPV + FDAS
   253|
   254|worldenergydata/drilling/batch_economics/  Client FDAS data (historical)
   255|  - Learning curve, break-even              - Cascade/Chinook, BigFoot, Jack
   256|```
   257|
