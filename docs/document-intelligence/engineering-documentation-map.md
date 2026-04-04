# Engineering Documentation Map — Complete Inventory
# Generated: 2026-04-04 by documentation audit subagent
# Scope: Field Development, Naval Architecture, Geotechnical Engineering

---

## EXECUTIVE SUMMARY

### Global Statistics
- **Total indexed documents**: 1,033,933 records in index.jsonl
- **Total summaries extracted**: 639,585 (61.9% coverage)
- **Standards in transfer ledger**: 425 (29 done, 23 WRK-captured, 235 gap, 138 reference)
- **Conference papers (unindexed)**: 38,526 files across 30 conferences
- **Literature on DDE remote**: 14,620 MB (5,456 PDFs across Engineering + Oil & Gas)
- **Standards on ACE drive**: 27,513 organized files (11,289 MB) across 11 orgs
- **Standards on DDE drive**: 28,000+ files across 36 orgs (18 orgs unique to DDE)
- **Doc-intelligence deep extractions**: 9 deep reports, 44+ naval architecture extraction reports
- **Structured extracts**: 12M requirements, 4.9M constants, 2M equations, 1.4M procedures, 717K definitions, 279K worked examples

### Status by Interest Domain

| Domain | Downloaded PDFs | Cataloged/Not Downloaded | Standards (done/gap) | Deep Extractions | Dark Intelligence |
|--------|----------------|--------------------------|---------------------|------------------|-------------------|
| Naval Architecture | 17 textbooks + 10 hydrostatics + 110 ship plans + 2 regulatory + 5 DNV/additional | 23 resources not started | 33 marine stds (4 done, 2 gap) | 44+ extraction reports | None specific |
| Field Development (O&G) | 0 local docs indexed | 29 resources all not_started | 55 pipeline (12 done, 13 gap) | 2 deep reports (API 1111, DNV F105) | 6 Excel extractions |
| Geotechnical | 1 dark-intelligence extraction | 0 specific resources cataloged | API RP 2GEO (reference) | 1 deep (API RP 2A WSD) | API RP 2GEO alpha method |
| Structural | 50,001 local docs indexed | 30 resources not_started | 72 stds (4 done, 24 gap) | 4 deep reports | SN-curve riser analysis |

---

## 1. NAVAL ARCHITECTURE — Detailed Inventory

### 1.1 Downloaded PDFs (Located on /mnt/ace/docs/_standards/SNAME/)

#### Textbooks (17 PDFs, ~570 MB total)
1. Principles of Naval Architecture Vol I — Stability & Strength (SNAME, ~1988) — 29 MB
2. Principles of Naval Architecture Vol II — Resistance, Propulsion & Vibration (SNAME) — 30 MB
3. PNA Vol II (Internet Archive higher-quality scan) — 84 MB
4. PNA Second Revision Vol I — 32 MB
5. PNA Second Revision Vol II — Resistance & Propulsion — 55 MB
6. PNA Second Revision Vol III — Motions & Controllability — 34 MB
7. Introduction to Naval Architecture (Tupper 1996) — 19 MB
8. Introduction to Naval Architecture (Comstock 1942) — 5.7 MB
9. Basic Ship Theory Vol 1 (Rawson & Tupper 2001) — 3.9 MB
10. Design Principles of Ships and Marine Structures — 18 MB
11. Engineering Mathematics for Ship Design — 20 MB
12. Hybrid Ship Hulls — Engineering Design — 6.7 MB
13. Ship Construction (Eyres 2001) — 17 MB
14. Jane's Fighting Ships 2009-2010 — 198 MB
15. ABS Introduction to Rules and Guides — 2.1 MB
16. Warship 2011 — Naval Submarines & UUVs — 31 MB
17. Warship — Naval Submarines Vol 9 — 22 MB

#### Hydrostatics, Stability & Resistance (10 PDFs, ~120 MB total)
1. Ship Hydrostatics and Stability (Biran, ~2003) — 9.3 MB
2. Ship Hydrostatics and Stability 2nd Ed (Biran & Lopez Pulido, ~2014) — 10 MB
3. PNA Series — Ship Resistance and Flow (~2010) — 9.7 MB
4. Marine Hydrodynamics (Newman 2018) — 11 MB
5. Practical Ship Hydrodynamics (Bertram 2000) — 2.2 MB
6. Fluid-Dynamic Drag (Hoerner 1965) — 22 MB
7. Handbook of Offshore Engineering (Chakrabarti 2005) — 36 MB
8. Offshore Hydromechanics (Journee & Massie 2001) — 12 MB
9. Ship Hydromechanics Introduction — 3.5 MB
10. PNA — GZ Curves — 1.8 MB

