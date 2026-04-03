# Mount Drive Knowledge Map — Complete Resource Intelligence Guide

> **Generated:** 2026-04-02
> **Purpose:** Single reference for all document/resource intelligence across mounted drives
> **Audience:** AI agents, engineers, and automation scripts needing to locate data

---

## Executive Summary

The ACE workspace spans 4 physical/logical mount points containing **3.6M+ files across 12+ TB** of engineering knowledge. This includes:

- **1,033,933** indexed documents in the workspace-hub pipeline
- **1,043,616** searchable text chunks with embeddings (O&G Standards)
- **38,526** conference papers (OMAE, OTC, DOT, ISOPE — 0% indexed)
- **26,884** industry standards files (API, DNV, ISO, ASTM, ABS, etc.)
- **119** project documentation folders spanning 20+ years
- **8** open-source engineering repositories (WEC-Sim, OpenFAST, Capytaine, etc.)
- **12** engineering domain taxonomies with extraction pipelines

### Documentation Quality Assessment

| Aspect | Rating | Notes |
|--------|--------|-------|
| Mount structure docs | GOOD | `/mnt/ace/README.md` is clear, assets.json is machine-readable |
| Data intelligence map | EXCELLENT | `docs/document-intelligence/data-intelligence-map.md` is comprehensive |
| Document pipeline docs | EXCELLENT | 7-phase pipeline fully documented in audit report |
| Standards coverage | PARTIAL | 26,884 files on disk but only 425 in transfer ledger (1.6%) |
| Conference papers | POOR | 38,526 files exist with 0% indexing — highest-value gap |
| DDE remote drive | POOR | Not indexed, no catalog, not in mounted-source-registry |
| Remote Dropbox/OneDrive | NOT DOCUMENTED | Unknown contents, not accessible currently |
| INDEX.md files | GOOD | Present in Production/, 0_mrv/, umbilical/ |
| Cross-drive dedup | PARTIAL | Mounted-source-registry defines rules but no dedup audit done |

---

## 1. Mount Point Inventory

### 1.1 /mnt/ace — Primary Engineering Storage (7.3 TB, 67% used)

**Device:** `/dev/sda1` (ext4, local to ace-linux-1)
**Alias:** `/mnt/ace-data` (symlink)
**Network:** NFS-shared rw to ace-linux-2

| Directory | Type | Size Est. | Files | Description |
|-----------|------|-----------|-------|-------------|
| `O&G-Standards/` | Standards library | 38 GB | 26,884 | Industry codes: API(574), ASTM(25537), ISO(308), DNV(100), ABS(30), BSI(76), Norsok(9), SNAME(145), OnePetro(94) |
| `docs/` | Project archives | ~3.4 TB | 100K+ | 119 project folders (0063-0200+), conferences/, engineering-refs/, _archive/ |
| `docs/conferences/` | Conference papers | ~50 GB | 38,526 | OMAE(13126), OTC(8500), DOT(7516), ISOPE(4516), + 26 more conferences |
| `digitalmodel/` | Domain docs overflow | varies | varies | 22+ domain literature folders with download scripts |
| `client_projects/` | Client archives | varies | varies | 50+ project folders (legacy + active) |
| `Production/` | Production eng | 960 MB | varies | ESP, EOR, GIS, Halliburton, training materials |
| `2H/` | Riser engineering | varies | varies | 15+ riser/wellhead projects (31057-31290) |
| `doris/` | Floating systems | varies | varies | FPSO projects (Zama, Lakach, SESA), OrcaFlex models |
| `frontierdeepwater/` | Deepwater eng | varies | varies | Agent-OS enabled repo, deepwater analysis |
| `saipem/` | EPC/installation | varies | varies | Yellowtail project, admin |
| `data/` | Datasets | varies | varies | document-index, osi-datasets, legacy HDD archives |
| `.ace-knowledge/` | Knowledge DB | 1.2 GB | 2 | SQLite index.db for cross-drive search |
| `scripts/` | Maintenance | small | 3 | build-manifest.py + tests |
| `assets.json` | Machine manifest | 19 MB | 1 | Auto-generated drive inventory |

