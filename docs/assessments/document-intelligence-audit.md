# Document Intelligence Infrastructure Audit

> **Date:** 2026-04-02
> **Issue:** #1575 (Holistic Document & Resource Intelligence)
> **Author:** AI Agent (Gemini/Codex seat 2, Terminal 6)

---

## Executive Summary

The workspace-hub document intelligence pipeline is a **7-phase, resume-safe batch system** that indexes, extracts, classifies, and registers over **1 million documents** across 8 mounted sources. The extraction library (`doc_intelligence/`) contains **51 top-level scripts**, **6 parsers**, **10 promoters**, and **31 tests**. Current maturity stands at **6.8% document-read** (29/425 in-scope standards), with a target of 80% within 3 months.

**Key metrics:**
- **1,033,933** documents indexed across 8 sources
- **639,585** summaries generated (61.9% coverage)
- **425** standards in the transfer ledger (29 done, 235 gap, 138 reference, 23 WRK-captured)
- **12** engineering domains tracked (reclassification eliminated "other" entirely)
- **3,825** lines of pipeline code across 12 phase scripts

---

## 1. The 7-Phase Pipeline

All scripts live in `scripts/data/document-index/`. Each phase is resume-safe and reads from the previous phase's output.

### Phase A — Multi-Source Index Builder (`phase-a-index.py`, 389 lines)

- **Purpose:** Scans all document sources in parallel, hashes files, and builds `index.jsonl`
- **Input:** `config.yaml` defining source roots (8 mounted sources)
- **Output:** `data/document-index/index.jsonl` — one JSON record per document (path, SHA-256, size, extension, source)
- **Features:** Resume-safe via SQLite state tracking, hash-based dedup, progress reporting every 1,000 files, provenance tracking via `provenance.py`
- **Current yield:** 1,033,933 index records

### Phase B — Text Extraction & LLM Summarisation (`phase-b-extract.py`, 314 lines + `phase-b-claude-worker.py`, 455 lines)

- **Purpose:** Extracts text from indexed documents and generates LLM summaries
- **Input:** `index.jsonl` records
- **Output:** `summaries/<sha256>.json` — one summary file per document
- **Architecture:**
  - `phase-b-extract.py` — Main batch processor, reads index, dispatches extraction
  - `phase-b-claude-worker.py` — Overnight sharded Claude CLI worker (10 shards, 90s timeout per call)
  - `phase-b-astm-validate.py` (154 lines) — ASTM-specific validation
- **LLM integration:** Claude CLI with disciplines taxonomy (structural, cathodic-protection, pipeline, marine, installation, energy-economics, materials, regulatory, drilling, workspace-spec)
- **Current yield:** 639,585 summaries (61.9% of indexed documents)

### Phase C — Domain Classification (`phase-c-classify.py`, 345 lines)

- **Purpose:** Classifies indexed documents by engineering domain and generates enhancement plan
- **Input:** Index records + Phase B summaries
- **Output:** `data/document-index/enhancement-plan.yaml` (1.7 MB, 34,099 lines)
- **Taxonomy:** 12 valid domains: structural, cathodic-protection, pipeline, marine, installation, energy-economics, portfolio, materials, regulatory, cad, workspace-spec, other
- **Status mapping:** implemented, gap, data_source, reference
- **Phase B → C remap:** Maps Phase B discipline labels to Phase C domain taxonomy

### Phase D — Data Source Generation (`phase-d-data-sources.py`, 283 lines)

- **Purpose:** Generates per-repo data-source YAML specs from enhancement plan
- **Input:** `enhancement-plan.yaml`
- **Output:** `specs/data-sources/<repo>.yaml` per Tier-1/Tier-2 repo
- **Legal gate:** Runs `legal-sanity-scan.sh` before writing; sanitizes paths
- **Repo tiers:** Tier 1 (digitalmodel, worldenergydata, assethold), Tier 2 (doris, OGManufacturing, saipem, rock-oil-field, acma-projects)

### Phase E — Registry Building (`phase-e-registry.py`, 190 lines + `phase-e-backpopulate.py`, 222 lines + `phase-e2-remap.py`, 531 lines)

