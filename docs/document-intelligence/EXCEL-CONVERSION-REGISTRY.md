# Excel Workbook Conversion Registry

> **Goal**: Systematically convert productive engineering Excel workbooks to Python code in our repo ecosystem, enabling scalable, testable, and version-controlled calculations.

> **Strategy**:
> 1. Transfer productive workbooks to private `client_projects` repo on target machine
> 2. Use Claude in Excel to analyze calculations and extract logic
> 3. Port calculations to Python code in appropriate repos (digitalmodel, assetutilities, workspace-hub)
> 4. Track conversion progress: INVENTORY -> ANALYZED -> CONVERTED -> VERIFIED

---
## Phase A: High-Priority Engineering Calculations

### Tier 1: Deepwater Installation/Lift Engineering

| # | Source Path | File | Domain | Sheets | Complexity | Status | Target Module |
|---|-------------|------|--------|--------|------------|--------|---------------|
| 1 | `/mnt/ace/rock-oil-field/s7/ballymore/Jumper_Manifold to PLET/` | `Jumper_Input_Ballymore_Manifold-PLET V2.xlsx` | Jumper lift/installation engineering (pipe geometry, buoyancy, strake, rigging, crane capacity, weight check) | 7 | Medium | INVENTORY | `digitalmodel/install/lift_analysis.py` |
| 2 | `client_projects/energy_engineering/003 fdas-report/Ph1/Cal/` | `614-CAL-2217-01 (SideLift Case 2-1 Plate Buckling_1P04g).xlsm` | Plate buckling analysis (FDAS) | TBD | High | INVENTORY | `digitalmodel/structural/plate_buckling.py` |
| 3 | `client_projects/energy_engineering/015 Plate Buckling/Ref/` | `614-CAL-2215-01 (SEWOL ANSYS Buckling Template) DRAFT2.xlsm` | ANSYS buckling template | TBD | High | INVENTORY | `digitalmodel/structural/plate_buckling.py` |

### Tier 2: Riser/Intervention Engineering

| # | Source Path | File | Domain | Complexity | Status | Target Module |
|---|-------------|------|--------|------------|--------|---------------|
| 4 | `client_projects/energy_tei/17-087 TEI Intervention Riser/RiserAbaqus/` | `InterventionRiser.xlsm` (+ Rev1/Rev2 variants) | Intervention riser Abaqus model generation | High | INVENTORY | `digitalmodel/riser/intervention.py` |
| 5 | `client_projects/energy_tei/17-087 TEI Intervention Riser/RiserAbaqus/` | `drillingriser.xlsm` (+ HWCG variant) | Drilling riser Abaqus model generation | High | INVENTORY | `digitalmodel/riser/drilling.py` |
| 6 | `client_projects/energy_tei/17-087 TEI Intervention Riser/RiserAbaqus/` | `CoilTubingRiser1.xlsm` | Coil tubing riser analysis | Medium | INVENTORY | `digitalmodel/riser/coil_tubing.py` |
| 7 | `/mnt/ace/client_projects/0163-FDAS/FDAS/Engineering/risers/` | `Riser Sizing and Top Tension1.xlsx` | Riser sizing/top tension calc | Medium | INVENTORY | `digitalmodel/riser/top_tension.py` |
| 8 | `/mnt/ace/client_projects/0163-FDAS/FDAS/Engineering/risers/` | `20160730 Riser Stroke-Stretch v WSirius Heave (VA).xlsx` | Riser stroke/stretch analysis | High | INVENTORY | `digitalmodel/riser/stroke_stretch.py` |
| 9 | `/mnt/ace/client_projects/0163-FDAS/FDAS/Engineering/risers/assembly/Rev20/` | Telescopic Joint, Tree, Stem Joint models (12+ files) | Riser component assembly models | Medium | INVENTORY | `digitalmodel/riser/assembly/` |

### Tier 3: Umbilical/SCR Installation (Saipem Yellowtail)

