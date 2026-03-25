# WRK-1355: Consolidate /mnt/ace — Single Source of Truth

## Context

WRK-1341 relocated ~46 GB from 10 git repos to `/mnt/ace/<repo>/`, but the drive already had
disorganized legacy content (HDD dumps, duplicate-looking dirs, root clutter). This plan
creates a single source of truth with canonical locations, deduplication, and an LLM-assisted
classification pipeline for unsorted files.

**Drive:** 7.3 TB, 66% used (4.5 TB). Plenty of headroom.

## Canonical Directory Structure (target state)

```
/mnt/ace/
├── README.md                          # NEW — drive manifest & conventions
├── assets.json                        # NEW — machine-readable manifest
│
├── digitalmodel/                      # Repo overflow (WRK-1341)
│   ├── docs/<84 domains>/             # Already organized by domain
│   ├── projects/
│   └── tests/
├── worldenergydata/                   # Repo overflow
├── frontierdeepwater/                 # Repo overflow
├── client_projects/                   # Repo overflow
├── rock-oil-field/                    # Repo overflow
├── saipem/                            # Repo overflow
├── doris/                             # Repo overflow
├── seanation/                         # Repo overflow
├── aceengineer-admin/                 # Repo overflow
├── OGManufacturing/                   # Repo overflow
├── 2H/                                # Repo overflow
├── 0_mrv/                             # Repo overflow
├── umbilical/                         # Repo overflow
│
├── docs/                              # Project & discipline archive
│   ├── disciplines/                   # 9 O&G disciplines (3.4 TB) — KEEP
│   │   ├── abandonment/
│   │   ├── completion/
│   │   ├── drilling/
│   │   ├── exploration/
│   │   ├── integrity_management/
│   │   ├── interventions/
│   │   ├── knowledge_skills/
│   │   ├── misc/
│   │   └── production/
│   ├── _standards -> /mnt/ace/O&G-Standards   # Existing symlink — KEEP
│   ├── system-admin/                  # NEW — relocated root scripts/docs
│   └── <numbered projects>/           # Existing 0xxx/7xxx projects — KEEP
│
├── O&G-Standards/                     # 38 GB industry standards — KEEP (canonical)
│
├── Production/                        # 960 MB production engineering — KEEP
│
├── data/                              # Legacy data archive
│   ├── va-hdd-2/                      # 883 GB — TRIAGE per Phase 2
│   │   ├── engineering/               # NEW — relocated engineering dirs
│   │   └── personal/                  # Remaining personal/media (leave as-is)
│   └── 2021-11-22-sd-HDD/            # 30 GB personal — LEAVE AS-IS per user
│
├── _ss_repo/                          # 193 GB — TRIAGE per Phase 3
│   └── 0127 Mooring Analysis/        # UNIQUE 193 GB — must keep/relocate
│
├── .ace-knowledge/                    # Existing knowledge DB — KEEP
└── lost+found/                        # Filesystem — KEEP
```

## Execution Phases

### Phase 1: Root Cleanup (< 10 min)

Quick wins — remove clutter from drive root.

| Action | Item | Command |
|--------|------|---------|
| Delete | `O` (empty file) | `rm /mnt/ace/O` |
| Delete | `$RECYCLE.BIN/` | `rm -rf '/mnt/ace/$RECYCLE.BIN'` |
| Create | `docs/system-admin/` | `mkdir -p /mnt/ace/docs/system-admin` |
| Move | 3 shell scripts | `mv /mnt/ace/*.sh /mnt/ace/docs/system-admin/` |
| Move | 3 markdown guides | `mv /mnt/ace/*SAMBA*.md /mnt/ace/github_issue*.md /mnt/ace/LESSON*.md /mnt/ace/docs/system-admin/` |
| Move | LINUX_SYSTEM_STATUS.txt | `mv /mnt/ace/LINUX_SYSTEM_STATUS.txt /mnt/ace/docs/system-admin/` |

**Result:** Drive root contains only canonical directories + README.md + assets.json.

### Phase 2: va-hdd-2 Engineering Extraction (~94 GB → digitalmodel)

Extract engineering content from legacy HDD, leave personal media in place.

#### 2a. Relocate 2H-era project archives (94 GB)

