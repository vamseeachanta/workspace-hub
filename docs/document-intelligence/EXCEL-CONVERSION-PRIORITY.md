# Excel-to-Code Conversion: Budget-Ranked Priority List

> **Estimation model**: Each workbook requires:
> - **Analysis** (Claude in Excel): read sheets, extract formulas, understand logic flow
> - **Conversion** (Hermes): write Python with openpyxl, type hints, tests, docs
> - **Verification**: cross-check outputs vs original
>
> **Effort levels**: `Low` (1 workbook, 1-3 sheets, simple math), `Medium` (2-7 sheets, cross-refs), `High` (7+ sheets, macros/VBA, iteration, complex engineering)
>
> **Estimated token cost per workbook** (analysis + conversion + tests):
> - Low: ~500K-1M tokens
> - Medium: ~1M-2M tokens  
> - High: ~2M-5M tokens

---

## RANKED PRIORITY LIST

### 1. Jumper Lift Engineering: Ballymore Manifold-to-PLET
**Source**: `/mnt/ace/rock-oil-field/s7/ballymore/Jumper_Manifold to PLET/Jumper_Input_Ballymore_Manifold-PLET V2.xlsx`
**Domain**: Deepwater jumper installation (pipe geometry, buoyancy, strake, rigging, crane capacity, weight tally)
**Sheets**: 7 (GA, Bare pipe, Bouyancy, Strake, Rigging, Crane Configuration, Weight Check)
**Complexity**: Medium
**Est tokens**: ~1.5M
**GTM value**: Direct demo capability -- lift/installation analysis is a sellable offering
**Target module**: `digitalmodel/install/jumper_lift.py`
**Status**: Already analyzed -- sheet contents, formulas, cross-sheet refs fully documented. Ready to convert.

---

### 2. SUT Mudmat Analysis (Ballymore)
**Source**: `/mnt/ace/rock-oil-field/s7/ballymore/sut_mm/` (2 .xlsm + 3 .xlsx = 5 files)
**Domain**: Manifold/structure installation on seabed, resonance checks, mudmat tool
**Complexity**: High
**Est tokens**: ~3M
**GTM value**: Reusable installation tool -- mudmat design is repeatable across projects
**Target module**: `digitalmodel/install/mudmat.py`

---

### 3. Jumper PLET-to-PLEM (Ballymore)
**Source**: `/mnt/ace/rock-oil-field/s7/ballymore/Jumper_PLET to PLEM/` (2 .xlsm files)
**Domain**: SZ/DZ jumper models with AHC offsets
**Complexity**: Medium
**Est tokens**: ~1.5M
**GTM value**: Complements #1 -- full jumper analysis capability
**Target module**: `digitalmodel/install/jumper_aht.py`

---

### 4. Riser Stroke-Stretch vs Vessel Heave (FDAS)
**Source**: `/mnt/ace/client_projects/0163-FDAS/FDAS/Engineering/risers/stroke/20160730 Riser Stroke-Stretch v WSirius Heave.xlsx` (+ variants)
**Domain**: Drilling riser kinematics under vessel motion
**Complexity**: High
**Est tokens**: ~2.5M
**GTM value**: Critical for riser analysis demos -- stroke/stretch is a top-priority calculation
**Target module**: `digitalmodel/riser/stroke_stretch.py`

---

### 5. Riser Sizing and Top Tension (FDAS)
**Source**: `/mnt/ace/client_projects/0163-FDAS/FDAS/Engineering/risers/Riser Sizing and Top Tension*.xlsx` (+ multiple copies)
**Domain**: Riser weight, buoyancy module sizing, top tension envelope
**Complexity**: Medium
**Est tokens**: ~1.5M
**GTM value**: Universal riser design calculation
**Target module**: `digitalmodel/riser/sizing.py`

---