| # | Source Path | File | Domain | Complexity | Status | Target Module |
|---|-------------|------|--------|------------|--------|---------------|
| 10 | `saipem/yellowtail/code/ref/dynamics/` | `502_LB100m_Bwd.xlsm` | Umbilical dynamic analysis | High | INVENTORY | `digitalmodel/umbilical/dynamics.py` |
| 11 | `saipem/yellowtail/code/rev2/umb_main_505/dynamics/` | `pih.xlsx`, `bm.xlsx`, `nl.xlsx`, `sta.xlsx` | Umbilical post-processing results | Medium | INVENTORY | `digitalmodel/umbilical/post_process.py` |
| 12 | `saipem/yellowtail/code/rev2/umb_main_505/5_sta/` | `UTA.xlsx`, `Termination.xlsx`, `BR_properties.xlsx` | Umbilical static analysis/termination | Medium | INVENTORY | `digitalmodel/umbilical/static.py` |
| 13 | `saipem/general/engg/dynamic_umb_go_by/` | `UMB_TYPE-G - Catenary Wave Lowering.xlsx` (+ variants) | Umbilical catenary wave installation | High | INVENTORY | `digitalmodel/umbilical/installation.py` |
| 14 | `saipem/yellowtail/code/ref/504 - Lazy Wave FPSO Offset/static/` | Multiple Static Results workbooks | FPSO offset/static analysis | Medium | INVENTORY | `digitalmodel/umbilical/fpso_offset.py` |
| 15 | `saipem/general/yml_modular_example/src/` | `talos_venice_2ndEnd_Laydown.xlsm` | Umbilical 2nd end laydown | Medium | INVENTORY | `digitalmodel/umbilical/laydown.py` |

### Tier 4: Production Engineering Calculations (Reusable Library)

| # | Source Path | File | Domain | Complexity | Status | Target Module |
|---|-------------|------|--------|------------|--------|---------------|
| 16 | `client_projects/energy_engineering/014 ProductionEngineering/Ref/CAL/` | `ESPdesign-SI Units.xls`, `ESPdesign-US Field Units.xls` | ESP design calculations | High | INVENTORY | `assetutilities/production/esp_design.py` |
| 17 | `client_projects/energy_engineering/014 ProductionEngineering/Ref/CAL/` | `GasLiftValveDesign-SI Units.xls`, `US Field Units.xls` | Gas lift valve design | High | INVENTORY | `assetutilities/production/gas_lift.py` |
| 18 | `client_projects/energy_engineering/014 ProductionEngineering/Ref/CAL/` | `Cullender-SmithBHP.xls`, `Guo-GhalamborBHP.xls` | BHP calculation methods | Medium | INVENTORY | `assetutilities/production/nodal_analysis.py` |
| 19 | `client_projects/energy_engineering/014 ProductionEngineering/Ref/CAL/` | `Brill-Beggs-Z.xls`, `Hall-Yarborough-Z.xls`, `Carr-Kobayashi-Burrows-GasViscosity.xls` | PVT/fluid property calculations | Low | INVENTORY | `assetutilities/production/pvt.py` |
| 20 | `client_projects/energy_engineering/014 ProductionEngineering/Ref/CAL/` | `BottomHoleNodalGas.xls`, `Multilateral Gas Well Deliverability*.xls` | Nodal analysis/multilateral | High | INVENTORY | `assetutilities/production/nodal_analysis.py` |
| 21 | `client_projects/energy_engineering/014 ProductionEngineering/Ref/CAL/` | `CentrifugalCompressorPower*.xls`, `ReciprocatingCompressorPower*.xls` | Compression calculations | Medium | INVENTORY | `assetutilities/production/compression.py` |
| 22 | `client_projects/energy_engineering/014 ProductionEngineering/Ref/CAL/` | `SuckerRodPumpingFlowRate&Power.xls`, `SuckerRodPumpingLoad.xls` | Sucker rod pumping calcs | Medium | INVENTORY | `assetutilities/production/srp.py` |
| 23 | `client_projects/energy_firm_data_analytics/dynacard/srp/` | Multiple dynacard workbooks (7 files) | Dynamometer card/SRP analysis | High | INVENTORY | `assetutilities/production/dynacard.py` |
| 24 | `client_projects/energy_firm_data_analytics/oda/Data/Hydraulics/` | `Hydraulics Input Sheet v2.xlsm` | Well hydraulics | Medium | INVENTORY | `assetutilities/production/hydraulics.py` |

### Tier 5: Structural/Mechanical Engineering

