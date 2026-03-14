# digitalmodel Calculation Audit

Generated: 2026-03-13 | WRK-1179 Stream B Task 1

## Summary Statistics

| Metric | Count |
|--------|-------|
| Source files with public API | 1,077 |
| Public functions | 7,355 |
| Public classes | 2,027 |
| Top-level disciplines | 30 |
| Standards mapped (capability map) | 17,799 |
| Capability map modules | 27 |
| Standards with status=done | 0 |
| Standards with status=gap | 455 |

## Per-Discipline Breakdown

### structural (107 files, 739 funcs, 233 classes) -- LARGEST

**Implemented calculations:**
- Wall thickness design: API RP 1111, API RP 2RD, API STD 2RD, ASME B31.8, DNV ST F101, ISO 13623, PD 8010-2
- Fatigue: SN curves (DNV, API, BS 7608), rainflow counting (ASTM), Miner's rule damage accumulation, frequency-domain spectral fatigue (Dirlik, Narrowband, Wirsching-Light, Zhao-Baker), time-domain fatigue, parametric sweeps
- Pipe capacity: burst, collapse, propagation buckling, combined loading (per DNV OS F101, API STD 2RD, ASME B31)
- Structural analysis: Euler/Johnson-Ostenfeld column buckling, plate buckling, tension/combined-loading checks
- Stress: von Mises, principal stresses, hoop/longitudinal/torsional, nonlinear stress-strain
- Pipe cross-section: geometry, section properties, multi-layer pipes
- Jacket/topside: API RP 2A joint classification, punching shear, member checks

**Standards referenced in code:** API RP 2A, API RP 1111, API RP 2RD, API STD 2RD, ASME B31.4, ASME B31.8, DNV ST F101 (OS F101), DNV RP C203, ISO 13623, PD 8010-2, BS 7608, ASTM E1049 (rainflow)

**Gaps (from capability map):**
- structural/fatigue: 48 gap standards (BS 7608 editions, DNV RP C203 editions, DNV RP F204, spectral fatigue FPSO guides, NORSOK N-001)
- structural/structural_analysis: 28 gap standards (API RP 2A-WSD/LRFD editions, AISC, NORSOK N-004)
- structural/pipe_capacity: 50 gap standards (API 5L editions, API 17E, DNV OS F101 editions)

### subsea (55 files, 325 funcs, 75 classes)

**Implemented calculations:**
- Pipeline: pressure containment (DNV, API), pipe sizing, lateral/upheaval/thermal buckling, free-span (natural frequency, VIV onset screening, VIV response amplitude, fatigue damage), installation (S-lay sagbend/overbend per API RP 1111), pressure loss
- Catenary riser: simple catenary, lazy-wave analysis, effective weight, buoyancy module design, OrcaFlex model generation
- VIV analysis: natural frequency (multi-mode), vortex shedding frequency, reduced velocity screening, lock-in check, VIV fatigue damage
- Mooring: catenary solver, horizontal tension, stiffness, touchdown analysis, environmental loads, intact/damaged condition checks, OrcaFlex model generation
- Vertical riser: stack-up, joint properties, pipe properties

**Standards referenced:** API RP 1111, API RP 2RD, DNV OS F101, DNV RP F109, API RP 2SK, DNV OS E301

**Gaps (from capability map):**
- subsea/pipeline: 48 gaps (API RP 1111 editions, DNV ST F101 editions, on-bottom stability)
- subsea/catenary_riser: 49 gaps (API RP 2RD editions, DNV OS F201)
- subsea/mooring_analysis: 49 gaps (API RP 2SK editions, DNV OS E301)
- subsea/viv_analysis: 6 gaps (DNV RP F105 free spanning, experimental VIV data)

### cathodic_protection (4 files, 30 funcs, 4 classes)

**Implemented calculations:**
- Anode design per DNV RP B401 (anode mass, resistance, current output, design life)
- Coating breakdown per ISO 15589-2
- API RP 16Q2 fuel system CP
- CP assessment workflow

**Standards referenced:** DNV RP B401, ISO 15589-2, API RP 16Q2, ASTM, NACE