### 1.2 /mnt/local-analysis — Workspace Hub Home (932 GB, 7% used)

**Device:** `/dev/sdc1` (NTFS/fuseblk, local to ace-linux-1)

| Directory | Type | Files | Description |
|-----------|------|-------|-------------|
| `workspace-hub/` | Main git repo | 534K+ | Engineering workspace with all sub-repos, data pipelines, AI agent infrastructure |

Key subdirectories within workspace-hub:
- `data/document-index/` — Master index (1M+ records), registry, ledger, summaries
- `data/doc-intelligence/` — Extracted requirements (12M), constants (4.9M), equations (2M), procedures (1.4M)
- `data/standards/` — Promoted standards extracts
- `data/design-codes/` — Code registry (30+ codes with edition tracking)
- `docs/document-intelligence/` — THIS directory — maps, audits, coverage reports
- `docs/resources/` — 14 domain resource pages (cad, cfd, hydro, marine, etc.)
- `scripts/data/document-index/` — 16 pipeline scripts (phases A-G)
- `scripts/data/doc_intelligence/` — 98+ extraction library (parsers, promoters, tests)

### 1.3 /mnt/remote/ace-linux-2/dde — Remote DDE Drive (2.8 TB, 70% used)

**Device:** SSHFS mount from ace-linux-2 `/mnt/dde`
**Status:** NOT in mounted-source-registry, NOT indexed — MAJOR GAP

| Directory | Type | Est. Files | Description |
|-----------|------|------------|-------------|
| `documents/` | Project archives | 99+ folders | Historical project docs (0063-0200+, mirrors /mnt/ace/docs partially) |
| `Literature/` | Books & references | 500+ | 33 topic dirs: Engineering, Oil & Gas, Finance, MBA, Career, etc. |
| `Literature/Engineering/` | Eng textbooks | 50+ | Petroleum refining, heat transfer, environmental, FFT, reservoir eng |
| `Literature/Oil and Gas/` | O&G literature | 80+ | Reservoir eng, peak oil, pipeline, SPE papers |
| `0000 O&G/` | Standards (legacy) | 1000+ | OLDER standards collection — 36 org dirs (includes ASME, ASCE, AWS, NACE, IEC not in /mnt/ace) |
| `0000 O&G/0000 Codes & Standards/` | Codes DB | varies | Has `Codes & Standards Database.xls` master index |
| `Orcaflex/` | OrcaFlex models | varies | Drilling riser development, Shell Stones, Mecor S-Lay |
| `g-drive/` | Google Drive export | 30+ | AceEngineer financials, document registers, idea logs, invoices |
| `o-drive/` | OneDrive archive | 15+ | FFS assessments (018), ODA drilling (017), offshore data |
| `dropbox_contents/` | Dropbox archive | varies | Engineering projects (0145-0197), Python support, references |
| `FreeSpanVIVFatigue/` | MATLAB code | 13 | VIV fatigue analysis scripts (TwoH pipeline span) |
| `Information_Important/` | Personal docs | 15+ | Green card, SPE membership, job search |
| `Personal/` | Personal | varies | OTC2015 conference attendance |
| `TECH Animation Fundaes/` | 3D animation | 3 | 3DS Max, Blender manuals |
| `TECH Writing/` | Writing guides | 2 | BBC, Economist style guides |

### 1.4 /mnt/remote/ace-linux-2/local-analysis — Remote Analysis Drive (932 GB, 6% used)

**Device:** SSHFS mount from ace-linux-2 `/mnt/local-analysis`

| Directory | Type | Description |
|-----------|------|-------------|
| `workspace-hub/` | Git repo (ace-linux-2 clone) | Separate working copy |
| `Dropbox/` | Dropbox sync | Currently empty/inaccessible |
| `OneDrive/` | OneDrive sync | Currently empty/inaccessible |
| `capytaine-env/` | Python venv | Capytaine hydrodynamics |
| `fluids-env/` | Python venv | Fluids library |
| `marker-env/` | Python venv | PDF-to-text marker |
| `raft-env/` | Python venv | RAFT (floating platform) |
| `sectionprops-env/` | Python venv | Cross-section properties |
| `cli-anything-env/` | Python venv | CLI utilities |