| # | Source Path | File | Domain | Complexity | Status | Target Module |
|---|-------------|------|--------|------------|--------|---------------|
| 25 | `client_projects/energy_firm_data_analytics/Corrosion/` | `Galvanic Corrosion Guide.xls`, `ScaleSoftPitzer V 12 1.xls` | Corrosion/materials | Medium | INVENTORY | `assetutilities/integrity/corrosion.py` |
| 26 | `client_projects/energy_integrity/salm/Ref/` | `Small FPSO (Rev0).xls`, `Small FPSO (Rev1).xls`, `STA BARMOT Swiftwater Barge.xlsm` | FPSO/barge characteristics | Low | INVENTORY | `assetutilities/vessel/vessel_props.py` |
| 27 | `client_projects/energy_tei/17-087 TEI Intervention Riser/Proposal/` | `TVO17-087-CTR-0001.xls` | Cost estimation | Low | INVENTORY | `assetutilities/economics/cost_est.py` |
| 28 | `rock-oil-field/s7/analysis_general/_ref/epic/` | Multiple padeye sizing workbooks (4 files) | Padeye/lifting point design | Medium | INVENTORY | `assetutilities/lifting/padeye.py` |
| 29 | `rock-oil-field/s7/analysis_general/train/SCR Design April 2015/Spreadsheets/` | `FR-DCE-RPL-306-SCR-pipe-design-rev0.4.xls` | SCR pipe design | Medium | INVENTORY | `digitalmodel/pipeline/scr_design.py` |
| 30 | `client_projects/energy_engineering/Big Dog/` | `5300-80-DM-REG-0001-A14.xls` (SPAR Export SCR), `5300-30-DM-REG-0001-AB.xls` (Mad Dog screening) | Spar/SCR design docs | Medium | INVENTORY | `digitalmodel/pipeline/scr_design.py` |

### Tier 6: Hydrodynamics/Mooring (ACMA Projects)

| # | Source Path | File | Domain | Complexity | Status | Target Module |
|---|-------------|------|--------|------------|--------|---------------|
| 31 | `acma-projects/_engineering/passing_ship/` | Multiple passing ship analysis workbooks (6 files .xlsm) | Passing ship forces | High | INVENTORY | `digitalmodel/hydro/passing_ship.py` |
| 32 | `acma-projects/B1512/analysis/rev2/03_stability/` | Stability analysis workbooks (Righting Arms, Offsets, Tanks, etc.) | Vessel stability analysis | High | INVENTORY | `digitalmodel/hydro/stability.py` |
| 33 | `acma-projects/B1512/analysis/rev2/04_diffraction/orcawave/output/` | OrcaWave output workbooks | Diffraction analysis results | Medium | INVENTORY | `digitalmodel/hydro/diffraction_results.py` |
| 34 | `acma-projects/B1512/analysis/rev2/05_mooring/output/collate/` | Mooring static results workbooks | Mooring static analysis | Medium | INVENTORY | `digitalmodel/mooring/static.py` |
| 35 | `acma-projects/calculations/raos/` | RAO data QA workbooks | RAO data processing | Medium | INVENTORY | `digitalmodel/hydro/rao_processing.py` |
| 36 | `acma-projects/_aqwa/` | `Damping_Analysis.xlsm`, `FST1 AQWA Setup R0 -VA.xlsm` | AQWA damping/analysis setup | High | INVENTORY | `digitalmodel/hydro/aqwa_damping.py` |
| 37 | `client_projects/ecs/proj/9645/` | `SHI RAO curves VIK-0001-55464_-_003.XLS` (+ checks variant) | RAO curve data from ECS | Low | INVENTORY | `digitalmodel/hydro/rao_curves.py` |
| 38 | `client_projects/ecs/proj/9831/res/` | `ECS H1122464-1 SPLIT RING.xls` | Split ring calculation | Low | INVENTORY | `assetutilities/structural/split_ring.py` |

---
## Phase B: Internal Reference Workbooks (Our Work)

### GTM/Demo Support Calculations