### 6. Plate Buckling: SideLift (FDAS)
**Source**: `client_projects/energy_engineering/003 fdas-report/Ph1/Py/Plate Buckling/Rev2/614-CAL-2217-01 (SideLift Case 2-1 Plate Buckling_1P04g).xlsm`
**Domain**: Structural plate buckling with ANSYS correlation
**Complexity**: High
**Est tokens**: ~2.5M
**GTM value**: Structural analysis demo -- plate buckling checks are universal in offshore
**Target module**: `digitalmodel/structural/plate_buckling.py`

---

### 7. Plate Buckling: ANSYS Template (SEWOL)
**Source**: `client_projects/energy_engineering/015 Plate Buckling/Ref/614-CAL-2215-01 (SEWOL ANSYS Buckling Template) DRAFT2.xlsm`
**Domain**: ANSYS plate buckling setup template
**Complexity**: High
**Est tokens**: ~2.5M
**GTM value**: Same structural domain as #6
**Target module**: `digitalmodel/structural/plate_buckling.py`

---

### 8. Padeye Sizing / Lifting Checks
**Source**: `/mnt/ace/rock-oil-field/s7/analysis_general/_ref/epic/` (4 .xls files)
**Domain**: Lifting padeye design checks (multiple projects: epic driven pile, ballast block, main SBM)
**Complexity**: Medium
**Est tokens**: ~1.5M
**GTM value**: Every installation needs padeye checks -- highly reusable
**Target module**: `digitalmodel/install/padeye.py`

---

### 9. Riser Assembly Models (FDAS)
**Source**: `/mnt/ace/client_projects/0163-FDAS/FDAS/Engineering/risers/assembly/Rev20/` (14+ workbooks: Telescopic Joint, Tree, Stem Bell Mouth, Taper Stress Joint, etc.)
**Domain**: Complete drilling riser assembly component geometry
**Complexity**: High
**Est tokens**: ~3M
**GTM value**: Deepwater riser system design capability
**Target module**: `digitalmodel/riser/assembly/`

---

### 10. Intervention Riser Abaqus Model Generation
**Source**: `client_projects/energy_tei/17-087 TEI Intervention Riser/RiserAbaqus/` (10+ .xlsm: InterventionRiser, drillingriser, CoilTubeRiser, variants)
**Domain**: Abaqus model generation for intervention/drilling risers
**Complexity**: High
**Est tokens**: ~3M
**GTM value**: Abaqus model gen from spreadsheet is a unique capability
**Target module**: `digitalmodel/riser/abaqus_gen.py`

---

### 11. SCR Pipe Design (DNV OS F201)
**Source**: `/mnt/ace/rock-oil-field/s7/analysis_general/train/SCR Design April 2015/Spreadsheets/` (12+ .xlsm: WTD, histograms, flexible joints, vessel motion sim, SN curves, SCFs)
**Domain**: Complete SCR mechanical design per DNV OS F201
**Complexity**: High
**Est tokens**: ~4M
**GTM value**: DNV-compliant SCR design is a major consulting deliverable
**Target module**: `digitalmodel/pipeline/scr_design.py`

---

### 12. Wall Thickness Design + Monte Carlo
**Source**: `/mnt/ace/rock-oil-field/s7/analysis_general/train/2014 DNV training/Module 1 wall thickness design/Exercises/` + Pipeline Design Workshop
**Domain**: DNV WTD methodology with Monte Carlo simulation
**Complexity**: Medium
**Est tokens**: ~1.5M
**GTM value**: Pipeline wall thickness is fundamental -- every project needs it
**Target module**: `digitalmodel/pipeline/wall_thickness.py`

---

### 13. Talos Venice Infield Umbilical Installation
**Source**: `/mnt/ace/rock-oil-field/s7/talos_venice/infield/` (31 workbooks: static steps, initiation, laydown, NL, 2nd end, deck handling, resonance)
**Domain**: Complete umbilical installation analysis workflow
**Complexity**: High
**Est tokens**: ~4M
**GTM value**: Umbilical installation is the #7 in the registry -- big domain
**Target module**: `digitalmodel/umbilical/installation.py`

---