---

## 2. Document Intelligence Infrastructure

### 2.1 Indexed & Searchable Systems

| System | Location | Records | Search Method | Status |
|--------|----------|---------|---------------|--------|
| **Master Document Index** | `data/document-index/index.jsonl` | 1,033,933 | Phase A script scan | ACTIVE |
| **LLM Summaries** | `data/document-index/summaries/` | 639,585 | SHA-keyed lookup | 61.9% done |
| **O&G Standards Semantic Search** | `/mnt/ace/O&G-Standards/_inventory.db` | 27,980 docs, 1,043,616 chunks | Sentence-transformer embeddings | ACTIVE |
| **O&G Standards FTS** | Same DB, `documents_fts` table | 27,980 | SQLite FTS5 | ACTIVE |
| **O&G Standards OCR** | `/mnt/ace/O&G-Standards/_ocr_text/` | varies | Pre-extracted text by org | ACTIVE |
| **ACE Knowledge DB** | `/mnt/ace/.ace-knowledge/index.db` | unknown | SQLite | ACTIVE |
| **Standards Transfer Ledger** | `data/document-index/standards-transfer-ledger.yaml` | 425 entries | YAML lookup | ACTIVE |
| **Design Code Registry** | `data/design-codes/code-registry.yaml` | 30+ codes | YAML lookup | ACTIVE |
| **Online Resource Registry** | `data/document-index/online-resource-registry.yaml` | 247 entries | YAML lookup | ACTIVE |
| **Machine Manifest** | `/mnt/ace/assets.json` | 22 top-level entries | JSON lookup | ACTIVE |

### 2.2 Extraction Pipeline (7 Phases)

All scripts: `scripts/data/document-index/`

| Phase | Script | Lines | Input | Output | Status |
|-------|--------|-------|-------|--------|--------|
| A | `phase-a-index.py` | 389 | Mount sources | `index.jsonl` (1M records) | COMPLETE |
| B | `phase-b-extract.py` + `phase-b-claude-worker.py` | 769 | Index records | `summaries/<sha>.json` (639K) | 62% done |
| C | `phase-c-classify.py` | 345 | Index + summaries | `enhancement-plan.yaml` | COMPLETE |
| D | `phase-d-data-sources.py` | 283 | Enhancement plan | Per-repo data-source YAMLs | COMPLETE |
| E | `phase-e-registry.py` + 2 sub-phases | 943 | All prior | `registry.yaml` | COMPLETE |
| F | `phase-f-wrk-items.py` + gap generator | 612 | Enhancement plan | WRK backlog items | COMPLETE |
| G | `phase-g-wrk-items.py` | 330 | Hardcoded missions | Strategic gap WRKs | COMPLETE |

### 2.3 Structured Extracts (Phase B Deep Output)

| Extract Type | Records | Location |
|-------------|---------|----------|
| Requirements | 12.0M | `data/doc-intelligence/requirements.jsonl` |
| Constants | 4.9M | `data/doc-intelligence/constants.jsonl` |
| Equations | 2.0M | `data/doc-intelligence/equations.jsonl` |
| Procedures | 1.4M | `data/doc-intelligence/procedures.jsonl` |
| Definitions | 717K | `data/doc-intelligence/definitions.jsonl` |
| Worked Examples | 279K | `data/doc-intelligence/worked_examples.jsonl` |
| Deep Tables | varies | `data/doc-intelligence/deep/tables/<domain>/` |
| Deep Charts | varies | `data/doc-intelligence/deep/charts/<domain>/` |
| Naval Arch Catalog | 144 docs | `data/doc-intelligence/naval-architecture-catalog.yaml` |

### 2.4 Domain Coverage (Standards Transfer Ledger)

