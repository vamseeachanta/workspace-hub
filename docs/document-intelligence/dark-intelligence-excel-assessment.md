# Dark Intelligence: Excel Calculation Assessment & Promotion Map

Generated: 2026-04-04

## Executive Summary

The workspace-hub ecosystem contains **~3,600 Excel calculation files** across mounted
archives, **6 workbooks fully extracted** through the dark-intelligence pipeline, and
**1,362 Python source files** in digitalmodel across 30 engineering domains. The gap
between what exists in Excel and what has been promoted to code is massive — only
**29 of 425 cataloged standards** have implementations, and digitalmodel sits at
**2.95% test coverage**.

This document maps the full landscape: what we have, what's been extracted, what's
in code, and the prioritized path to close gaps.

---

## 1. SOURCE INVENTORY — Excel Calculations on Disk/Mounts

### 1a. Riser Engineering Archive (/mnt/ace/)
| Format | Count | Status              |
|--------|------:|---------------------|
| .xls   | 3,550 | Cataloged, unprocessed |
| .xlsx  |    43 | 10 selected for POC    |

### 1b. ACMA Marine Engineering (CONTENT_INDEX)
- 419 xlsx references across marine engineering projects
- Domains: gyradius calcs, stability, mooring, diffraction output, ballast tanks

### 1c. Standards/Codes Database
- Codes & Standards Database.xls (legacy master index)
- Houston Codes and Standards Priority List.xlsx
- DNV Wall Thickness Sizing calculations

### 1d. On-Disk in Repo (8 files)
- 5 solver test fixtures (OrcaWave xlsx + owr pairs)
- 3 queue/completed outputs (WAMIT validation)

---

## 2. DARK INTELLIGENCE PIPELINE — Current State

### 2a. Infrastructure (Mature)
```
Scripts (12+ files):
  parsers/formula_xlsx.py       ← Dual-pass XLSX loader (data + formulas)
  formula_to_python.py          ← Translates 25+ Excel functions to Python
  formula_chain_builder.py      ← NetworkX dependency DAG builder
  formula_reference_parser.py   ← Cell reference parser
  pattern_detector.py           ← Normalizes to row-1 canonical form
  module_assembler.py           ← Assembles Python module per workbook
  test_generator_v2.py          ← Baseline + 10 parametric variation tests
  loop_collapse_generator.py    ← Collapses repeated rows into functions
  vba_extractor.py              ← VBA source extraction from .xlsm
  run_poc_extraction.py         ← POC v1 orchestrator
  run_poc_v2.py                 ← POC v2 orchestrator
```

### 2b. Extraction Results (6 Workbooks Processed)

| Workbook                        | Domain           | Formulas | Compression | Status   |
|---------------------------------|------------------|----------|-------------|----------|
| sn-curve-definitions            | Fatigue/Riser    |   6,264  |   44.4x     | Extracted |
| flowback-calculator             | Production       | 647,447  |    2.5x     | Extracted |
| surface-wellhead-sitp           | Well Integrity   |       3  |     —       | Extracted |
| conductor-length-assessment     | Structural       |   2,699  |     —       | Extracted |
| spotfire-formulas               | Portfolio/Data   |     222  |     —       | Extracted |
| flow-rate-calculation           | Production       |       0  |     —       | Skipped   |

Total: 656,635 formulas extracted → 187,093 tests generated

### 2c. Geotechnical Archive (Manual)
- API RP 2GEO Alpha Method → Full YAML archive with equations, inputs, outputs,
  worked examples (knowledge/dark-intelligence/geotechnical/)

### 2d. Pipeline Gap
- POC v2 generated calculations.py with TODO stubs — NOT fully wired
- No feedback loop from generated code → digitalmodel modules
- Generated code lives in knowledge/dark-intelligence/ (gitignored), not promoted

---

## 3. DIGITALMODEL — Current Code Coverage by Domain

### 3a. Module File Counts (1,362 source files across 30 domains)