- **Purpose:** Builds master registry linking all index/summary/domain data
- **Input:** Index records + summaries + enhancement plan
- **Output:** `data/document-index/registry.yaml` (committed, sanitized)
- **Sub-phases:**
  - `phase-e-registry.py` — Core registry builder
  - `phase-e-backpopulate.py` — Backfills missing metadata
  - `phase-e2-remap.py` — Standards reclassification (531 lines, eliminated "other" domain)
- **Legal gate:** Runs `legal-sanity-scan.sh` before writing

### Phase F — WRK Item Generation (`phase-f-wrk-items.py`, 214 lines + `phase-f-gap-wrk-generator.py`, 398 lines)

- **Purpose:** Creates WRK-style backlog candidates from document gaps identified in enhancement plan
- **Input:** `enhancement-plan.yaml`
- **Legacy output:** WRK item YAML files in `.claude/work-queue/`
- **Canonical tracking note:** New execution work should be represented as GitHub issues plus `.planning/` artifacts; `.claude/work-queue/` is legacy compatibility storage only.
- **Logic:** Reads gaps, creates pending WRK-style records for unimplemented standards, assigns to repos

### Phase G — Pre-seeded Mission WRK Items (`phase-g-wrk-items.py`, 330 lines)

- **Purpose:** Creates WRK-style backlog candidates for known engineering gaps independent of document indexing
- **Input:** Hardcoded `REPO_MISSION_ITEMS` list of strategic gaps
- **Legacy output:** WRK item YAML files in `.claude/work-queue/`
- **Canonical tracking note:** Promote active items into GitHub issues before new execution; keep local WRK artifacts only for historical/compatibility workflows.
- **Scope:** Pre-seeds items like "Expand S-N curve library from 17 to 20 standards", "CALM buoy mooring fatigue", etc.
- **Repos covered:** digitalmodel (G-1 through G-6 groups), worldenergydata, assethold, doris, saipem

---

## 2. Extraction Library (`scripts/data/doc_intelligence/`)

### 2.1 Overview

| Category | Count | Description |
|----------|-------|-------------|
| **Top-level scripts** | 51 | Core extraction, orchestration, quality tools |
| **Parsers** (`parsers/`) | 6 | Format-specific extraction backends |
| **Promoters** (`promoters/`) | 10 | Extracted-data-to-knowledge promotion |
| **Tests** (`tests/`) | 31 | Unit tests for extraction pipeline |
| **Total Python files** | 98+ | Full doc-intelligence library |

### 2.2 Parser Inventory

| Parser | File | Capabilities |
|--------|------|-------------|
| **PDF** | `parsers/pdf.py` | PDF text extraction, page-level parsing |
| **XLSX** | `parsers/xlsx.py` | Excel spreadsheet extraction |
| **Formula XLSX** | `parsers/formula_xlsx.py` | Excel formula chain extraction (656K+ formulas in POC) |
| **HTML** | `parsers/html.py` | Web page content extraction |
| **DOCX** | `parsers/docx_parser.py` | Word document extraction |
| **Base** | `parsers/base.py` | Abstract base parser interface |

### 2.3 Extraction Capabilities

| Script | Purpose |
|--------|---------|
| `deep_extract.py` | Deep multi-pass extraction for complex documents |
| `batch_deep_extract_naval.py` | Batch deep extraction for naval architecture documents |
| `end_to_end_online_extraction.py` | Online resource → extracted knowledge pipeline |
| `extract_url.py` | URL content extraction |
| `extract_engineering_constants.py` | Engineering constants from standards |
| `formula_to_python.py` | Excel formula → Python code conversion |
| `formula_chain_builder.py` | Formula dependency chain analysis |
| `formula_reference_parser.py` | Standard reference extraction from formulas |
| `chart_extractor.py` | Chart/figure extraction from documents |
| `vba_extractor.py` | VBA macro extraction from Excel |
| `crawl_and_enqueue.py` | Web crawler with queue management |
| `fetch_from_api.py` | API-based document fetching |
| `fetcher.py` | Generic document fetcher |
| `orchestrator.py` | Multi-stage extraction orchestrator |

### 2.4 Promoter Pipeline

The `promoters/` directory handles promoting extracted data into structured knowledge:

