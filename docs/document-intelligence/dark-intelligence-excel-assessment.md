     1|# Dark Intelligence: Excel Calculation Assessment & Promotion Map
     2|
     3|Generated: 2026-04-04
     4|
     5|## Executive Summary
     6|
     7|The workspace-hub ecosystem contains **~3,600 Excel calculation files** across mounted
     8|archives, **6 workbooks fully extracted** through the dark-intelligence pipeline, and
     9|**1,362 Python source files** in digitalmodel across 30 engineering domains. The gap
    10|between what exists in Excel and what has been promoted to code is massive — only
    11|**29 of 425 cataloged standards** have implementations, and digitalmodel sits at
    12|**2.95% test coverage**.
    13|
    14|This document maps the full landscape: what we have, what's been extracted, what's
    15|in code, and the prioritized path to close gaps.
    16|
    17|---
    18|
    19|## 1. SOURCE INVENTORY — Excel Calculations on Disk/Mounts
    20|
    21|### 1a. Riser Engineering Archive (/mnt/ace/)
    22|| Format | Count | Status              |
    23||--------|------:|---------------------|
    24|| .xls   | 3,550 | Cataloged, unprocessed |
    25|| .xlsx  |    43 | 10 selected for POC    |
    26|
    27|### 1b. ACMA Marine Engineering (CONTENT_INDEX)
    28|- 419 xlsx references across marine engineering projects
    29|- Domains: gyradius calcs, stability, mooring, diffraction output, ballast tanks
    30|
    31|### 1c. Standards/Codes Database
    32|- Codes & Standards Database.xls (legacy master index)
    33|- Houston Codes and Standards Priority List.xlsx
    34|- DNV Wall Thickness Sizing calculations
    35|
    36|### 1d. On-Disk in Repo (8 files)
    37|- 5 solver test fixtures (OrcaWave xlsx + owr pairs)
    38|- 3 queue/completed outputs (WAMIT validation)
    39|
    40|---
    41|
    42|## 2. DARK INTELLIGENCE PIPELINE — Current State
    43|
    44|### 2a. Infrastructure (Mature)
    45|```
    46|Scripts (12+ files):
    47|  parsers/formula_xlsx.py       ← Dual-pass XLSX loader (data + formulas)
    48|  formula_to_python.py          ← Translates 25+ Excel functions to Python
    49|  formula_chain_builder.py      ← NetworkX dependency DAG builder
    50|  formula_reference_parser.py   ← Cell reference parser
    51|  pattern_detector.py           ← Normalizes to row-1 canonical form
    52|  module_assembler.py           ← Assembles Python module per workbook
    53|  test_generator_v2.py          ← Baseline + 10 parametric variation tests
    54|  loop_collapse_generator.py    ← Collapses repeated rows into functions
    55|  vba_extractor.py              ← VBA source extraction from .xlsm
    56|  run_poc_extraction.py         ← POC v1 orchestrator
    57|  run_poc_v2.py                 ← POC v2 orchestrator
    58|```
    59|
    60|### 2b. Extraction Results (6 Workbooks Processed)
    61|
    62|| Workbook                        | Domain           | Formulas | Compression | Status   |
    63||---------------------------------|------------------|----------|-------------|----------|
    64|| sn-curve-definitions            | Fatigue/Riser    |   6,264  |   44.4x     | Extracted |
    65|| flowback-calculator             | Production       | 647,447  |    2.5x     | Extracted |
    66|| surface-wellhead-sitp           | Well Integrity   |       3  |     —       | Extracted |
    67|| conductor-length-assessment     | Structural       |   2,699  |     —       | Extracted |
    68|| spotfire-formulas               | Portfolio/Data   |     222  |     —       | Extracted |
    69|| flow-rate-calculation           | Production       |       0  |     —       | Skipped   |
    70|
    71|Total: 656,635 formulas extracted → 187,093 tests generated
    72|
    73|### 2c. Geotechnical Archive (Manual)
    74|- API RP 2GEO Alpha Method → Full YAML archive with equations, inputs, outputs,
    75|  worked examples (knowledge/dark-intelligence/geotechnical/)
    76|
    77|### 2d. Pipeline Gap
    78|- POC v2 generated calculations.py with TODO stubs — NOT fully wired
    79|- No feedback loop from generated code → digitalmodel modules
    80|- Generated code lives in knowledge/dark-intelligence/ (gitignored), not promoted
    81|
    82|---
    83|
    84|## 3. DIGITALMODEL — Current Code Coverage by Domain
    85|
    86|### 3a. Module File Counts (1,362 source files across 30 domains)
    87|
    88|| Domain               | Files | Standards Done | Standards Gap | Functions |
    89||----------------------|------:|---------------:|--------------:|----------:|
    90|| solvers              |   274 |        —       |       —       |     —     |
    91|| structural           |   166 |       12       |      24       |    739    |
    92|| hydrodynamics        |   154 |        0       |       —       |    825    |
    93|| infrastructure       |   135 |        —       |       —       |     —     |
    94|| marine_ops           |    92 |        3       |       2       |    510    |
    95|| workflows            |    76 |        —       |       —       |     —     |
    96|| subsea               |    60 |        6       |       —       |    325    |
    97|| visualization        |    48 |        —       |       —       |     —     |
    98|| asset_integrity      |    47 |        4       |       —       |    393    |
    99|| data_systems         |    41 |        —       |       —       |     —     |
   100|| specialized          |    38 |        —       |       —       |     —     |
   101|| web                  |    36 |        —       |       —       |     —     |
   102|| orcaflex             |    22 |        —       |       —       |     —     |
   103|| gis                  |    21 |        —       |       —       |     —     |
   104|| naval_architecture   |    20 |        —       |       —       |     —     |
   105|| signal_processing    |    19 |        —       |       —       |     —     |
   106|| orcawave             |    17 |        —       |       —       |     —     |
   107|| cathodic_protection  |    16 |        3       |       2       |     30    |
   108|| fatigue              |    15 |        —       |       —       |     —     |
   109|| ansys                |    14 |        —       |       —       |     —     |
   110|| power                |    12 |        —       |       —       |     —     |
   111|| field_development    |     8 |        —       |       —       |     —     |
   112|| production_eng       |     7 |        —       |       —       |     —     |
   113|| well                 |     4 |        —       |       —       |     —     |
   114|| geotechnical         |     4 |        2       |       —       |     13    |
   115|| drilling_riser       |     4 |        —       |       —       |     —     |
   116|
   117|### 3b. Standards Transfer Ledger (425 entries)
   118|
   119|| Status       | Count | Meaning                           |
   120||--------------|------:|-----------------------------------|
   121|| done         |    29 | Implemented in digitalmodel       |
   122|| gap          |   235 | Cataloged, no implementation      |
   123|| wrk_captured |    ~80| Work item created, not started    |
   124|| reference    |    ~81| Reference only, not for coding    |
   125|
   126|### 3c. Test Coverage
   127|| Repo             | Coverage |
   128||------------------|----------|
   129|| digitalmodel     |   2.95%  |
   130|| worldenergydata  |  40.42%  |
   131|| assetutilities   |  41.17%  |
   132|| assethold        |  76.86%  |
   133|
   134|---
   135|
   136|## 4. EXCEL → CODE PROMOTION MAP
   137|
   138|### 4a. What Connects to What
   139|
   140|```
   141|EXCEL SOURCE                    EXTRACTION              CODE TARGET
   142|─────────────                   ──────────              ───────────
   143|/mnt/ace/*.xls (3,593)    ──→  dark-intelligence/      ──→  digitalmodel/src/
   144|                                xlsx-poc/                     (1,362 files)
   145|                                xlsx-poc-v2/
   146|                                                        
   147|CONTENT_INDEX xlsx (419)   ──→  (not extracted yet)     ──→  (unmapped)
   148|
   149|Standards Database         ──→  standards-transfer-     ──→  29 done / 235 gap
   150|                                ledger.yaml
   151|
   152|Dark intelligence          ──→  YAML archive +          ──→  TODO stubs in
   153|workbook extractions            calc-report +                 calculations.py
   154|(6 workbooks)                   patterns.yaml                 (not promoted)
   155|```
   156|
   157|### 4b. Existing Excel Utility Code in digitalmodel
   158|
   159|| Module Path                                          | Purpose                    |
   160||------------------------------------------------------|----------------------------|
   161|| infrastructure/utils/excel_utilities.py              | ReadFromExcel (pandas)     |
   162|| infrastructure/common/excel_utilities.py             | Common Excel utils         |
   163|| marine_ops/marine_analysis/analysis/excel_analyzer.py| Marine XLSM analyzer       |
   164|| solvers/orcaflex/browser/excel_reader.py             | OrcaFlex Excel collation   |
   165|| asset_integrity/common/DataFrame_To_xlsx.py          | DataFrame → Excel writer   |
   166|| solvers/orcaflex/post_results/xlsx_To_DataFrame.py   | Excel → DataFrame reader   |
   167|| legacy/analyze_marine_excel.py                       | XLSM formula+VBA analyzer  |
   168|| legacy/extract_mooring_components.py                 | Chain/wire/line extraction  |
   169|| legacy/extract_hydro_coefficients.py                 | Hydro coefficient extract  |
   170|| legacy/extract_ocimf_database.py                     | OCIMF database extraction  |
   171|
   172|---
   173|
   174|## 5. DOMAIN GAP ANALYSIS — Excel Intelligence vs Code
   175|
   176|### Priority 1: HIGH-VALUE, HAVE EXCEL + PARTIAL CODE
   177|| Domain              | Excel Evidence           | Code State          | Gap Action             |
   178||---------------------|--------------------------|---------------------|------------------------|
   179|| Structural/Fatigue  | SN curves (6,264 formulas)| 166 files, 12 stds | Wire POC v2 output     |
   180|| Cathodic Protection | 19 standards cataloged   | 16 files, 3 done   | Extract remaining 2 gaps|
   181|| Marine/Mooring      | 419 CONTENT_INDEX refs   | 92+60 files         | Map xlsx → module gaps |
   182|| Asset Integrity/FFS | Wall thickness xlsx      | 47 files, 4 stds   | API 579 Excel → code   |
   183|
   184|### Priority 2: HAVE EXCEL, MINIMAL CODE
   185|| Domain              | Excel Evidence           | Code State          | Gap Action             |
   186||---------------------|--------------------------|---------------------|------------------------|
   187|| Production Eng      | Flowback calc (647K fml) | 7 files             | Promote POC v2 output  |
   188|| Drilling            | 9 standards, 8 gaps      | 4 files             | Target conductor calc  |
   189|| Geotechnical        | API RP 2GEO archived     | 4 files, 2 done    | Archive → module wire  |
   190|| Well Integrity      | SITP calc (3 formulas)   | 4 files             | Direct promotion       |
   191|
   192|### Priority 3: HAVE EXCEL, NO CODE
   193|| Domain              | Excel Evidence           | Code State          | Gap Action             |
   194||---------------------|--------------------------|---------------------|------------------------|
   195|| Materials           | 122 standards, 93 gaps   | 0 implemented       | Bulk extraction needed |
   196|| Process             | 55 standards, 53 gaps    | 0 implemented       | Bulk extraction needed |
   197|| CAD                 | 23 standards, 22 gaps    | 0 implemented       | Low priority           |
   198|| Installation        | 22 standards, 11 gaps    | 0 implemented       | Medium priority        |
   199|
   200|---
   201|
   202|## 6. RECOMMENDED EXECUTION PLAN
   203|
   204|### Phase 1: Wire Existing Extractions (Quick Wins)
   205|1. Promote xlsx-poc-v2 calculations.py → digitalmodel modules
   206|   - SN curve definitions → fatigue/sn_curves.py
   207|   - Conductor length → structural/conductor.py
   208|   - Surface wellhead SITP → well/sitp.py
   209|2. Wire geotechnical YAML archive → geotechnical/pile_capacity.py
   210|3. Update standards-transfer-ledger.yaml status for promoted items
   211|
   212|### Phase 2: Extract High-Value Unprocessed Excel (Batch)
   213|1. Run dark-intelligence pipeline on CONTENT_INDEX xlsx files
   214|   - Target: mooring calcs, stability calcs, gyradius calcs
   215|2. Run pipeline on remaining 4 skipped POC files (>15MB)
   216|3. Extract /mnt/ace/ riser engineering priority files
   217|   - Target: 3837-CAL series (403+ formulas)
   218|
   219|### Phase 3: Standards Gap Closure (Systematic)
   220|1. Process 235 gap entries in standards-transfer-ledger.yaml
   221|2. For each: check if Excel source exists → extract → promote → test
   222|3. Target: 10 standards/month = close all gaps in ~24 months
   223|
   224|### Phase 4: Test Coverage Uplift
   225|1. Use dark-intelligence test generators for existing modules
   226|2. Target: digitalmodel 2.95% → 20% in 6 months
   227|3. Wire parametric variation tests from xlsx-poc-v2
   228|
   229|---
   230|
   231|## 7. KEY FILES & REGISTRIES
   232|
   233|| Asset                                    | Path                                              |
   234||------------------------------------------|----------------------------------------------------|
   235|| Standards Transfer Ledger                | data/document-index/standards-transfer-ledger.yaml |
   236|| Domain Coverage Report                   | docs/document-intelligence/domain-coverage.md      |
   237|| Calculations Vision                      | docs/vision/CALCULATIONS-VISION.md                 |
   238|| Dark Intelligence Archives               | knowledge/dark-intelligence/                       |
   239|| Doc Intelligence Scripts                 | scripts/data/doc_intelligence/                     |
   240|| Design Code Registry                     | data/design-codes/code-registry.yaml               |
   241|| CONTENT_INDEX (Excel refs)               | docs/CONTENT_INDEX.md                              |
   242|| Skill Graph Index                        | config/agents/skill-graph-index.yaml               |
   243|| Algorithm Extraction Plan                | .planning/algorithm-extraction.md                  |
   244|| Excel Translation Plan                   | docs/plans/2026-01-19-excel-translation.md         |
   245|| Dark Intelligence Schema                 | config/schemas/dark-intelligence-archive.yaml      |
   246|| digitalmodel Coverage Map                | digitalmodel/_coverage_map.py                      |
   247|