| Domain               | Files | Standards Done | Standards Gap | Functions |
|----------------------|------:|---------------:|--------------:|----------:|
| solvers              |   274 |        —       |       —       |     —     |
| structural           |   166 |       12       |      24       |    739    |
| hydrodynamics        |   154 |        0       |       —       |    825    |
| infrastructure       |   135 |        —       |       —       |     —     |
| marine_ops           |    92 |        3       |       2       |    510    |
| workflows            |    76 |        —       |       —       |     —     |
| subsea               |    60 |        6       |       —       |    325    |
| visualization        |    48 |        —       |       —       |     —     |
| asset_integrity      |    47 |        4       |       —       |    393    |
| data_systems         |    41 |        —       |       —       |     —     |
| specialized          |    38 |        —       |       —       |     —     |
| web                  |    36 |        —       |       —       |     —     |
| orcaflex             |    22 |        —       |       —       |     —     |
| gis                  |    21 |        —       |       —       |     —     |
| naval_architecture   |    20 |        —       |       —       |     —     |
| signal_processing    |    19 |        —       |       —       |     —     |
| orcawave             |    17 |        —       |       —       |     —     |
| cathodic_protection  |    16 |        3       |       2       |     30    |
| fatigue              |    15 |        —       |       —       |     —     |
| ansys                |    14 |        —       |       —       |     —     |
| power                |    12 |        —       |       —       |     —     |
| field_development    |     8 |        —       |       —       |     —     |
| production_eng       |     7 |        —       |       —       |     —     |
| well                 |     4 |        —       |       —       |     —     |
| geotechnical         |     4 |        2       |       —       |     13    |
| drilling_riser       |     4 |        —       |       —       |     —     |

### 3b. Standards Transfer Ledger (425 entries)

| Status       | Count | Meaning                           |
|--------------|------:|-----------------------------------|
| done         |    29 | Implemented in digitalmodel       |
| gap          |   235 | Cataloged, no implementation      |
| wrk_captured |    ~80| Work item created, not started    |
| reference    |    ~81| Reference only, not for coding    |

### 3c. Test Coverage
| Repo             | Coverage |
|------------------|----------|
| digitalmodel     |   2.95%  |
| worldenergydata  |  40.42%  |
| assetutilities   |  41.17%  |
| assethold        |  76.86%  |

---

## 4. EXCEL → CODE PROMOTION MAP

### 4a. What Connects to What

```
EXCEL SOURCE                    EXTRACTION              CODE TARGET
─────────────                   ──────────              ───────────
/mnt/ace/*.xls (3,593)    ──→  dark-intelligence/      ──→  digitalmodel/src/
                                xlsx-poc/                     (1,362 files)
                                xlsx-poc-v2/
                                                        
CONTENT_INDEX xlsx (419)   ──→  (not extracted yet)     ──→  (unmapped)

Standards Database         ──→  standards-transfer-     ──→  29 done / 235 gap
                                ledger.yaml

Dark intelligence          ──→  YAML archive +          ──→  TODO stubs in
workbook extractions            calc-report +                 calculations.py
(6 workbooks)                   patterns.yaml                 (not promoted)
```

### 4b. Existing Excel Utility Code in digitalmodel

| Module Path                                          | Purpose                    |
|------------------------------------------------------|----------------------------|
| infrastructure/utils/excel_utilities.py              | ReadFromExcel (pandas)     |
| infrastructure/common/excel_utilities.py             | Common Excel utils         |
| marine_ops/marine_analysis/analysis/excel_analyzer.py| Marine XLSM analyzer       |
| solvers/orcaflex/browser/excel_reader.py             | OrcaFlex Excel collation   |
| asset_integrity/common/DataFrame_To_xlsx.py          | DataFrame → Excel writer   |
| solvers/orcaflex/post_results/xlsx_To_DataFrame.py   | Excel → DataFrame reader   |
| legacy/analyze_marine_excel.py                       | XLSM formula+VBA analyzer  |
| legacy/extract_mooring_components.py                 | Chain/wire/line extraction  |
| legacy/extract_hydro_coefficients.py                 | Hydro coefficient extract  |
| legacy/extract_ocimf_database.py                     | OCIMF database extraction  |

---

## 5. DOMAIN GAP ANALYSIS — Excel Intelligence vs Code

