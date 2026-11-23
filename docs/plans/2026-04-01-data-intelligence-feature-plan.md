# Data & Resource Intelligence — Consolidated Feature Plan

> Created: 2026-04-01
> Tracking issue: #1563
> Scope: 45 open GitHub issues across 8 sub-features

## Current State

| Metric | Value |
|--------|------:|
| Corpus index records | 1,033,933 |
| Phase B summaries done | 639,585 (62%) |
| Standards ledger total | 425 |
| Standards done | 29 (6.8%) |
| Standards gap | 235 (55.3%) |
| Resource intelligence maturity | 0% (0/5 docs read) |
| Mounted sources | 8 |
| Promoted tables (uncurated) | 3,683 CSVs |
| "other" domain records | 101,471 (9.8% of index) |
| "other" domain gap standards | 162 (68.9% of all gaps) |

## Feature Groups

### Group 1: Phase B Enrichment (batch AI summarization) — P0

Highest leverage. 0% summary coverage on multiple sources.

| Issue | Title | Machine |
|-------|-------|---------|
| #1437 | Phase B batch summaries for dde_project (495K docs) | dev-secondary |
| #1401 | Phase B batch summaries for ace_project gap pool (394K) | dev-secondary |
| #1399 | Phase B batch summaries for va-hdd-2 (15,990 gap docs) | dev-secondary |
| #1400 | Spot-check va-hdd-2 classification accuracy | dev-secondary |
| #95 | Regenerate document index to include 202 new literature | dev-primary |

### Group 2: Domain Classification & Triage — P1

101K records in "other" domain, 162 gap standards unclassified.

| Issue | Title | Machine |
|-------|-------|---------|
| #1357 | LLM-classify va-hdd-2 remaining content into domains | dev-secondary |
| #1363 | LLM domain-tag riser-eng-job literature | dev-secondary |
| #189 | Review disciplines/knowledge_skills — 30K docs | dev-primary |

### Group 3: Deep Extraction & Table Promotion — P1

Converts raw extraction to usable engineering data.

| Issue | Title | Machine |
|-------|-------|---------|
| #1353 | Deep extraction & table promotion for ace_standards | dev-secondary |
| #1295 | Promoted table curation — clean 3,683 CSVs | both |
| #1294 | Curate extracted worked examples into TDD fixtures | dev-primary |
| #1291 | Deepen naval architecture extraction from SNAME | dev-secondary |
| #1360 | Extract algorithms and methods from riser-eng-job | dev-secondary |

### Group 4: Standards Implementation (ledger gap closure) — P1

235 gap standards. CP & pipeline strongest (9+12 done).

| Issue | Title | Priority |
|-------|-------|----------|
| #172 | ASTM E647 (fatigue crack) — digitalmodel | high |
| #173 | ASTM E647 — OGManufacturing | high |
| #178 | ASTM A36 (carbon steel) — digitalmodel | medium |
| #179 | ASTM A36 — OGManufacturing | medium |
| #168 | ASTM A131 (ship steel) — digitalmodel | medium |
| #169 | ASTM A131 — OGManufacturing | medium |
| #170 | ASTM E606 (strain fatigue) — digitalmodel | medium |
| #171 | ASTM E606 — OGManufacturing | medium |
| #174 | ASTM E466 (force fatigue) — digitalmodel | medium |
| #175 | ASTM E466 — OGManufacturing | medium |
| #176 | ASTM E739 (statistical fatigue) — digitalmodel | medium |
| #177 | ASTM E739 — OGManufacturing | medium |
| #601 | VIV implementation (Allen, D.W., 1998) | high |

### Group 5: Data Sources & Literature Acquisition — P2

38 public O&G sources (16 ingested), 8 mounted source roots.

| Issue | Title | Priority |
|-------|-------|----------|
| #1395 | Add Equinor Northern Lights dataset | unset |
| #1394 | Add Equinor/Norce U7 reference data | unset |
| #1393 | Add Equinor ASA Databricks marketplace | unset |
| #94 | Fix metocean download script DEST path | high |
| #57 | Collect electrical engineering resources | medium |
| #41 | Add HydroComp NavCad resources | medium |
| #68 | Create research-and-literature-gathering skill | high |
| #1461 | Research backlog: remaining OSS catalog (59 items) | low |
| #1397 | Recurring research: OSS engineering catalog | high |
| #182 | Install Semantic Scholar MCP server | medium |

### Group 6: Naval Architecture Intelligence — P2

144 docs, 110 ship plans, SNAME collection, EN400 worked examples.

| Issue | Title | Priority |
|-------|-------|----------|
| #1312 | Phase 1 manual entry for ship dimensions template | medium |
| #152 | Extract ship plan drawings via CAD pipeline | medium |
| #1291 | Deepen naval architecture extraction from SNAME | high |
| #1297 | Naval architect expert skill — eng + legal | high |
| #1296 | Naval architecture expert skill — knowledge synthesis | high |

### Group 7: Knowledge Persistence & Workflow Integration — P2

Resource intelligence at 0% maturity, /work flow disconnected.

| Issue | Title | Priority |
|-------|-------|----------|
| #894 | Knowledge persistence architecture | high |
| #1321 | Session-to-execution flow: integrate data intelligence | unset |
| #1352 | Targeted index refresh before display | unset |
| #198 | Standardize execute gate variation tests | medium |

### Group 8: Document Source Hygiene — P3

Broken pointers, stale NTFS remnants, unorganized /mnt/ace/docs.

| Issue | Title | Machine |
|-------|-------|---------|
| #1404 | Organize /mnt/ace/docs/ subfolders and deduplicate | dev-primary |
| #1403 | Clean stale NTFS remnants from local-analysis | dev-primary |
| #1378 | Review local-analysis folders for knowledge center | multi |
| #1362 | Fix broken README_MIGRATED.md pointers | dev-secondary |
| #91 | Document extraction pipeline — index repo ecosystem | dev-primary |
| #166 | sabithaandkrishnaestates repo — doc indexing | dev-primary |

## Execution Phases

### Phase 1 — Foundation (weeks 1-2)
- Group 1: Phase B enrichment (start va-hdd-2, then ace_project)
- Group 2: LLM classification for va-hdd-2 and riser-eng-job
- Fix metocean download script (#94)
- Reclassify "other" domain standards in ledger

### Phase 2 — Extraction value (weeks 3-4)
- Group 3: Deep extraction + table/worked-example curation
- Group 4: ASTM fatigue cluster (E647, E606, E466, E739)
- Group 1 cont: dde_project Phase B batch (495K)

### Phase 3 — Expansion (weeks 5-6)
- Group 5: Literature-gathering skill + Equinor datasets
- Group 6: Naval architecture template + SNAME extraction
- Group 7: Knowledge persistence architecture

### Phase 4 — Hygiene & integration (weeks 7-8)
- Group 7: /work integration + index refresh
- Group 8: Source cleanup, dedup, broken-pointer fixes
- Group 4 cont: Remaining structural/materials standards

## Machine Allocation

| Machine | Groups | Workload type |
|---------|--------|---------------|
| dev-secondary (ace-linux-2) | 1, 2, 3 | Batch LLM, GPU, NFS |
| dev-primary (ace-linux-1) | 4, 7, 8 | Code implementation, workflow |
| Both | 5, 6 | Downloads, mixed |

## Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Phase B summary coverage | 62% | 90%+ |
| Standards ledger gap | 235 | <150 |
| "other" domain records | 101K | <30K |
| Resource intelligence maturity | 0% | 80% |
| Promoted table usability | 3,683 raw | curated subset |