### 14. Shell Perdido South Installation
**Source**: `/mnt/ace/rock-oil-field/s7/shell_perdido_south/` (14 workbooks: manifold AHCoff/SZ/SSRAO, mudmat tool, resonance)
**Domain**: Manifold installation analysis
**Complexity**: Medium
**Est tokens**: ~2M
**GTM value**: Complements #2 (mudmat) -- installation toolchain
**Target module**: `digitalmodel/install/manifold.py`

---

### 15. Passing Ship Force Calculator
**Source**: `acma-projects/_engineering/passing_ship/` (6 .xlsm + 1 .xlsx: Enhanced versions 1-5, Deep, test)
**Domain**: Hydrodynamic passing ship forces on moored vessels
**Complexity**: High
**Est tokens**: ~3M
**GTM value**: Unique calculation capability -- few have this in code
**Target module**: `digitalmodel/hydro/passing_ship.py`

---

### 16. Vessel Stability Analysis (ACMA B1512)
**Source**: `acma-projects/B1512/analysis/rev2/03_stability/` (10+ workbooks: Righting Arms, Offsets, Sail, Tanks, Gyradius)
**Domain**: Vessel intact stability per regulatory standards
**Complexity**: High
**Est tokens**: ~2.5M
**GTM value**: Naval architecture capability -- stability is fundamental
**Target module**: `digitalmodel/hydro/stability.py`

---

### 17. AQWA Damping Analysis Setup
**Source**: `acma-projects/_aqwa/` (2 .xlsm files)
**Domain**: AQWA hydrodynamic damping coefficient analysis
**Complexity**: High
**Est tokens**: ~2M
**GTM value**: AQWA integration is unique in the digitalmodel ecosystem
**Target module**: `digitalmodel/hydro/aqwa_damping.py`

---

### 18. Mooring Static Analysis Output Collation
**Source**: `acma-projects/B1512/analysis/rev2/05_mooring/output/` (4 workbooks: static 0dof, 3dof, template_general)
**Domain**: Mooring static results processing
**Complexity**: Medium
**Est tokens**: ~1.5M
**GTM value**: Mooring analysis results collation
**Target module**: `digitalmodel/mooring/post_process.py`

---

### 19. RAO Data Processing (ACMA)
**Source**: `acma-projects/calculations/raos/` (3 workbooks) + `client_projects/ecs/proj/9645/` (SHI RAO curves)
**Domain**: Response Amplitude Operator data QA and curve processing
**Complexity**: Medium
**Est tokens**: ~1.5M
**GTM value**: RAO processing feeds every hydrodynamic analysis
**Target module**: `digitalmodel/hydro/rao_processing.py`

---