**Gaps:** Module not in capability map as separate entry; standards appear covered by implementation

### hydrodynamics (132 files, 825 funcs, 278 classes)

**Implemented calculations:**
- Wave spectra (JONSWAP, PM, Ochi-Hubble, Torsethaugen, etc.)
- RAO analysis: interpolation, phase handling, motion response
- Diffraction: large module with AQWA/BEMRosetta interfaces
- Hull library: parametric hull forms
- OCIMF loading: vessel-vessel interaction
- Passing ship effects
- Planing hull hydrodynamics
- Coefficient database

**Standards referenced:** API, DNV, ISO (in code); no explicit capability map gaps (0 gaps listed for hydro modules)

**Note:** Hydrodynamics has 0 standards mapped in capability map -- this is a data gap in the map itself, not in the code. The code is substantial (825 functions).

### asset_integrity (45 files, 393 funcs, 52 classes)

**Implemented calculations:**
- API 579 / ASME FFS-1: RSF (Remaining Strength Factor) calculations, Level 1/2 assessments
- Fracture mechanics: basic framework present
- GML (General Metal Loss) assessment, double-averaging method
- Pipeline fitness-for-service skill

**Standards referenced:** API 579-1/ASME FFS-1, BS 7910

**Gaps (from capability map):**
- asset_integrity/API579: 50 gaps (API 579-1 editions, ASME sections)
- asset_integrity/fracture_mechanics: 50 gaps (BS 7910 editions, ASTM E1290, R6, SINTAP/FITNET)

### well (4 files, 18 funcs, 11 classes)

**Implemented calculations:**
- Drilling hydraulics: annular velocity, pressure drop, ECD, cuttings transport
- ROP models: Bourgoyne-Young, drilling-specific-energy regression
- Dysfunction detector: MSE-based drilling dysfunction
- Tubular design envelope: hoop stress, VME stress, casing design

**Standards referenced:** API (general), ISO

**Gaps:** Not explicitly in capability map; small module with basic calculations

### marine_ops (84 files, 510 funcs, 197 classes)

**Implemented calculations:**
- Marine engineering: lifting, installation, vessel operations
- Artificial lift: ESP, gas lift, plunger lift
- Marine analysis: motion analysis, operability
- Reservoir: basic inflow models

**Gaps:** marine_ops/artificial_lift has 50 gaps; marine_ops/marine_engineering has 14 gaps

### signal_processing (18 files, 140 funcs, 23 classes)

**Implemented calculations:**
- Rainflow counting (ASTM E1049 compliant)
- FFT/PSD: windowed FFT, power spectral density
- SN curve fatigue damage from signal data
- Digital filters: bandpass, bandstop, lowpass, highpass (Butterworth)
- Time series: detrend, smooth, resample, outlier removal
- OrcaFlex signal analysis pipeline

**Standards referenced:** ASTM E1049, DNV RP C203, BS 7608

### production_engineering (7 files, 39 funcs, 27 classes)

**Implemented calculations:**
- IPR models: Vogel, Fetkovich, linear
- VLP correlations: Hagedorn-Brown, Beggs-Brill
- Nodal analysis solver
- Test quality scoring, GIGO detection, reconciliation workflow

### geotechnical -- DIRECTORY DOES NOT EXIST (HIGH PRIORITY GAP)

**Status:** No source directory exists at `src/digitalmodel/geotechnical/`. The capability map lists 6 sub-modules with 10 gap standards total:
- soil_models: API RP 2GEO, DNV RP C212 (2 gaps)
- piles: API RP 2GEO Pile Design Sec 6-8 (1 gap)
- on_bottom_stability: DNV RP F109 (1 gap)
- foundations: DNV RP C212, ISO 19901-4 (2 gaps)
- anchors: DNVGL RP E301, DNV RP E303, API RP 2SK (3 gaps)
- scour: DNV RP F107 (1 gap)

### Other Disciplines