Destination: `/mnt/ace/digitalmodel/docs/domain/subsea-risers/`
(fits the existing 84-domain taxonomy under digitalmodel)

| Source | Size | Destination subdir |
|--------|------|--------------------|
| `2HDD 2100 BLK31 SLOR Design` | 53G | `2h-projects/2100-blk31-slor/` |
| `2HDD 3824 - BP Macondo Containment Riser Analysis` | 30G | `2h-projects/3824-macondo-containment/` |
| `2HDD 3836 - BP Macondo - HP1 Riser Systems Engineering` | 7.4G | `2h-projects/3836-macondo-hp1/` |
| `2HDD 3837 - BP CDP 2 FSR  Engineering` | 3.7G | `2h-projects/3837-bp-cdp2-fsr/` |

#### 2b. LLM-assisted extraction & classification

The va-hdd-2 engineering dirs contain extractable data, algorithms, and methods
that should feed into digitalmodel — not just be archived.

**Step 1: Inventory scan** — For each engineering dir, catalog files by type:
- Input files (.dat, .yml, .xlsx, .csv) → highest priority to extract
- Analysis scripts (.py, .m, .vbs) → extract algorithms for digitalmodel
- Reports (.pdf, .docx) → classify into domain taxonomy
- CAD/model files (.dxf, .wbpz, .sim) → keep with project context
- Raw output/results (large binary) → can regenerate, lower priority

**Step 2: LLM classification** — For each file:

```python
# Script: /mnt/ace/scripts/classify-files.py
# 1. Extract filename, path, size, extension
# 2. For PDFs: extract first-page text via pdftotext
# 3. For code: read first 50 lines
# 4. Send to LLM with domain taxonomy (84 digitalmodel domains + 9 disciplines)
# 5. Output: { file, suggested_domain, confidence, reasoning, extract_type }
#    extract_type: "algorithm" | "data" | "reference" | "archive" | "personal"
# 6. High-confidence (>0.8) → auto-move; low-confidence → human review queue
```

**Domain taxonomy for LLM prompt:**
- 84 digitalmodel domains (tool/method-focused): ansys, orcaflex, fatigue, risers, mooring, etc.
- 9 discipline categories (business/operational): drilling, completion, production, etc.
- Rule: tool-focused → digitalmodel; project-bound → disciplines; personal → leave in data/

**Step 3: Relocate by classification**

| Source | Size | Destination |
|--------|------|-------------|
| 2H project archives (×4) | 94G | `/mnt/ace/digitalmodel/docs/domain/subsea-risers/2h-projects/` |
| `2HDD Literature/Engineering/` | 7.7G | `/mnt/ace/digitalmodel/docs/domain/references/literature/engineering/` |
| `2HDD Literature/Oil and Gas/` | 373M | `/mnt/ace/digitalmodel/docs/domain/references/literature/oil-and-gas/` |
| `2HDD AceMatrix/` (engineering proposals) | subset | LLM-classified into relevant domains |
| `2HDD AceMatrix/` (admin/tax/legal) | subset | `/mnt/ace/data/archive/acematrix-admin/` |
| `2HDD Installation Programs/` | 49G | DELETE (outdated: ANSYS 10-17, SolidWorks 2011) |
| LLM-classified algorithms/scripts | varies | Extracted into digitalmodel source repos as WRK items |

### Phase 3: _ss_repo Triage (193 GB)

#### 3a. Merge unique files from small projects

| Item | Size | Action |
|------|------|--------|
| `008 GoM Wells` | 109 MB | Merge CAL/, MAN/, REF/, test/ → `/mnt/ace/client_projects/energy_engineering/008 GoM Wells/` |
| `0113 Drilling Riser Dev` + offsets.xlsx | 7 MB | Copy Rev5/ + offsets.xlsx → `/mnt/ace/client_projects/energy_engineering/0113 Orc DR/` |

After merge, delete `_ss_repo/008*` and `_ss_repo/0113*`.

#### 3b. Triage 0127 Mooring Analysis (193 GB — simulation runs)

These are OrcaFlex simulation runs. Strategy: **keep input files, delete regenerable output.**