| Promoter | Purpose |
|----------|---------|
| `equations.py` | Mathematical equation extraction and structuring |
| `constants.py` | Engineering constant cataloging |
| `tables.py` | Table extraction and normalization |
| `curves.py` | S-N curves, fatigue curves extraction |
| `procedures.py` | Engineering procedure extraction |
| `definitions.py` | Technical definition extraction |
| `requirements.py` | Standard requirements extraction |
| `worked_examples.py` | Worked example extraction |
| `coordinator.py` | Promotion pipeline orchestrator |
| `text_utils.py` | Text processing utilities |

### 2.5 Extraction Yield (XLSX POC — `yield-report.yaml`)

| Metric | Value |
|--------|-------|
| **WRK:** | WRK-1247 |
| **Files processed:** | 10 |
| **Successful:** | 6 |
| **Skipped (size limit):** | 4 (>15 MB limit) |
| **Total formulas extracted:** | 656,635 |
| **Total tests generated:** | 187,093 |
| **Cache quality:** | 100% (all formulas cached OK) |
| **Largest file processed:** | CC 23 6H Flowback Calculator 4.xlsx (12.6 MB, 647,447 formulas, 182,713 tests) |

---

## 3. Data Registries

### 3.1 Master Registry (`data/document-index/registry.yaml`)

| Metric | Value |
|--------|-------|
| **Generated:** | 2026-04-01T19:05:00 |
| **Total documents:** | 1,033,933 |
| **Total summaries:** | 639,585 |

**By source:**

| Source | Documents |
|--------|-----------|
| dde_project | 495,487 |
| ace_project | 453,285 |
| ace_standards | 55,442 |
| og_standards | 27,980 |
| workspace_spec | 1,587 |
| api_metadata | 8 |

**By domain:**

| Domain | Documents | % of Total |
|--------|-----------|-----------|
| marine | 283,451 | 27.4% |
| cad | 275,445 | 26.6% |
| pipeline | 188,173 | 18.2% |
| materials | 72,344 | 7.0% |
| portfolio | 55,942 | 5.4% |
| structural | 50,001 | 4.8% |
| other | 44,705 | 4.3% |
| project-management | 43,922 | 4.2% |
| installation | 13,502 | 1.3% |
| energy-economics | 2,930 | 0.3% |
| cathodic-protection | 1,714 | 0.2% |
| workspace-spec | 1,587 | 0.2% |
| naval-architecture | 144 | 0.01% |
| regulatory | 73 | 0.007% |

**Per-repo standards:**

| Repo | Standards Count | Gaps | Implemented |
|------|----------------|------|-------------|
| digitalmodel | 183 | 14 | 2 |
| acma-projects | 110 | 0 | 0 |
| doris | 92 | 0 | 0 |
| OGManufacturing | 71 | 0 | 0 |
| rock-oil-field | 35 | 0 | 0 |
| saipem | 35 | 0 | 0 |
| worldenergydata | 12 | 4 | 0 |
| assethold | 0 | 5 | 0 |

### 3.2 Mounted Source Registry (`data/document-index/mounted-source-registry.yaml`)

8 sources with deduplication rules, provenance tracking, and availability checks:

| Source ID | Bucket | Mount Root | Type | Notes |
|-----------|--------|-----------|------|-------|
| workspace_hub_local | workspace_spec | /mnt/local-analysis/workspace-hub | local | In-repo canonical source |
| ace_standards_local | ace_standards | /mnt/ace/docs/_standards | local | Mounted standards library |
| og_standards_local | og_standards | /mnt/ace/0000 O&G | local | Mounted standards/reference library |
| ace_project_local | ace_project | /mnt/ace/docs | local | Mounted project-document source |
| research_literature_local | research_literature | /mnt/ace-data/digitalmodel/docs/domains | local | Downloaded research by domain |
| riser_eng_job_local | riser_eng_job | /mnt/ace/digitalmodel/docs/domain/subsea-risers | local | 4 projects, 93G, 15,449 files |
| dde_project_remote | dde_project | (remote mount) | remote | Remote project documents |
| api_metadata_virtual | api_metadata | api://worldenergydata | API | API-backed metadata source |