| Discipline | Files | Funcs | Classes | Notes |
|-----------|-------|-------|---------|-------|
| solvers | 243 | 1,351 | 477 | FEA, ODE, optimization frameworks |
| infrastructure | 82 | 1,187 | 145 | Data pipelines, ETL, config management |
| visualization | 41 | 342 | 118 | Dashboards, reports, CAD integration |
| data_systems | 41 | 258 | 50 | Data models, transformers |
| gis | 21 | 124 | 23 | Geospatial analysis |
| specialized | 21 | 201 | 21 | Rigging, API analysis |
| workflows | 80 | 547 | 171 | Automation, MCP servers, agents |
| power | 12 | 42 | 40 | Power systems |
| field_development | 8 | 18 | 3 | Field layout, economics |
| naval_architecture | 7 | 20 | 0 | Vessel design checks |
| drilling_riser | 4 | 13 | 0 | Drilling riser analysis |
| web | 36 | 174 | 37 | DigitalTwinFeed web app |
| orcaflex | 12 | 12 | 11 | OrcaFlex interfaces |
| orcawave | 11 | 11 | 11 | OrcaWave interfaces |
| ansys | 4 | 4 | 8 | ANSYS interfaces |
| nde | 1 | 1 | 1 | Non-destructive examination |

## Priority Gap Ranking

### HIGH Priority (no implementation exists)

| # | Gap | Standards Available | Impact |
|---|-----|-------------------|--------|
| 1 | geotechnical/soil_models | API RP 2GEO, DNV RP C212 | Foundation design blocked |
| 2 | geotechnical/on_bottom_stability | DNV RP F109 | Pipeline stability assessments blocked |
| 3 | geotechnical/piles | API RP 2GEO Sec 6-8 | Pile design blocked |
| 4 | geotechnical/foundations | DNV RP C212, ISO 19901-4 | Shallow foundation design blocked |
| 5 | geotechnical/anchors | DNVGL RP E301, DNV RP E303, API RP 2SK | Anchor design blocked |
| 6 | geotechnical/scour | DNV RP F107 | Scour assessment blocked |

### MEDIUM Priority (partial implementation, key standards missing)

| # | Gap | Current State | Standards Needed |
|---|-----|--------------|-----------------|
| 7 | Spectral fatigue completion | Framework exists (4 methods) but not validated against FPSO/riser standards | ABS FPSO fatigue guide, DNV RP F204 |
| 8 | Fracture mechanics (BS 7910) | Basic framework only | BS 7910:2013, R6, SINTAP/FITNET |
| 9 | API 579 Level 3 | RSF + Level 1/2 exist | API 579 Part 9-13 (creep, fire, dents) |
| 10 | Mooring analysis (API RP 2SK) | Catenary solver exists, no full API 2SK checks | API RP 2SK 3rd Ed, BV NR 493 |

### LOWER Priority (extensive code exists, incremental standard coverage needed)

| # | Gap | Notes |
|---|-----|-------|
| 11 | Pipeline DNV ST F101 latest edition alignment | Code implements many checks; edition-specific factors may differ |
| 12 | Structural API RP 2A-LRFD | WSD path implemented; LRFD variant missing |
| 13 | VIV DNV RP F105 full implementation | Screening + frequency calc exist; full response model partial |
| 14 | Hydrodynamics capability map population | 825 functions exist but 0 standards mapped in capability map |
| 15 | Artificial lift standards | 50 gaps in capability map; code exists in marine_ops |

## Key Findings

1. **Geotechnical is the largest gap** -- no source directory exists despite 10 standards identified in the capability map. This blocks foundation, pile, anchor, and on-bottom stability workflows.

2. **Hydrodynamics capability map is empty** -- the code has 825 functions across 132 files but the capability map shows 0 standards. The map needs population, not the code.

3. **Structural is the most mature discipline** -- 739 functions covering 7 wall-thickness design codes, comprehensive fatigue (time and frequency domain), pipe capacity, and structural analysis.

4. **Zero standards marked as "done"** in the entire capability map -- either the map status field is not being updated as code is written, or the mapping methodology does not track implementation status. This is a process gap.

5. **signal_processing is an unlisted strength** -- 140 functions with ASTM-compliant rainflow counting and spectral analysis, but not represented in the capability map at all.