**Step 1: Identify input vs output files**
```bash
# Input files to KEEP (small): .dat, .yml, .yaml, .csv, .xlsx, .py, .m
find "/mnt/ace/_ss_repo/0127 Mooring Analysis/" -type f \
  \( -name "*.dat" -o -name "*.yml" -o -name "*.yaml" -o -name "*.csv" \
     -o -name "*.xlsx" -o -name "*.py" -o -name "*.m" \) \
  -exec du -ch {} + | tail -1
# Output files (large, regenerable): .sim, .res, .rfx, animation files
find "/mnt/ace/_ss_repo/0127 Mooring Analysis/" -type f \
  \( -name "*.sim" -o -name "*.res" -o -name "*.rfx" \) \
  -exec du -ch {} + | tail -1
```

**Step 2: Extract inputs** → `/mnt/ace/digitalmodel/docs/domain/mooring/0127-mooring-analysis/inputs/`

**Step 3: Verify** input files are self-contained (can regenerate outputs)

**Step 4: Delete** `_ss_repo/` entirely (~193 GB recovered)

After relocation, `_ss_repo/` directory is deleted.

### Phase 4: Build assets.json Manifest

Per ORGANIZATION_PLAN.md, create a machine-readable manifest of all content.

```python
# Script: /mnt/ace/scripts/build-manifest.py
# Crawls /mnt/ace/ and produces:
{
  "generated": "2026-03-25T...",
  "drive": "/mnt/ace",
  "total_size_gb": 4500,
  "entries": [
    {
      "path": "digitalmodel/docs/domain/subsea-risers/2h-projects/",
      "size_gb": 94,
      "type": "engineering_archive",
      "source": "va-hdd-2 (WRK-1355 relocation)",
      "domains": ["subsea-risers"],
      "tags": ["2H-offshore", "riser-analysis", "macondo"]
    },
    ...
  ]
}
```

**Metadata per entry:** path, size, type (repo_overflow | engineering_archive | standards | personal | system), source origin, domain tags, last modified.

### Phase 5: Deduplication Scan

After all relocations, run a dedup check:

```bash
# Find potential duplicates by filename across /mnt/ace/
find /mnt/ace -type f -name "*.pdf" -printf "%f\t%s\t%p\n" | sort | uniq -d -w 100
# Cross-check with fdupes for content-level dedup on high-value dirs
fdupes -r /mnt/ace/digitalmodel/docs/ /mnt/ace/O&G-Standards/
```

### Phase 6: Write README.md

Create `/mnt/ace/README.md` documenting:
- Drive purpose and conventions
- Directory structure with descriptions
- How repo overflow works (symlink pattern from RELOCATION-LOG.md)
- Where to put new files (decision tree)
- How to update assets.json

## Critical Files

| File | Purpose |
|------|---------|
| `/mnt/ace/digitalmodel/RELOCATION-LOG.md` | Existing relocation record from WRK-1341 |
| `docs/assessments/ORGANIZATION_PLAN.md` | Original plan with assets.json spec |
| `/mnt/ace/O&G-Standards/_catalog.json` | Existing standards catalog format |
| `/mnt/ace/.ace-knowledge/` | Existing knowledge DB |

## Verification

1. After Phase 1: `ls /mnt/ace/` shows only canonical dirs + README + assets.json
2. After Phase 2: engineering content extracted from va-hdd-2, algorithms cataloged
3. After Phase 3: `_ss_repo/` directory no longer exists, inputs preserved in digitalmodel
4. After Phase 4: `python -m json.tool /mnt/ace/assets.json` validates
5. After Phase 5: dedup report shows no actionable duplicates
6. Final: `df -h /mnt/ace` — usage should drop by ~240 GB (49G installers + ~190G sim outputs)

## User Decisions (captured)

1. **va-hdd-2 engineering:** Extract data, algorithms, methods into digitalmodel — not just archive
2. **2021-11-22-sd-HDD (30 GB):** Leave as-is
3. **_ss_repo/0127 (193 GB):** Keep input files only, delete regenerable sim outputs → recover ~190 GB
4. **Root clutter:** Clean up

## Open Decision

1. **LLM classification:** Use Claude API (`classify-files.py`) or manual triage for ambiguous files?