| Domain | Total | Done | Gap | WRK Captured | Coverage % |
|--------|------:|-----:|----:|-------------:|-----------:|
| materials | 122 | 0 | 93 | 2 | 0% |
| structural | 72 | 4 | 24 | 3 | 6% |
| pipeline | 55 | 12 | 13 | 10 | 22% |
| process | 55 | 0 | 53 | 0 | 0% |
| marine | 33 | 4 | 2 | 1 | 12% |
| cad | 23 | 0 | 22 | 0 | 0% |
| installation | 22 | 0 | 11 | 0 | 0% |
| cathodic-protection | 19 | 9 | 2 | 6 | 47% |
| regulatory | 15 | 0 | 7 | 0 | 0% |
| drilling | 9 | 0 | 8 | 1 | 0% |
| **TOTAL** | **425** | **29** | **235** | **23** | **6.8%** |

---

## 3. Mounted Source Registry (8 Sources)

Defined in `data/document-index/mounted-source-registry.yaml`:

| Source ID | Mount Root | Type | Indexed | Notes |
|-----------|-----------|------|---------|-------|
| `workspace_hub_local` | `/mnt/local-analysis/workspace-hub` | local | YES | In-repo canonical source |
| `ace_standards_local` | `/mnt/ace/docs/_standards` | local | YES | Symlink to O&G-Standards/ |
| `og_standards_local` | `/mnt/ace/0000 O&G` | local | YES | Legacy standards mount |
| `ace_project_local` | `/mnt/ace/docs` | local | YES | 119 project folders |
| `research_literature_local` | `/mnt/ace-data/digitalmodel/docs/domains` | local | YES | Domain-organized PDFs |
| `riser_eng_job_local` | `/mnt/ace/digitalmodel/...` | local | YES | 15,449 riser eng files |
| `dde_project_remote` | env: `DDE_PROJECT_REMOTE_ROOT` | remote | NO — GAP | Fallback to cached metadata |
| `api_metadata_virtual` | `api://worldenergydata` | api | PARTIAL | API-backed metadata |

---

## 4. Critical Gaps & Recommendations

### 4.1 HIGH PRIORITY — Conference Papers (38,526 files, 0% indexed)

The conference paper collection is the single highest-value unindexed resource:

| Conference | Files | Estimated Value |
|-----------|-------|-----------------|
| OMAE | 13,126 | Offshore mechanics, riser/mooring, VIV, structural — CORE domain |
| OTC | 8,500 | Offshore technology, deepwater — CORE domain |
| DOT | 7,516 | Deep offshore technology — CORE domain |
| ISOPE | 4,516 | Ocean/polar engineering — HIGH value |
| UK Conference | 2,725 | UK offshore engineering |
| NACE | 561 | Corrosion/CP — directly feeds cathodic-protection domain |
| Flow Induced Vibration | 229 | VIV — critical for riser analysis |
| Arctic Technology | 216 | Arctic offshore |
| Subsea Tieback | 214 | Subsea engineering |
| 21 more | 2,139 | Various (SPE, SNAME, Rio O&G, DeepGulf, etc.) |

**Action:** Run Phase A indexing on `/mnt/ace/docs/conferences/`, then Phase B summarization.
**Script:** `uv run scripts/data/document-index/phase-a-index.py --source conferences`

### 4.2 HIGH PRIORITY — DDE Remote Drive (not indexed, not in registry)