#### Ship Plans (110 PDFs from maritime.org)
- Historical US Navy/Allied vessel general arrangement drawings (1863-2008)
- Located: /mnt/ace/docs/_standards/SNAME/ship-plans/

#### Additional Resources (Downloaded)
- USNA EN400 Principles of Ship Performance Course Notes (2020) — 9.6 MB
- Text-book of Theoretical Naval Architecture (Attwood 1899) — 12 MB
- Ship Structural Analysis and Design (Hughes & Paik) — 14 MB
- DNV-RP-C205 Environmental Conditions & Loads (2007) — 2.9 MB
- DNV-RP-H103 Marine Operations (2010) — 2.4 MB

#### Regulatory (Downloaded)
- UK MCA MSIS43 Intact Stability Guidance (2023) — 4.7 MB
- SOLAS 2020 Consolidated Edition — 2.1 MB

### 1.2 Cataloged but NOT Downloaded (23 items)
- ABS Marine Vessel Rules Part 4 (2024) — WAF blocks wget
- Aalto University Lecture Notes on Basic Naval Architecture (2021, CC BY)
- Bureau Veritas Rules (130+ publications)
- ClassNK Technical Rules (complete set)
- DTIC Engineering for Ship Production — DTIC blocks wget
- DTIC Small Craft Design Guide (1977) — DTIC blocks wget
- IMO Guidelines on Intact Stability 2014 — download failed
- Internet Archive Naval Architecture Collection
- Introduction to Naval Architecture (Gillmer & Johnson) — borrow-only
- Lloyd's Register Heritage Centre
- Lloyd's Register Rules for Classification (July 2022, Internet Archive)
- MIT OCW 2.019 Design of Ocean Systems Lecture Notes
- MIT OCW 2.20 Marine Hydrodynamics Lecture Notes (24 PDFs)
- University of Michigan Basic Naval Architecture Vol I & II — redirects wget
- RINA Transactions portal
- SNAME publications portal

### 1.3 Doc-Intelligence Extractions for Naval Architecture
- **44+ extraction reports** in data/doc-intelligence/extraction-reports/naval-architecture/
  - Covers all downloaded textbooks and ship plans
  - Reports include: equations, tables, worked examples, constants, procedures
- **Naval architecture catalog**: data/doc-intelligence/naval-architecture-catalog.yaml (144 docs, 110 ship plans, 21 textbooks, 65 hull codes)
- **Ship plans index**: data/doc-intelligence/ship-plans-index.yaml
- **EN400 worked examples**: data/doc-intelligence/en400-worked-examples.yaml
- **Ship dimensions**: data/doc-intelligence/ship-dimensions.yaml

---

## 2. FIELD DEVELOPMENT / OIL & GAS — Detailed Inventory

### 2.1 Downloaded Standards (on ACE drive)
Pipeline domain (12 done):
- API RP 1111 (Offshore Hydrocarbon Pipelines, Limit State Design)
- API RP 2RD (Design of Risers)
- API RP 5L (Line Pipe)
- API STD 2RD 2nd Ed (Dynamic Risers for Floating Production)
- DNV-OS-F101 (Submarine Pipeline Systems)
- DNV-OS-F201 (Dynamic Risers)
- DNV-RP-F105 (Free Spanning Pipelines)
- DNV-RP-F109 (On-bottom Stability)
- DNV-RP-F110 (Global Buckling)
- ISO 13624-1 (Risers)
- ISO 13628 (Completion/Workover)
- ISO 16389 (Dynamic Risers)

Marine domain (4 done):
- API RP 2I (Mooring Hardware Inspection)
- API RP 2P
- API RP 2SM (Synthetic Fiber Ropes for Mooring)
- DNV-OS-E301 (Position Mooring)

### 2.2 Literature on DDE Remote Drive (not yet migrated)
Engineering Literature (~8,640 MB, 823 PDFs):
- Reservoir engineering textbooks (Fundamentals of Reservoir Engineering, Reservoir Engineering Handbook 2E, etc.)
- Flow assurance references
- DNV-RP-B401 Cathodic Protection Design
- Structural, Soil, Riser Engineering directories (~400+ files in Structural/ alone)
- OTC 2004 conference papers (~20 files)
- Oil and Gas Codes directory (~15 files)