### 3.3 Standards Transfer Ledger (`data/document-index/standards-transfer-ledger.yaml`)

| Metric | Value |
|--------|-------|
| **Total standards:** | 425 |
| **Reference:** | 138 |
| **Gap:** | 235 |
| **WRK captured:** | 23 |
| **Done:** | 29 |

**By domain:**

| Domain | Count | % of Total |
|--------|-------|-----------|
| materials | 122 | 28.7% |
| structural | 72 | 16.9% |
| process | 55 | 12.9% |
| pipeline | 55 | 12.9% |
| marine | 33 | 7.8% |
| cad | 23 | 5.4% |
| installation | 22 | 5.2% |
| cathodic-protection | 19 | 4.5% |
| regulatory | 15 | 3.5% |
| drilling | 9 | 2.1% |

### 3.4 Enhancement Plan (`data/document-index/enhancement-plan.yaml`)

- **Size:** 1.7 MB, 34,099 lines
- **Generated:** 2026-03-15
- **Total classified:** 1,033,933 documents
- **Structure:** `by_domain → <domain> → { count, repos, items[] }` with 500 sample items per domain

| Domain | Document Count | Items Listed |
|--------|---------------|-------------|
| cad | 474,663 | 500 |
| pipeline | 186,911 | 500 |
| other | 176,527 | 500 |
| portfolio | 55,265 | 500 |
| materials | 48,133 | 500 |
| marine | 32,060 | 500 |
| regulatory | 25,066 | 500 |
| structural | 22,506 | 500 |
| installation | 7,656 | 500 |
| energy-economics | 2,027 | 500 |
| cathodic-protection | 1,532 | 500 |
| workspace-spec | 1,587 | 500 |

### 3.5 Ship Plans Catalog (`data/document-index/ship-plans-catalog.yaml`)

- **Source:** `/mnt/ace/O&G-Standards/SNAME/ship-plans/`
- **Total plans:** 110
- **Total pages:** 986
- **Vessel types:** 43 distinct types (Submarine: 13, Battleship: 9, Aircraft Carrier: 9, Destroyer: 8, Transport: 3, etc.)

---

## 4. Current State — Resource Intelligence Maturity

**From `data/document-index/resource-intelligence-maturity.yaml` (v1.1.0):**

| Metric | Value |
|--------|-------|
| **Target window:** | 3 months (from 2026-03-01) |
| **Documents in scope:** | 425 |
| **Documents marked read:** | 29 |
| **Read percentage:** | 6.8% |
| **Target:** | 80% |
| **Gap to target:** | 73.2 percentage points (396 more standards to read) |
| **Gap standards:** | 235 |
| **Reference standards:** | 138 |
| **WRK-captured standards:** | 23 |
| **Total index records:** | 1,033,933 |
| **Total summaries:** | 639,585 |
| **Summary coverage:** | 61.9% |

**Key calculations implemented:**

| Domain | Done | Domain % | Notes |
|--------|------|----------|-------|
| cathodic-protection | 9 | 47.4% | Leading domain |
| pipeline | 12 | 21.8% | Good progress |
| marine | 4 | 12.1% | Moderate |
| structural | 4 | 5.6% | Large domain, low coverage |

**Recent milestones:**
- Standards reclassification complete — "other" eliminated (166 → 0)
- Two new domains created: process (55 standards), drilling (9 standards)
- 76 standards reclassified into proper engineering domains

---

## 5. Gap Analysis

### 5.1 Domains with Most Un-indexed Documents

The enhancement plan reveals massive un-indexed document volumes:

| Domain | Total Docs | In Ledger | Indexed Ratio |
|--------|-----------|-----------|---------------|
| cad | 474,663 | 23 | 0.005% |
| pipeline | 186,911 | 55 | 0.03% |
| other | 176,527 | 0 | 0% |
| portfolio | 55,265 | 0 | 0% |
| materials | 48,133 | 122 | 0.25% |
| marine | 32,060 | 33 | 0.10% |

**The "other" domain** (176,527 docs in enhancement plan) has been eliminated from the ledger but still contains a large volume of unclassified documents in the raw index.

### 5.2 Missing Extraction Capabilities