### 20. FDAS Riser Analysis Load/RAO (0127/1000yr)
**Source**: `/mnt/ace/client_projects/0163-FDAS/FDAS/Engineering/ace/LoadRAO/0127/` (0127-CAL-0014-05 Riser Analysis, 0127-CAL-0022-01 RAO's)
**Domain**: Riser analysis with load case RAO processing
**Complexity**: High
**Est tokens**: ~2.5M
**GTM value**: Riser/RAO integration
**Target module**: `digitalmodel/riser/load_rao.py`

---

### 21. Production Engineering Reference Library
**Source**: `client_projects/energy_engineering/014 ProductionEngineering/Ref/CAL/` (48 .xls files covering full production engineering toolkit)
**Domain**: ESP design, gas lift, PVT, nodal analysis, compression, SRP, hydraulics, wellhead/bottomhole models, multilateral deliverability
**Complexity**: Medium-High per workbook, Low per individual
**Est tokens**: ~6M (entire library)
**GTM value**: Production engineering is a HUGE domain -- converting all 48 creates a complete production engineering Python library
**Target modules**: `assetutilities/production/` (esp_design, gas_lift, nodal_analysis, pvt, compression, srp, hydraulics)
**NOTE**: These are already in client_projects repo. Can be done incrementally, one sub-domain at a time.

---

### 22. Sucker Rod Pumping + Dynacard Analysis
**Source**: `client_projects/energy_firm_data_analytics/dynacard/srp/` (10 workbooks) + main production eng SRP sheets
**Domain**: Dynamometer card analysis, pump efficiency, gas anchor, TAC calculations
**Complexity**: Medium
**Est tokens**: ~2M
**GTM value**: Artificial lift optimization
**Target module**: `assetutilities/production/dynacard.py`

---

### 23. Umbilical Reference: ONGC Standard
**Source**: `/mnt/ace/rock-oil-field/s7/analysis_general/_ref/umbilical/ongc/` (9 workbooks: initiation, 1st/2nd end, deck handling, static, inputs)
**Domain**: Umbilical installation reference templates
**Complexity**: Medium
**Est tokens**: ~2M
**GTM value**: Reference methodology for umbilical installation
**Target module**: `digitalmodel/umbilical/reference/`

---

### 24. Lift and Lowering Installation Reference
**Source**: `/mnt/ace/rock-oil-field/s7/analysis_general/_ref/installations/` (5 workbooks: PLET MM lowering velocity, SafeLink, stiffness calc, resinance period)
**Domain**: Installation lifting and lowering methodology
**Complexity**: Medium
**Est tokens**: ~1.5M
**GTM value**: General installation methodology
**Target module**: `digitalmodel/install/lowering.py`

---

### 25. VMCast Metocean Duration Analysis
**Source**: `/mnt/ace/rock-oil-field/s7/BP_MD2_FJR/` (9 workbooks)
**Domain**: Vessel motion-based operational window analysis with metocean scatter tables
**Complexity**: Medium
**Est tokens**: ~2M
**GTM value**: Operability/meteocean duration calc
**Target module**: `digitalmodel/metocean/operability.py`

---

### 26. Pipe Burst/Collapse and Drilling Calcs (FDAS)
**Source**: `/mnt/ace/client_projects/0163-FDAS/FDAS/Engineering/Calculation Spreadsheets/` (multiple: Pipe Burst and Collapse, MASP, kill calcs, casing sizing, gas gradient)
**Domain**: Casing/drilling riser pressure ratings
**Complexity**: Medium
**Est tokens**: ~2M
**GTM value**: Casing/drilling analysis basics
**Target module**: `digitalmodel/casing/pressure_rating.py`

---

## BUDGET SUMMARY TABLE

| Rank | Workbook/Domain | Files | Effort | ~M Tokens | GTM Value | Already in CP repo? |
|------|----------------|-------|--------|-----------|-----------|---------------------|
| 1 | Ballymore Jumper | 1 | Medium | 1.5 | Demo ready | NO - needs copy |
| 2 | Ballymore SUT Mudmat | 5 | High | 3.0 | Reusable tool | NO |
| 3 | Ballymore PLET-LEM Jumper | 2 | Medium | 1.5 | Complements #1 | NO |
| 4 | FDAS Riser Stroke-Stretch | 3+ | High | 2.5 | Demo ready | NO (raw) |
| 5 | FDAS Riser Sizing/TT | 3+ | Medium | 1.5 | Universal | NO (raw) |
| 6 | FDAS Plate Buckling | 1 | High | 2.5 | Structural demo | YES |
| 7 | SEWOL ANSYS Buckling | 1 | High | 2.5 | Structural demo | YES |
| 8 | Padeye/Lifting (EPIC) | 4 | Medium | 1.5 | Universal | NO (raw) |
| 9 | FDAS Riser Assembly | 14+ | High | 3.0 | Deepwater demo | NO (raw) |
| 10 | Intervention Riser Abaqus | 10+ | High | 3.0 | Model gen | YES |
| 11 | SCR Design (DNV OS F201) | 12+ | High | 4.0 | Major deliverable | NO (raw) |
| 12 | DNV WTD/Monte Carlo | 6+ | Medium | 1.5 | Fundamental | NO (raw) |
| 13 | Talos Venice Umbilical | 31 | High | 4.0 | Full workflow | NO (raw) |
| 14 | Shell Perdido Manifold | 14 | Medium | 2.0 | Installation | NO (raw) |
| 15 | Passing Ship Forces | 6+ | High | 3.0 | Unique capability | YES (acma) |
| 16 | Vessel Stability (B1512) | 10+ | High | 2.5 | Naval arch | YES (acma) |
| 17 | AQWA Damping Setup | 2 | High | 2.0 | AQWA integration | YES (acma) |
| 18 | Mooring Static Output | 4 | Medium | 1.5 | Mooring domain | YES (acma) |
| 19 | RAO Processing | 5 | Medium | 1.5 | Hydro base | Mixed |
| 20 | FDAS Load/RAO Analysis | 2 | High | 2.5 | Riser/RAO | NO (raw) |
| 21 | Production Eng Library | 48 | Mixed | 6.0 | HUGE domain | YES |
| 22 | SRP/Dynacard Library | 10+ | Medium | 2.0 | Artificial lift | YES |
| 23 | ONGC Umbilical Refs | 9 | Medium | 2.0 | Installation ref | NO (raw) |
| 24 | Lift/Lowering Refs | 5 | Medium | 1.5 | Installation ref | NO (raw) |
| 25 | VMCast Operability | 9 | Medium | 2.0 | Metocean duration | NO (raw) |
| 26 | Pipe Burst/Drilling Calcs | 10+ | Medium | 2.0 | Casing/drilling | NO (raw) |

### Cumulative Token Budgets

| Up to Rank | Cumulative ~M Tokens | Workbooks Included |
|------------|---------------------|-------------------|
| 1-5 | 10M | Ballymore jumper set + FDAS riser basics |
| 1-10 | 22M | + Structural buckling, padeye, assembly models, Abaqus gen |
| 1-15 | 31M | + SCR design, umbilical installation, passing ship forces |
| 1-20 | 42M | + Stability, AQWA, mooring, RAO processing, Load/RAO |
| 1-26 (Full list) | ~65M | Everything |

### File Transfer Status: What Needs to Be Copied

| Source Location | Files | Destination in client_projects | Action |
|----------------|-------|-------------------------------|--------|
| `/mnt/ace/rock-oil-field/s7/ballymore/` | 10 | `ballymore/` | COPY NEEDED |
| `/mnt/ace/rock-oil-field/s7/talos_venice/` | 31 | `talos_venice/` | COPY NEEDED |
| `/mnt/ace/rock-oil-field/s7/shell_perdido_south/` | 14 | `shell_perdido_south/` | COPY NEEDED |
| `/mnt/ace/rock-oil-field/s7/analysis_general/_ref/epic/` | 4 | `engineering_tools/padeye/` | COPY NEEDED |
| `/mnt/ace/rock-oil-field/s7/analysis_general/_ref/installations/` | 5 | `engineering_tools/installation/` | COPY NEEDED |
| `/mnt/ace/rock-oil-field/s7/analysis_general/_ref/umbilical/ongc/` | 9 | `engineering_tools/umbilical_ongc/` | COPY NEEDED |
| `/mnt/ace/rock-oil-field/s7/analysis_general/train/SCR/` | 12 | `engineering_training/SCR_design/` | COPY NEEDED |
| `/mnt/ace/rock-oil-field/s7/analysis_general/train/wall_thickness/` | 6 | `engineering_training/wall_thickness/` | COPY NEEDED |
| `/mnt/ace/rock-oil-field/s7/BP_MD2_FJR/` | 9 | `BP_MD2_FJR/` | COPY NEEDED |
| `/mnt/ace/client_projects/0163-FDAS/` | 182 | `0163-FDAS/` (already in repo) | ALREADY TRACKED |
| `acma-projects/_engineering/passing_ship/` | 7 | `_engineering/passing_ship/` | NEEDS TRANSFER |
| `acma-projects/B1512/stability/` | 10+ | `B1512/stability/` | NEEDS TRANSFER |
| `acma-projects/_aqwa/` | 2 | `_aqwa/` | NEEDS TRANSFER |

Already in client_projects repo (133 xlsx): Production eng library (#21), dynacard (#22), plate buckling (#6,7), intervention riser (#10), ECS RAO curves, corrosion guides.