Oil & Gas Literature (~5,980 MB, 4,633 PDFs):
- Advanced Reservoir Engineering (Ahmed & McKinney, Elsevier 2005) — 9.7 MB
- Applied Petroleum Reservoir Engineering — 13.1 MB
- Quantitative Methods in Reservoir Engineering — 2.4 MB
- Reservoir Engineering Handbook (multiple editions) — 9.8 MB, 9.9 MB
- Oil & Gas Standard Handbook — 32 MB
- Rigtrain Manual — 78 MB
- Energy economics literature (Wiley Finance, Hirsch Report, etc.)
- Khori/BOOKS (~200 files, 700 MB) — structural textbooks
- Khori/STRUCTURAL BOOK (~100 files, 800 MB)
- 2006-07 Geotech Conference (~7 files, 8 MB)

### 2.3 Online Resources (All 29 Not Yet Started)
- BOEM, Baker Hughes Rig Count, EIA Open Data API v2 (score 5)
- SPE OnePetro (score 5)
- API MyCommittees, OPM Flow, ResInsight, Whitson+ (score 4)
- ANP Brazil, JODI, OPEC, USGS assessments (score 3)

### 2.4 Conference Papers (Unindexed — 38,526 total files)
Key conferences for field development:
- **OTC** (Offshore Technology Conference): 8,500 files, 5,432 PDFs, 7,946 MB (1988-2017)
- **OMAE**: 13,126 files, 7,292 PDFs, 8,345 MB (1998-2014)
- **ISOPE**: 4,516 files, 4,074 PDFs, 3,044 MB (2003-2014)
- **DOT** (Deep Offshore Technology): 7,516 files, 1,456 PDFs, 2,255 MB (2001-2013)
- **SPE**: 129 files, 124 PDFs, 116 MB
- **Subsea Tieback**: 214 files, 798 MB
- **DeepGulf**: 43 files, 42 PDFs
- **Rio Oil & Gas**: 66 PDFs, 31 MB

### 2.5 Standards on Drive (DDE + ACE)
ACE organized:
- API: 574 files (2,591 MB)
- ISO: 308 files (736 MB)
- DNV: 100 files (213 MB)
- SNAME: 145 files (1,417 MB)
- OnePetro: 94 files (129 MB)

DDE unique (not in ACE):
- ASCE: 404 files (4,534 MB) — CRITICAL, includes Deepwater Horizon Blue-Ribbon Panel
- ASME: 91 files (984 MB) — BPVC, B31.3, B31.4, B31.8
- AWS: 16 files (471 MB) — D1.1 Structural Welding Code
- NACE: 8 files (5 MB) — MR 0175 (H2S), corrosion papers
- HSE: 2 files (5 MB) — offshore fatigue guidance
- NFPA: 2 files (585 MB) — fire safety
- CFR: 9 files (155 MB) — US regulatory
- ISO (DDE delta): ~350 additional standards vs ACE

---

## 3. GEOTECHNICAL ENGINEERING — Detailed Inventory

### 3.1 Dark Intelligence Extractions
- **API RP 2GEO Alpha Method** (knowledge/dark-intelligence/geotechnical/pile_capacity/)
  - Full equation extraction: alpha factor, unit skin friction, total axial capacity
  - Worked example: 1.0m diameter pile, 30m long, firm clay
  - Test vectors with tolerances for validation
  - Source: API RP 2GEO Section 7.3

### 3.2 Related Standards Available
- API RP 2A-WSD (Fixed Offshore Platforms — includes pile design) — deep extraction done
- API RP 2GEO 1st Ed Addendum 1, Oct 2014 — cataloged as reference
- Design of Large Diameter Monopiles under Lateral Loads — cataloged
- Soil directory on DDE: /mnt/remote/ace-linux-2/dde/Literature/Engineering/Soil (~5 files)
- 2006-07 Geotech Conference on DDE: ~7 files, 8 MB

### 3.3 Deep Extraction Reports Relevant
- API RP 2A WSD Offshore Platforms — deep extraction done (includes geotechnical sections)

### 3.4 Gaps
- No dedicated geotechnical textbooks downloaded yet (e.g., Das, Bowles, Tomlinson)
- API RP 2GEO full document not in standards ledger as "done"
- No specific pile design software tools cataloged
- OpenSees cataloged for structural/geotechnical FEM but not downloaded

---

## 4. DOC-INTELLIGENCE EXTRACTION STATUS