The DDE drive on ace-linux-2 contains:
- **99+ project folders** in `documents/` (partial overlap with /mnt/ace/docs)
- **Legacy standards collection** in `0000 O&G/` with orgs NOT in /mnt/ace: ASME, ASCE, AWS, NACE, IEC, NFPA, FAA, CFR
- **Engineering literature** — textbooks, reservoir eng, heat transfer
- **OrcaFlex models** — drilling riser, wellhead fatigue analysis
- **FreeSpanVIVFatigue/** — 13 MATLAB scripts for pipeline VIV
- **Dropbox/OneDrive archives** — engineering project backups

**Actions:**
1. Add `dde_literature_remote` and `dde_standards_remote` to mounted-source-registry.yaml
2. Run dedup audit against /mnt/ace to identify unique content
3. Index unique DDE content into Phase A pipeline
4. Migrate `0000 O&G/0000 Codes & Standards/Codes & Standards Database.xls` index

### 4.3 MEDIUM PRIORITY — Standards Ledger Coverage (1.6% of files on disk)

- 26,884 standard files exist on disk
- Only 425 are in the transfer ledger
- ASTM has 25,537 files but only 97 in ledger (0.4%)
- SNAME (145), OnePetro (94), BSI (76), Norsok (9) have 0 ledger entries

**Action:** Run `phase-e2-remap.py` expansion to bulk-add unledgered standards.

### 4.4 MEDIUM PRIORITY — Cross-Drive Deduplication

Known overlaps:
- `/mnt/ace/docs/` ↔ `/mnt/remote/ace-linux-2/dde/documents/` (99+ project folders)
- `/mnt/ace/O&G-Standards/` ↔ DDE `0000 O&G/0000 Codes & Standards/` (partial overlap, DDE has more orgs)
- `/mnt/ace/digitalmodel/docs/domains/` ↔ DDE `Literature/Engineering/` and `Literature/Oil and Gas/`

**Action:** Script a SHA-256 dedup audit across drives.

### 4.5 LOW PRIORITY — Legacy Data Triage

- `data/va-hdd-2/` (240 GB) — mostly personal media, `2HDD Literature/` may have engineering value
- `data/2021-11-22-sd-HDD/` (30 GB) — personal backup
- DDE `Literature/` non-engineering dirs (Finance, MBA, Career, etc.) — business knowledge

---

## 5. How to Use This Resource Intelligence

### 5.1 Finding a Standard

```bash
# Semantic search (best for conceptual queries)
uv run --no-project python /mnt/ace/O&G-Standards/search_og_standards.py "fatigue S-N curve" 20

# File search (best for known standard numbers)
find /mnt/ace/O&G-Standards/ -name "*API*579*" -type f

# DDE legacy standards (has orgs not in /mnt/ace)
find "/mnt/remote/ace-linux-2/dde/0000 O&G/" -name "*ASME*" -type f

# Check the transfer ledger for implementation status
grep "API 579" /mnt/local-analysis/workspace-hub/data/document-index/standards-transfer-ledger.yaml
```

### 5.2 Finding Domain Literature

```bash
# Research literature by domain
ls /mnt/ace/digitalmodel/docs/domains/<domain>/literature/

# Available domains:
# cathodic_protection, geotechnical, hydrodynamics, naval_architecture,
# pipeline, structural, structural-parachute, subsea

# DDE engineering literature (broader topics)
ls "/mnt/remote/ace-linux-2/dde/Literature/Engineering/"
ls "/mnt/remote/ace-linux-2/dde/Literature/Oil and Gas/"
```

### 5.3 Finding Project Documentation

```bash
# Primary project archive (119 folders)
ls /mnt/ace/docs/ | grep "^0[0-9]"

# Client-specific repos on /mnt/ace
ls /mnt/ace/2H/        # Riser engineering
ls /mnt/ace/doris/     # FPSO/floating
ls /mnt/ace/saipem/    # EPC/installation

# DDE project archive (may have files not in /mnt/ace)
ls /mnt/remote/ace-linux-2/dde/documents/

# DDE Dropbox project backups
ls /mnt/remote/ace-linux-2/dde/dropbox_contents/Engineering/
```

### 5.4 Finding Conference Papers

```bash
# All conferences
ls /mnt/ace/docs/conferences/

# Specific conference
find /mnt/ace/docs/conferences/OMAE/ -name "*.pdf" | wc -l

# DDE also has some conference content
ls "/mnt/remote/ace-linux-2/dde/Literature/Engineering/OTC2004/"
```

### 5.5 Finding Extracted Intelligence

```bash
# Search extracted requirements
grep -i "mooring" /mnt/local-analysis/workspace-hub/data/doc-intelligence/requirements.jsonl | head -5

# Search extracted equations
grep -i "catenary" /mnt/local-analysis/workspace-hub/data/doc-intelligence/equations.jsonl | head -5

# Domain catalogs
cat /mnt/local-analysis/workspace-hub/data/doc-intelligence/naval-architecture-catalog.yaml

# Deep extraction reports
ls /mnt/local-analysis/workspace-hub/data/doc-intelligence/deep/
ls /mnt/local-analysis/workspace-hub/data/doc-intelligence/extraction-reports/
```

### 5.6 Running the Pipeline

```bash
# Regenerate master index
cd /mnt/local-analysis/workspace-hub
uv run scripts/data/document-index/phase-a-index.py

# Run summarization batch
uv run scripts/data/document-index/phase-b-extract.py

# Update drive manifest
uv run /mnt/ace/scripts/build-manifest.py

# Generate coverage report
uv run scripts/data/document-index/generate-coverage-report.py
```

---

## 6. Open-Source Engineering Repositories on /mnt/ace

| Repository | Domain | Key Content | Use Case |
|-----------|--------|-------------|----------|
| `capytaine/` | Hydrodynamics | BEM solver, Python API | Diffraction/radiation analysis |
| `openfast/` | Marine/Wind | Aero-hydro-servo-elastic | Floating wind turbine analysis |
| `HAMS/` | Hydrodynamics | BEM solver, Fortran | Alternative to OrcaWave/AQWA |
| `MoorDyn/` | Marine | Mooring dynamics, C++ | Dynamic mooring line analysis |
| `MoorPy/` | Marine | Mooring statics, Python | Quick mooring system design |
| `WEC-Sim/` | Hydrodynamics | Wave energy converter, MATLAB | WEC device simulation |
| `gmsh/` | CAD/Mesh | Mesh generator, C++ | FEM mesh generation |
| `opm-common/` | Reservoir | OPM reservoir sim | Reservoir simulation support |

All are cloned git repos available for reference, benchmarking, and integration.

---

## 7. Existing Documentation Quality Scorecard

| Document | Location | Quality | Last Updated | Gap |
|----------|----------|---------|-------------|-----|
| `/mnt/ace/README.md` | Mount root | GOOD | 2026-03-25 | Missing DDE reference |
| `assets.json` | Mount root | GOOD | 2026-03-26 | Auto-generated, current |
| `data-intelligence-map.md` | docs/document-intelligence/ | EXCELLENT | ~2026-04 | Most complete reference |
| `document-intelligence-audit.md` | docs/assessments/ | EXCELLENT | 2026-04-02 | Pipeline fully documented |
| `ace-undiscovered-resources.md` | docs/reports/ | GOOD | 2026-04-01 | Actionable gap list |
| `domain-coverage.md` | docs/document-intelligence/ | GOOD | 2026-04-02 | Auto-generated |
| `mounted-source-registry.yaml` | data/document-index/ | GOOD | 2026-02-28 | Missing DDE Literature source |
| `Production/INDEX.md` | /mnt/ace/ | GOOD | 2026-02-20 | Placeholder migration done |
| `0_mrv/INDEX.md` | /mnt/ace/ | GOOD | 2026-02-20 | All placeholders |
| `umbilical/INDEX.md` | /mnt/ace/ | GOOD | 2026-02-20 | Stub only |
| `docs/resources/*.md` (14 files) | docs/resources/ | GOOD | varies | Online resource guides |

### Documentation That Does NOT Exist Yet

| Missing Document | Priority | Description |
|-----------------|----------|-------------|
| DDE drive catalog | HIGH | No index/catalog for remote DDE drive contents |
| Conference paper index | HIGH | 38,526 files with zero metadata |
| Cross-drive dedup report | MEDIUM | No audit of duplicates across drives |
| DDE-to-ace migration map | MEDIUM | Which DDE content has been migrated, which is unique |
| Legacy data triage report | LOW | va-hdd-2 engineering content assessment |
| MATLAB code catalog | LOW | FreeSpanVIVFatigue + any other MATLAB on DDE |

---

## 8. Architecture Diagram

```
ace-linux-1 (this machine)
├── /mnt/ace (7.3 TB ext4, local) ←──── Primary engineering storage
│   ├── O&G-Standards/ (38 GB, 26,884 files, semantic search DB)
│   ├── docs/ (119 project folders + conferences/ + engineering-refs/)
│   │   └── conferences/ (38,526 papers — NOT indexed)
│   ├── digitalmodel/docs/domains/ (research literature by domain)
│   ├── client_projects/ (50+ project archives)
│   ├── 2H/, doris/, saipem/, frontierdeepwater/... (client repos)
│   ├── Production/, 0_mrv/, umbilical/ (domain archives with INDEX.md)
│   ├── .ace-knowledge/index.db (1.2 GB knowledge DB)
│   ├── assets.json (machine-readable manifest)
│   └── capytaine/, openfast/, HAMS/, MoorDyn/, MoorPy/... (OSS repos)
│
├── /mnt/local-analysis (932 GB NTFS, local)
│   └── workspace-hub/ (git repo — main working tree)
│       ├── data/document-index/ (1M+ index, 639K summaries)
│       ├── data/doc-intelligence/ (21M+ extracted records)
│       ├── data/design-codes/ (30+ codes registry)
│       ├── scripts/data/ (pipeline + extraction library)
│       └── docs/document-intelligence/ (THIS knowledge map)
│
├── /mnt/remote/ace-linux-2/dde (2.8 TB, SSHFS) ←──── NOT INDEXED
│   ├── documents/ (99 project folders)
│   ├── Literature/ (33 topic dirs — Engineering, O&G, Finance...)
│   ├── 0000 O&G/ (legacy standards — has ASME, ASCE, AWS, NACE, IEC)
│   ├── Orcaflex/ (drilling riser models)
│   ├── g-drive/ (Google Drive export — financials, doc register)
│   ├── o-drive/ (OneDrive archive — FFS, ODA, manuals)
│   ├── dropbox_contents/ (project backups, references)
│   └── FreeSpanVIVFatigue/ (MATLAB VIV scripts)
│
└── /mnt/remote/ace-linux-2/local-analysis (932 GB, SSHFS)
    ├── workspace-hub/ (ace-linux-2 clone)
    ├── Dropbox/, OneDrive/ (currently empty)
    └── *-env/ (Python virtual environments)
```

---

## 9. Quick Reference: "Where Is...?"

| Looking for... | Go to... |
|---------------|----------|
| An API/DNV/ISO standard | `/mnt/ace/O&G-Standards/<org>/` + semantic search via `search_og_standards.py` |
| An ASME/ASCE/AWS/NACE standard | `/mnt/remote/ace-linux-2/dde/0000 O&G/0000 Codes & Standards/<org>/` (NOT in /mnt/ace) |
| Conference paper (OMAE, OTC, DOT) | `/mnt/ace/docs/conferences/<conf>/` |
| Domain research literature | `/mnt/ace/digitalmodel/docs/domains/<domain>/literature/` |
| Project documentation | `/mnt/ace/docs/0NNN...` or `/mnt/ace/<client>/` |
| OrcaFlex model files | `/mnt/ace/doris/orcaflex/` or `/mnt/remote/ace-linux-2/dde/Orcaflex/` |
| Extracted equations/constants | `data/doc-intelligence/equations.jsonl` / `constants.jsonl` |
| Standards implementation status | `data/document-index/standards-transfer-ledger.yaml` |
| Online learning resources | `docs/resources/<domain>-resources.md` (14 domain pages) |
| Engineering textbook PDFs | `/mnt/remote/ace-linux-2/dde/Literature/Engineering/` |
| O&G industry literature | `/mnt/remote/ace-linux-2/dde/Literature/Oil and Gas/` |
| FFS assessment templates | `/mnt/remote/ace-linux-2/dde/o-drive/018 FFS/` |
| VIV/fatigue MATLAB code | `/mnt/remote/ace-linux-2/dde/FreeSpanVIVFatigue/` |
| Business admin/invoices | `/mnt/ace/aceengineer-admin/` or DDE `g-drive/` |
| Drive manifest (machine-readable) | `/mnt/ace/assets.json` |
| Knowledge search DB | `/mnt/ace/.ace-knowledge/index.db` |

---

## 10. Maintenance Commands

```bash
# Rebuild /mnt/ace manifest
uv run /mnt/ace/scripts/build-manifest.py

# Re-run document index (Phase A)
cd /mnt/local-analysis/workspace-hub
uv run scripts/data/document-index/phase-a-index.py

# Generate coverage report
uv run scripts/data/document-index/generate-coverage-report.py

# Semantic search standards
uv run --no-project python /mnt/ace/O&G-Standards/search_og_standards.py "your query" 20

# Check mount availability
mount | grep -E '/mnt'
df -h | grep -E '/mnt'
```