| # | Source Path | File | Domain | Complexity | Status | Notes |
|---|-------------|------|--------|------------|--------|-------|
| 39 | `client_projects/man/` | `0026-ENG-0002 O&G Technical Knowledge Refs.xlsm` | O&G technical knowledge base | Low | INVENTORY | Reference catalog |
| 40 | `rock-oil-field/s7/analysis_general/_ref/jpull/` | `JPULL Input_Droshky.xls` | Pipeline J-lay/J-pull analysis | Medium | INVENTORY | On-bottom pipeline |
| 41 | `rock-oil-field/s7/analysis_general/train/2014 DNV training/` | DNV training exercise workbooks | DNV pipeline methodology | Low | INVENTORY | Training/exercises |
| 42 | `client_projects/energy_firm_data_analytics/power_optimization/data/ice/` | ICE electric/natural gas data (2014-2016) | Emissions/emissions tracking | Low | INVENTORY | BSEE paper data |

---
## Phase C: Lower Priority / Exclude

### Administrative/Financial (Not for code conversion)

| # | Source Path | Description | Action |
|---|-------------|-------------|--------|
| 43 | `saipem/admin/quest/timesheet/` | Weekly timesheets | TRANSFER ONLY (no code) |
| 44 | `acma-projects/admin/timesheet/` | Weekly timesheets | TRANSFER ONLY (no code) |
| 45 | `aceengineer-admin/` | Invoices, business expenses | TRANSFER ONLY (no code) |
| 46 | `achantas-data/` | Personal financial/expense data | TRANSFER ONLY (no code) |
| 47 | `sabithaandkrishnaestates/` | SKEstates tax/lease docs | TRANSFER ONLY (no code) |

### Data/Reference Materials (Keep as data, not code)

| # | Source Path | Description | Action |
|---|-------------|-------------|--------|
| 48 | `client_projects/energy_bsee/data/` | BSEE production/well data | KEEP AS DATA files |
| 49 | `client_projects/ml_great_learning/`, `ML_LR/` | ML learning examples | KEEP AS REFERENCE |
| 50 | `client_projects/energy_firm_data_analytics/Refracing San Antonio Conference/` | Conference materials | KEEP AS REFERENCE |

---
## Conversion Priority Matrix

| Priority | Criteria | Tiers | Target Count |
|----------|----------|-------|--------------|
| P0 | Immediate GTM value; unique capabilities | Tier 1, 4 (top) | 5 workbooks |
| P1 | Core engineering library gaps; client deliverables | Tier 2, 3, 4 (remainder) | 12 workbooks |
| P2 | Reference/auxiliary calcs; nice-to-have | Tier 5, 6 | 10 workbooks |
| P3 | Internal reference data; training materials | Phase B | 4 workbooks |
| - | Admin/financial; raw data | Phase C | TRANSFER/KEEP |

---
## Progress Tracking

| Status | Count | Workbooks |
|--------|-------|-----------|
| INVENTORY | 38 | All workbooks identified |
| ANALYZED | 1 | #1 (Ballymore Jumper - 7 sheets: GA, Bare pipe, Bouyancy, Strake, Rigging, Crane Configuration, Weight Check) |
| CONVERTED | 0 | - |
| VERIFIED | 0 | - |

---
## Workflow

```
For each workbook:
1. 📋 INVENTORY - Identify file, sheets, and domain (DONE)
2. 🔍 ANALYZE   - Use Claude in Excel to extract calculation logic
3. 💻 CONVERT   - Port to Python with openpyxl for I/O, pytest for tests
4. ✅ VERIFY    - Cross-check results vs original spreadsheet
5. 📦 DEPLOY    - Merge to digitalmodel or assetutilities repo
```

---
## Notes

- **Source locations**: `/mnt/ace/` (raw ACE workspace), `/mnt/local-analysis/workspace-hub/` (workspace-hub repo)
- **Target repos**: `digitalmodel/` (engineering algorithms), `assetutilities/` (production/utilities)
- **Legal compliance**: All client project files must pass `.legal-deny-list.yaml` scan before transfer (scripts/legal/legal-sanity-scan.sh)
- **OCR limitation**: Image-based PDFs excluded - applies to any workbook that is a scanned image (not typical for .xlsx)
- **Phase B note**: Skip image-based PDFs as per user directive (#1643, #1772)

---
*Created: 2025-04-05 | Issue: workspace-hub#1933 | Maintainer: Hermes AI Agent*