### Priority 1: HIGH-VALUE, HAVE EXCEL + PARTIAL CODE
| Domain              | Excel Evidence           | Code State          | Gap Action             |
|---------------------|--------------------------|---------------------|------------------------|
| Structural/Fatigue  | SN curves (6,264 formulas)| 166 files, 12 stds | Wire POC v2 output     |
| Cathodic Protection | 19 standards cataloged   | 16 files, 3 done   | Extract remaining 2 gaps|
| Marine/Mooring      | 419 CONTENT_INDEX refs   | 92+60 files         | Map xlsx → module gaps |
| Asset Integrity/FFS | Wall thickness xlsx      | 47 files, 4 stds   | API 579 Excel → code   |

### Priority 2: HAVE EXCEL, MINIMAL CODE
| Domain              | Excel Evidence           | Code State          | Gap Action             |
|---------------------|--------------------------|---------------------|------------------------|
| Production Eng      | Flowback calc (647K fml) | 7 files             | Promote POC v2 output  |
| Drilling            | 9 standards, 8 gaps      | 4 files             | Target conductor calc  |
| Geotechnical        | API RP 2GEO archived     | 4 files, 2 done    | Archive → module wire  |
| Well Integrity      | SITP calc (3 formulas)   | 4 files             | Direct promotion       |

### Priority 3: HAVE EXCEL, NO CODE
| Domain              | Excel Evidence           | Code State          | Gap Action             |
|---------------------|--------------------------|---------------------|------------------------|
| Materials           | 122 standards, 93 gaps   | 0 implemented       | Bulk extraction needed |
| Process             | 55 standards, 53 gaps    | 0 implemented       | Bulk extraction needed |
| CAD                 | 23 standards, 22 gaps    | 0 implemented       | Low priority           |
| Installation        | 22 standards, 11 gaps    | 0 implemented       | Medium priority        |

---

## 6. RECOMMENDED EXECUTION PLAN

### Phase 1: Wire Existing Extractions (Quick Wins)
1. Promote xlsx-poc-v2 calculations.py → digitalmodel modules
   - SN curve definitions → fatigue/sn_curves.py
   - Conductor length → structural/conductor.py
   - Surface wellhead SITP → well/sitp.py
2. Wire geotechnical YAML archive → geotechnical/pile_capacity.py
3. Update standards-transfer-ledger.yaml status for promoted items

### Phase 2: Extract High-Value Unprocessed Excel (Batch)
1. Run dark-intelligence pipeline on CONTENT_INDEX xlsx files
   - Target: mooring calcs, stability calcs, gyradius calcs
2. Run pipeline on remaining 4 skipped POC files (>15MB)
3. Extract /mnt/ace/ riser engineering priority files
   - Target: 3837-CAL series (403+ formulas)

### Phase 3: Standards Gap Closure (Systematic)
1. Process 235 gap entries in standards-transfer-ledger.yaml
2. For each: check if Excel source exists → extract → promote → test
3. Target: 10 standards/month = close all gaps in ~24 months

### Phase 4: Test Coverage Uplift
1. Use dark-intelligence test generators for existing modules
2. Target: digitalmodel 2.95% → 20% in 6 months
3. Wire parametric variation tests from xlsx-poc-v2

---

## 7. KEY FILES & REGISTRIES

| Asset                                    | Path                                              |
|------------------------------------------|----------------------------------------------------|
| Standards Transfer Ledger                | data/document-index/standards-transfer-ledger.yaml |
| Domain Coverage Report                   | docs/document-intelligence/domain-coverage.md      |
| Calculations Vision                      | docs/vision/CALCULATIONS-VISION.md                 |
| Dark Intelligence Archives               | knowledge/dark-intelligence/                       |
| Doc Intelligence Scripts                 | scripts/data/doc_intelligence/                     |
| Design Code Registry                     | data/design-codes/code-registry.yaml               |
| CONTENT_INDEX (Excel refs)               | docs/CONTENT_INDEX.md                              |
| Skill Graph Index                        | config/agents/skill-graph-index.yaml               |
| Algorithm Extraction Plan                | .planning/algorithm-extraction.md                  |
| Excel Translation Plan                   | docs/plans/2026-01-19-excel-translation.md         |
| Dark Intelligence Schema                 | config/schemas/dark-intelligence-archive.yaml      |
| digitalmodel Coverage Map                | digitalmodel/_coverage_map.py                      |
