     1|# Engineering Documentation Map — Complete Inventory
     2|# Generated: 2026-04-04 by documentation audit subagent
     3|# Scope: Field Development, Naval Architecture, Geotechnical Engineering
     4|
     5|---
     6|
     7|## EXECUTIVE SUMMARY
     8|
     9|### Global Statistics
    10|- **Total indexed documents**: 1,033,933 records in index.jsonl
    11|- **Total summaries extracted**: 639,585 (61.9% coverage)
    12|- **Standards in transfer ledger**: 425 (29 done, 23 WRK-captured, 235 gap, 138 reference)
    13|- **Conference papers (unindexed)**: 38,526 files across 30 conferences
    14|- **Literature on DDE remote**: 14,620 MB (5,456 PDFs across Engineering + Oil & Gas)
    15|- **Standards on ACE drive**: 27,513 organized files (11,289 MB) across 11 orgs
    16|- **Standards on DDE drive**: 28,000+ files across 36 orgs (18 orgs unique to DDE)
    17|- **Doc-intelligence deep extractions**: 9 deep reports, 44+ naval architecture extraction reports
    18|- **Structured extracts**: 12M requirements, 4.9M constants, 2M equations, 1.4M procedures, 717K definitions, 279K worked examples
    19|
    20|### Status by Interest Domain
    21|
    22|| Domain | Downloaded PDFs | Cataloged/Not Downloaded | Standards (done/gap) | Deep Extractions | Dark Intelligence |
    23||--------|----------------|--------------------------|---------------------|------------------|-------------------|
    24|| Naval Architecture | 17 textbooks + 10 hydrostatics + 110 ship plans + 2 regulatory + 5 DNV/additional | 23 resources not started | 33 marine stds (4 done, 2 gap) | 44+ extraction reports | None specific |
    25|| Field Development (O&G) | 0 local docs indexed | 29 resources all not_started | 55 pipeline (12 done, 13 gap) | 2 deep reports (API 1111, DNV F105) | 6 Excel extractions |
    26|| Geotechnical | 1 dark-intelligence extraction | 0 specific resources cataloged | API RP 2GEO (reference) | 1 deep (API RP 2A WSD) | API RP 2GEO alpha method |
    27|| Structural | 50,001 local docs indexed | 30 resources not_started | 72 stds (4 done, 24 gap) | 4 deep reports | SN-curve riser analysis |
    28|
    29|---
    30|
    31|## 1. NAVAL ARCHITECTURE — Detailed Inventory
    32|
    33|### 1.1 Downloaded PDFs (Located on /mnt/ace/docs/_standards/SNAME/)
    34|
    35|#### Textbooks (17 PDFs, ~570 MB total)
    36|1. Principles of Naval Architecture Vol I — Stability & Strength (SNAME, ~1988) — 29 MB
    37|2. Principles of Naval Architecture Vol II — Resistance, Propulsion & Vibration (SNAME) — 30 MB
    38|3. PNA Vol II (Internet Archive higher-quality scan) — 84 MB
    39|4. PNA Second Revision Vol I — 32 MB
    40|5. PNA Second Revision Vol II — Resistance & Propulsion — 55 MB
    41|6. PNA Second Revision Vol III — Motions & Controllability — 34 MB
    42|7. Introduction to Naval Architecture (Tupper 1996) — 19 MB
    43|8. Introduction to Naval Architecture (Comstock 1942) — 5.7 MB
    44|9. Basic Ship Theory Vol 1 (Rawson & Tupper 2001) — 3.9 MB
    45|10. Design Principles of Ships and Marine Structures — 18 MB
    46|11. Engineering Mathematics for Ship Design — 20 MB
    47|12. Hybrid Ship Hulls — Engineering Design — 6.7 MB
    48|13. Ship Construction (Eyres 2001) — 17 MB
    49|14. Jane's Fighting Ships 2009-2010 — 198 MB
    50|15. ABS Introduction to Rules and Guides — 2.1 MB
    51|16. Warship 2011 — Naval Submarines & UUVs — 31 MB
    52|17. Warship — Naval Submarines Vol 9 — 22 MB
    53|
    54|#### Hydrostatics, Stability & Resistance (10 PDFs, ~120 MB total)
    55|1. Ship Hydrostatics and Stability (Biran, ~2003) — 9.3 MB
    56|2. Ship Hydrostatics and Stability 2nd Ed (Biran & Lopez Pulido, ~2014) — 10 MB
    57|3. PNA Series — Ship Resistance and Flow (~2010) — 9.7 MB
    58|4. Marine Hydrodynamics (Newman 2018) — 11 MB
    59|5. Practical Ship Hydrodynamics (Bertram 2000) — 2.2 MB
    60|6. Fluid-Dynamic Drag (Hoerner 1965) — 22 MB
    61|7. Handbook of Offshore Engineering (Chakrabarti 2005) — 36 MB
    62|8. Offshore Hydromechanics (Journee & Massie 2001) — 12 MB
    63|9. Ship Hydromechanics Introduction — 3.5 MB
    64|10. PNA — GZ Curves — 1.8 MB
    65|
    66|#### Ship Plans (110 PDFs from maritime.org)
    67|- Historical US Navy/Allied vessel general arrangement drawings (1863-2008)
    68|- Located: /mnt/ace/docs/_standards/SNAME/ship-plans/
    69|
    70|#### Additional Resources (Downloaded)
    71|- USNA EN400 Principles of Ship Performance Course Notes (2020) — 9.6 MB
    72|- Text-book of Theoretical Naval Architecture (Attwood 1899) — 12 MB
    73|- Ship Structural Analysis and Design (Hughes & Paik) — 14 MB
    74|- DNV-RP-C205 Environmental Conditions & Loads (2007) — 2.9 MB
    75|- DNV-RP-H103 Marine Operations (2010) — 2.4 MB
    76|
    77|#### Regulatory (Downloaded)
    78|- UK MCA MSIS43 Intact Stability Guidance (2023) — 4.7 MB
    79|- SOLAS 2020 Consolidated Edition — 2.1 MB
    80|
    81|### 1.2 Cataloged but NOT Downloaded (23 items)
    82|- ABS Marine Vessel Rules Part 4 (2024) — WAF blocks wget
    83|- Aalto University Lecture Notes on Basic Naval Architecture (2021, CC BY)
    84|- Bureau Veritas Rules (130+ publications)
    85|- ClassNK Technical Rules (complete set)
    86|- DTIC Engineering for Ship Production — DTIC blocks wget
    87|- DTIC Small Craft Design Guide (1977) — DTIC blocks wget
    88|- IMO Guidelines on Intact Stability 2014 — download failed
    89|- Internet Archive Naval Architecture Collection
    90|- Introduction to Naval Architecture (Gillmer & Johnson) — borrow-only
    91|- Lloyd's Register Heritage Centre
    92|- Lloyd's Register Rules for Classification (July 2022, Internet Archive)
    93|- MIT OCW 2.019 Design of Ocean Systems Lecture Notes
    94|- MIT OCW 2.20 Marine Hydrodynamics Lecture Notes (24 PDFs)
    95|- University of Michigan Basic Naval Architecture Vol I & II — redirects wget
    96|- RINA Transactions portal
    97|- SNAME publications portal
    98|
    99|### 1.3 Doc-Intelligence Extractions for Naval Architecture
   100|- **44+ extraction reports** in data/doc-intelligence/extraction-reports/naval-architecture/
   101|  - Covers all downloaded textbooks and ship plans
   102|  - Reports include: equations, tables, worked examples, constants, procedures
   103|- **Naval architecture catalog**: data/doc-intelligence/naval-architecture-catalog.yaml (144 docs, 110 ship plans, 21 textbooks, 65 hull codes)
   104|- **Ship plans index**: data/doc-intelligence/ship-plans-index.yaml
   105|- **EN400 worked examples**: data/doc-intelligence/en400-worked-examples.yaml
   106|- **Ship dimensions**: data/doc-intelligence/ship-dimensions.yaml
   107|
   108|---
   109|
   110|## 2. FIELD DEVELOPMENT / OIL & GAS — Detailed Inventory
   111|
   112|### 2.1 Downloaded Standards (on ACE drive)
   113|Pipeline domain (12 done):
   114|- API RP 1111 (Offshore Hydrocarbon Pipelines, Limit State Design)
   115|- API RP 2RD (Design of Risers)
   116|- API RP 5L (Line Pipe)
   117|- API STD 2RD 2nd Ed (Dynamic Risers for Floating Production)
   118|- DNV-OS-F101 (Submarine Pipeline Systems)
   119|- DNV-OS-F201 (Dynamic Risers)
   120|- DNV-RP-F105 (Free Spanning Pipelines)
   121|- DNV-RP-F109 (On-bottom Stability)
   122|- DNV-RP-F110 (Global Buckling)
   123|- ISO 13624-1 (Risers)
   124|- ISO 13628 (Completion/Workover)
   125|- ISO 16389 (Dynamic Risers)
   126|
   127|Marine domain (4 done):
   128|- API RP 2I (Mooring Hardware Inspection)
   129|- API RP 2P
   130|- API RP 2SM (Synthetic Fiber Ropes for Mooring)
   131|- DNV-OS-E301 (Position Mooring)
   132|
   133|### 2.2 Literature on DDE Remote Drive (not yet migrated)
   134|Engineering Literature (~8,640 MB, 823 PDFs):
   135|- Reservoir engineering textbooks (Fundamentals of Reservoir Engineering, Reservoir Engineering Handbook 2E, etc.)
   136|- Flow assurance references
   137|- DNV-RP-B401 Cathodic Protection Design
   138|- Structural, Soil, Riser Engineering directories (~400+ files in Structural/ alone)
   139|- OTC 2004 conference papers (~20 files)
   140|- Oil and Gas Codes directory (~15 files)
   141|
   142|Oil & Gas Literature (~5,980 MB, 4,633 PDFs):
   143|- Advanced Reservoir Engineering (Ahmed & McKinney, Elsevier 2005) — 9.7 MB
   144|- Applied Petroleum Reservoir Engineering — 13.1 MB
   145|- Quantitative Methods in Reservoir Engineering — 2.4 MB
   146|- Reservoir Engineering Handbook (multiple editions) — 9.8 MB, 9.9 MB
   147|- Oil & Gas Standard Handbook — 32 MB
   148|- Rigtrain Manual — 78 MB
   149|- Energy economics literature (Wiley Finance, Hirsch Report, etc.)
   150|- Khori/BOOKS (~200 files, 700 MB) — structural textbooks
   151|- Khori/STRUCTURAL BOOK (~100 files, 800 MB)
   152|- 2006-07 Geotech Conference (~7 files, 8 MB)
   153|
   154|### 2.3 Online Resources (All 29 Not Yet Started)
   155|- BOEM, Baker Hughes Rig Count, EIA Open Data API v2 (score 5)
   156|- SPE OnePetro (score 5)
   157|- API MyCommittees, OPM Flow, ResInsight, Whitson+ (score 4)
   158|- ANP Brazil, JODI, OPEC, USGS assessments (score 3)
   159|
   160|### 2.4 Conference Papers (Unindexed — 38,526 total files)
   161|Key conferences for field development:
   162|- **OTC** (Offshore Technology Conference): 8,500 files, 5,432 PDFs, 7,946 MB (1988-2017)
   163|- **OMAE**: 13,126 files, 7,292 PDFs, 8,345 MB (1998-2014)
   164|- **ISOPE**: 4,516 files, 4,074 PDFs, 3,044 MB (2003-2014)
   165|- **DOT** (Deep Offshore Technology): 7,516 files, 1,456 PDFs, 2,255 MB (2001-2013)
   166|- **SPE**: 129 files, 124 PDFs, 116 MB
   167|- **Subsea Tieback**: 214 files, 798 MB
   168|- **DeepGulf**: 43 files, 42 PDFs
   169|- **Rio Oil & Gas**: 66 PDFs, 31 MB
   170|
   171|### 2.5 Standards on Drive (DDE + ACE)
   172|ACE organized:
   173|- API: 574 files (2,591 MB)
   174|- ISO: 308 files (736 MB)
   175|- DNV: 100 files (213 MB)
   176|- SNAME: 145 files (1,417 MB)
   177|- OnePetro: 94 files (129 MB)
   178|
   179|DDE unique (not in ACE):
   180|- ASCE: 404 files (4,534 MB) — CRITICAL, includes Deepwater Horizon Blue-Ribbon Panel
   181|- ASME: 91 files (984 MB) — BPVC, B31.3, B31.4, B31.8
   182|- AWS: 16 files (471 MB) — D1.1 Structural Welding Code
   183|- NACE: 8 files (5 MB) — MR 0175 (H2S), corrosion papers
   184|- HSE: 2 files (5 MB) — offshore fatigue guidance
   185|- NFPA: 2 files (585 MB) — fire safety
   186|- CFR: 9 files (155 MB) — US regulatory
   187|- ISO (DDE delta): ~350 additional standards vs ACE
   188|
   189|---
   190|
   191|## 3. GEOTECHNICAL ENGINEERING — Detailed Inventory
   192|
   193|### 3.1 Dark Intelligence Extractions
   194|- **API RP 2GEO Alpha Method** (knowledge/dark-intelligence/geotechnical/pile_capacity/)
   195|  - Full equation extraction: alpha factor, unit skin friction, total axial capacity
   196|  - Worked example: 1.0m diameter pile, 30m long, firm clay
   197|  - Test vectors with tolerances for validation
   198|  - Source: API RP 2GEO Section 7.3
   199|
   200|### 3.2 Related Standards Available
   201|- API RP 2A-WSD (Fixed Offshore Platforms — includes pile design) — deep extraction done
   202|- API RP 2GEO 1st Ed Addendum 1, Oct 2014 — cataloged as reference
   203|- Design of Large Diameter Monopiles under Lateral Loads — cataloged
   204|- Soil directory on DDE: /mnt/remote/ace-linux-2/dde/Literature/Engineering/Soil (~5 files)
   205|- 2006-07 Geotech Conference on DDE: ~7 files, 8 MB
   206|
   207|### 3.3 Deep Extraction Reports Relevant
   208|- API RP 2A WSD Offshore Platforms — deep extraction done (includes geotechnical sections)
   209|
   210|### 3.4 Gaps
   211|- No dedicated geotechnical textbooks downloaded yet (e.g., Das, Bowles, Tomlinson)
   212|- API RP 2GEO full document not in standards ledger as "done"
   213|- No specific pile design software tools cataloged
   214|- OpenSees cataloged for structural/geotechnical FEM but not downloaded
   215|
   216|---
   217|
   218|## 4. DOC-INTELLIGENCE EXTRACTION STATUS
   219|
   220|### 4.1 Phase B Structured Extracts (Bulk)
   221|| Extract Type | Records | File |
   222||-------------|---------|------|
   223|| Requirements | 12.0M | data/doc-intelligence/requirements.jsonl |
   224|| Constants | 4.9M | data/doc-intelligence/constants.jsonl |
   225|| Equations | 2.0M | data/doc-intelligence/equations.jsonl |
   226|| Procedures | 1.4M | data/doc-intelligence/procedures.jsonl |
   227|| Definitions | 717K | data/doc-intelligence/definitions.jsonl |
   228|| Worked examples | 279K | data/doc-intelligence/worked_examples.jsonl |
   229|
   230|### 4.2 Deep Extraction Reports (9 standards)
   231|1. API 579-1/ASME FFS-1 (2016) — fitness for service
   232|2. API RP 1111 4th Ed (2009) — offshore hydrocarbon pipelines
   233|3. API RP 2A WSD (2000) — fixed offshore platforms (includes geotechnical)
   234|4. API RP 2SK 3rd Ed (2005) — stationkeeping systems
   235|5. DNV RP B401 (2011) — cathodic protection design
   236|6. DNV RP C203 (2011) — fatigue design of offshore steel
   237|7. DNV RP C205 (2007) — environmental conditions and loads
   238|8. DNV RP F105 (2002) — free spanning pipelines
   239|9. DNV RP F109 (2011) — on-bottom stability
   240|
   241|### 4.3 Naval Architecture Extraction Reports (44+)
   242|Full extraction reports for all textbooks and ship plans in the collection.
   243|
   244|### 4.4 Table Extractions
   245|- ABS Intro to Rules tables (6 CSVs)
   246|- ASME 31G tables (20 CSVs)
   247|- GEOBASE NHNC1 tables (multiple CSVs)
   248|- Domain-organized deep tables: cathodic-protection, fatigue, marine, mooring, pipeline, structural
   249|
   250|### 4.5 Dark Intelligence Excel Extractions (6 spreadsheets, 2 generations)
   251|POC v1 and v2 extractions with Python re-implementations:
   252|1. Surface wellhead SITP calculations (0163-cal-0001)
   253|2. Conductor length assessment (31126-cal-0001)
   254|3. SN curve definitions for riser analysis (31245-cal-0018)
   255|4. C-K flow rate calculation
   256|5. Flowback calculator (cc-23-6h)
   257|6. Spotfire formulas for calc variables
   258|
   259|---
   260|
   261|## 5. MOUNTED SOURCE REGISTRY (10 sources)
   262|
   263|| Source ID | Mount Root | Type | Content |
   264||-----------|-----------|------|---------|
   265|| workspace_hub_local | /mnt/local-analysis/workspace-hub | local | In-repo specs and configs |
   266|| ace_standards_local | /mnt/ace/docs/_standards | local | Standards library |
   267|| og_standards_local | /mnt/ace/0000 O&G | local | O&G standards collection |
   268|| ace_project_local | /mnt/ace/docs | local | Project documents |
   269|| research_literature_local | /mnt/ace-data/digitalmodel/docs/domains | local | Domain-organized literature |
   270|| riser_eng_job_local | /mnt/ace/digitalmodel/.../riser-eng-job | local | 4 riser projects (93G, 15,449 files) |
   271|| dde_project_remote | (env var) | remote | DDE project archive |
   272|| dde_standards_remote | /mnt/remote/ace-linux-2/dde/0000 O&G | remote | 36 org standards (18 unique) |
   273|| dde_literature_remote | /mnt/remote/ace-linux-2/dde/Literature | remote | Historical literature (33 dirs) |
   274|| dde_engineering_remote | /mnt/remote/ace-linux-2/dde | remote | Legacy engineering (MATLAB, OrcaFlex) |
   275|
   276|---
   277|
   278|## 6. KEY GAPS & RECOMMENDATIONS
   279|
   280|### High-Priority Gaps for Target Domains
   281|
   282|1. **Field Development Economics/CAPEX**: No FDP templates, concept selection guides, or economic models downloaded. The DDE Literature O&G collection has energy economics papers but nothing specific to field development planning. SPE OnePetro (score 5) is cataloged but not accessed.
   283|
   284|2. **Geotechnical Foundation Design**: Only API RP 2GEO alpha method extracted. Missing:
   285|   - Pile design textbooks (Das, Bowles, Tomlinson, Poulos & Davis)
   286|   - DNV-RP-C212 (Offshore Soil Mechanics and Geotechnical Engineering)
   287|   - ISO 19901-4 (Geotechnical and Foundation Design)
   288|   - Soil/foundation calculation spreadsheets
   289|   - DDE Soil directory (~5 files) not yet cataloged
   290|
   291|3. **Naval Architecture Stability Calculations**: Good textbook coverage but 23 resources not downloaded including key items:
   292|   - IMO Guidelines on Intact Stability 2014
   293|   - MIT OCW lecture notes (2.019, 2.20)
   294|   - Classification society rules (ABS Part 4, LR, BV, ClassNK)
   295|
   296|4. **Conference Papers**: 38,526 files (21,996 PDFs) completely unindexed — highest-value gap. OMAE + OTC alone = 21,626 files covering all target domains.
   297|
   298|5. **Standards Transfer Ledger**: Only 29/425 standards marked "done" (6.8%). 235 standards marked as "gap".
   299|