### 4.1 Phase B Structured Extracts (Bulk)
| Extract Type | Records | File |
|-------------|---------|------|
| Requirements | 12.0M | data/doc-intelligence/requirements.jsonl |
| Constants | 4.9M | data/doc-intelligence/constants.jsonl |
| Equations | 2.0M | data/doc-intelligence/equations.jsonl |
| Procedures | 1.4M | data/doc-intelligence/procedures.jsonl |
| Definitions | 717K | data/doc-intelligence/definitions.jsonl |
| Worked examples | 279K | data/doc-intelligence/worked_examples.jsonl |

### 4.2 Deep Extraction Reports (9 standards)
1. API 579-1/ASME FFS-1 (2016) — fitness for service
2. API RP 1111 4th Ed (2009) — offshore hydrocarbon pipelines
3. API RP 2A WSD (2000) — fixed offshore platforms (includes geotechnical)
4. API RP 2SK 3rd Ed (2005) — stationkeeping systems
5. DNV RP B401 (2011) — cathodic protection design
6. DNV RP C203 (2011) — fatigue design of offshore steel
7. DNV RP C205 (2007) — environmental conditions and loads
8. DNV RP F105 (2002) — free spanning pipelines
9. DNV RP F109 (2011) — on-bottom stability

### 4.3 Naval Architecture Extraction Reports (44+)
Full extraction reports for all textbooks and ship plans in the collection.

### 4.4 Table Extractions
- ABS Intro to Rules tables (6 CSVs)
- ASME 31G tables (20 CSVs)
- GEOBASE NHNC1 tables (multiple CSVs)
- Domain-organized deep tables: cathodic-protection, fatigue, marine, mooring, pipeline, structural

### 4.5 Dark Intelligence Excel Extractions (6 spreadsheets, 2 generations)
POC v1 and v2 extractions with Python re-implementations:
1. Surface wellhead SITP calculations (0163-cal-0001)
2. Conductor length assessment (31126-cal-0001)
3. SN curve definitions for riser analysis (31245-cal-0018)
4. C-K flow rate calculation
5. Flowback calculator (cc-23-6h)
6. Spotfire formulas for calc variables

---

## 5. MOUNTED SOURCE REGISTRY (10 sources)

| Source ID | Mount Root | Type | Content |
|-----------|-----------|------|---------|
| workspace_hub_local | /mnt/local-analysis/workspace-hub | local | In-repo specs and configs |
| ace_standards_local | /mnt/ace/docs/_standards | local | Standards library |
| og_standards_local | /mnt/ace/0000 O&G | local | O&G standards collection |
| ace_project_local | /mnt/ace/docs | local | Project documents |
| research_literature_local | /mnt/ace-data/digitalmodel/docs/domains | local | Domain-organized literature |
| riser_eng_job_local | /mnt/ace/digitalmodel/.../riser-eng-job | local | 4 riser projects (93G, 15,449 files) |
| dde_project_remote | (env var) | remote | DDE project archive |
| dde_standards_remote | /mnt/remote/ace-linux-2/dde/0000 O&G | remote | 36 org standards (18 unique) |
| dde_literature_remote | /mnt/remote/ace-linux-2/dde/Literature | remote | Historical literature (33 dirs) |
| dde_engineering_remote | /mnt/remote/ace-linux-2/dde | remote | Legacy engineering (MATLAB, OrcaFlex) |

---

## 6. KEY GAPS & RECOMMENDATIONS

### High-Priority Gaps for Target Domains

1. **Field Development Economics/CAPEX**: No FDP templates, concept selection guides, or economic models downloaded. The DDE Literature O&G collection has energy economics papers but nothing specific to field development planning. SPE OnePetro (score 5) is cataloged but not accessed.

2. **Geotechnical Foundation Design**: Only API RP 2GEO alpha method extracted. Missing:
   - Pile design textbooks (Das, Bowles, Tomlinson, Poulos & Davis)
   - DNV-RP-C212 (Offshore Soil Mechanics and Geotechnical Engineering)
   - ISO 19901-4 (Geotechnical and Foundation Design)
   - Soil/foundation calculation spreadsheets
   - DDE Soil directory (~5 files) not yet cataloged

3. **Naval Architecture Stability Calculations**: Good textbook coverage but 23 resources not downloaded including key items:
   - IMO Guidelines on Intact Stability 2014
   - MIT OCW lecture notes (2.019, 2.20)
   - Classification society rules (ABS Part 4, LR, BV, ClassNK)

4. **Conference Papers**: 38,526 files (21,996 PDFs) completely unindexed — highest-value gap. OMAE + OTC alone = 21,626 files covering all target domains.

5. **Standards Transfer Ledger**: Only 29/425 standards marked "done" (6.8%). 235 standards marked as "gap".