| Gap | Impact | Priority |
|-----|--------|----------|
| **No DWG/DXF parser** | 474,663 CAD documents cannot be text-extracted | Critical |
| **No image/scan OCR** | Many older standards are scanned PDFs | High |
| **XLSX size limit (15 MB)** | 4 of 10 POC files skipped (largest: 131 MB) | Medium |
| **No PowerPoint parser** | PPT/PPTX presentations not extracted | Low |
| **No email parser** | MSG/EML project correspondence not indexed | Low |
| **No DGN parser** | MicroStation files not accessible | Low |
| **Limited VBA extraction** | Complex macros not fully decompiled | Medium |

### 5.3 Path from 6.8% to 20% Document-Read Maturity

To reach 20% (85 standards read, up from 29), **56 additional standards** need to be read:

1. **Quick wins — standards already on disk with summaries (est. 20-30):**
   - Complete the 23 WRK-captured standards (summaries exist, need human review)
   - Prioritize standards with existing doc_paths in the ledger

2. **Medium effort — standards on disk, no summary (est. 15-20):**
   - Run Phase B extraction on the 138 reference-status standards that have doc_paths
   - Focus on domains with highest calculation implementation rates (CP, pipeline)

3. **Hard effort — gap standards requiring acquisition (est. 10-15):**
   - Target the 235 gap standards, starting with those in high-priority domains
   - Focus on marine (2 gaps), pipeline, and structural domains

**Estimated effort:** 2-3 overnight batch runs (Phase B Claude worker) + 2-3 days of targeted review

### 5.4 Known But Not Downloaded Online Resources

From the online resources catalog (`.planning/archive/online-resources/catalog.yaml`, 1,534 lines):

| Resource | Category | Status | Priority |
|----------|----------|--------|----------|
| DNV Standards Explorer | Engineering standards | known | Critical — 650+ standards, free viewer |
| API Standards Portal | Engineering standards | known | High — addenda and errata |
| CMEMS Marine Service | Metocean data | known | High — free marine data |
| Open-Meteo Marine API | Wave/weather data | known | Medium — free API |
| SNAME T&R Bulletins | Marine engineering | known | High — structural, hydro, materials |
| IMarEST Proceedings | Marine engineering | known | Medium |
| The Well (Polymathic AI) | Physics ML datasets | evaluated | High — 15 TB physics simulation data |
| wavespectra (Python) | Wave analysis | known | High — pip installable |

### 5.5 Conference Paper Archive (Unindexed)

| Conference | Files | Indexed? | Marine Relevance |
|-----------|-------|----------|-----------------|
| OMAE | 13,126 | No | **Critical** — primary marine hydrodynamics venue |
| OTC | 8,500 | No | **High** — offshore technology |
| ISOPE | 4,516 | No | **High** — ocean/polar engineering |
| SNAME | 99 | No | **High** — naval architecture |
| SUT | 1 | No | Medium — subsea technology |
| **Total unindexed** | **26,242** | | |

OMAE alone (2001-2014, 16 years) represents **13,126 unindexed papers** — many directly relevant to hydrodynamics, diffraction, and marine operations.

---

## 6. Recommendations

1. **Priority 1 — Index conference papers:** Add OMAE/OTC/ISOPE (26,242 files) to Phase A config as a new source
2. **Priority 2 — OCR capability:** Add OCR parser for scanned PDF standards (est. 30% of og_standards)
3. **Priority 3 — Batch Phase B runs:** Schedule 3 overnight Claude worker runs targeting WRK-captured + reference standards
4. **Priority 4 — DWG/DXF parser:** Integrate ODA File Converter or LibreCAD for CAD text extraction
5. **Priority 5 — XLSX size limit increase:** Raise from 15 MB to 50 MB for formula extraction (covers 2 of 4 skipped files)
6. **Priority 6 — Online resource downloads:** Automate download of DNV Standards Explorer, wavespectra, CMEMS data
7. **Priority 7 — Enhancement plan refinement:** Reduce "other" domain in enhancement plan (176K docs) through reclassification
8. **Priority 8 — Research literature indexing:** Index /mnt/ace-data/digitalmodel/docs/domains/ (12 domain folders, 52+ PDFs)
