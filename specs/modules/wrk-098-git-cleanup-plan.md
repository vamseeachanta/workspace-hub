# WRK-098: Git History Cleanup Plan for worldenergydata

| Field          | Value                                         |
|----------------|-----------------------------------------------|
| title          | 7.1GB Git History Cleanup for worldenergydata |
| description    | Audit, plan, and execute removal of large data files from git history |
| version        | 1.0.0                                         |
| module         | worldenergydata                               |
| session.id     | WRK-098                                       |
| session.agent  | claude-opus-4-6                               |
| review         | pending                                       |
| created        | 2026-02-08                                    |
| status         | PLAN                                          |

---

## 1. Current State Assessment

### 1.1 Repository Size Summary

| Metric                          | Value     |
|---------------------------------|-----------|
| `.git/` directory               | 6.8 GB    |
| Total working tree              | 19 GB     |
| Loose objects (count)           | 5,745     |
| Loose objects (size)            | 2.30 GB   |
| Pack files (count)              | 5         |
| Pack files (size)               | 4.40 GB   |
| Total blobs in history          | 10,433    |
| Total blob size in history      | 14.2 GB   |
| Top 50 blobs alone              | 6,972 MB  |
| Total commits                   | 601       |
| Remote                          | github.com/vamseeachanta/worldenergydata.git |

### 1.2 Working Tree Large File Breakdown (>10MB, excluding .git/ and .venv/)

#### data/modules/hse/raw/osha/ -- 6.6 GB (65 tracked files)
The single largest contributor. Contains OSHA enforcement data split across many CSV chunks:
- `osha_violation*.csv` (14 files): 156-492 MB each, ~2.7 GB total
- `osha_inspection*.csv` (5 files): 254-302 MB each, ~1.4 GB total
- `osha_violation_gen_duty_std*.csv` (3 files): 98-492 MB each, ~722 MB total
- `osha_violation_event*.csv` (12 files): 87-91 MB each, ~1.1 GB total
- `osha_optional_info*.csv`, `osha_related_activity*.csv`, `osha_accident*.csv`: 17-113 MB each
- ZIP archives (`*_20260201.csv.zip`): 14-296 MB each, ~800 MB total
- **Regenerable**: YES -- `osha_acquirer.py` downloads from enforcedata.dol.gov

#### data/modules/bsee/ -- 526 MB (278 tracked files)
- `zip/directional_survey/` (directdelimit.zip=97MB, dsptsdelimit.zip=134MB): 231 MB
- `zip/` other datasets (apm, pipeloc, production, offshorestats, etc.): ~150 MB
- `bin/war/mv_war_tubular_summaries.bin`: 15 MB
- `csv/online_query_raw_data/eWellWARRawData_mv_war_main.csv`: 63 MB
- `archive/2025-08-21-legacy.tar.gz`: 60 MB
- **Regenerable**: YES -- `bsee_acquirer.py` and `dwnld_from_zipurl.py` download from data.bsee.gov

#### data/modules/marine_safety/raw/ -- 479 MB (161 tracked files)
- `canadian_tsb/vessel.csv`: 72 MB, `occurrence.csv`: 90 MB, `navigation_equipment.csv`: 26 MB
- `dlp_historical/Vessels_1995-2012.csv`: 28 MB, `Accidents_1995-2012.csv`: 32 MB
- `doe_pipelines/PipelineArea.zip`: 21 MB, `PipelineArea.gpkg`: 30 MB
- `bsee_offshore/excel/cy-2021-excel-spreadsheet.xlsx`: 35 MB
- `bsee_offshore/pdf/incidents_1995-1996.pdf`: 24 MB
- `phmsa_*/PHMSA_Pipeline_Safety_Flagged_Incidents.zip`: 24 MB each
- `marine_safety.db`: 47 MB (working tree) + 60 MB (database/ copy)
- **Regenerable**: PARTIALLY -- scrapers exist for some sources; PDFs/CSVs may need manual re-download

#### data/modules/sodir_zip_data/ -- 156 MB
- `seaArea.csv`: 82 MB
- `prlAreaSplitByBlock.csv`: 23 MB
- `blkArea.csv`: 17 MB
- **Regenerable**: Likely YES (Norwegian Petroleum Directorate open data)

#### docs/modules/bsee/ -- 1.1 GB (tracked)
- `_legacy/` directory: 723 MB -- contains duplicated data, old presentations, PDFs
  - Duplicate files: `mv_boreholes.txt` (13 MB x2), `gepaldmp_Paleo.txt` (22 MB x2), `Deepwater-Gulf-of-Mexico-Report-2014.pdf` (24 MB x2), `First Original Development Plan.pdf` (34 MB x2)
  - Large references: API SPEC 5CT (46 MB), CR1995-Dickerson (26 MB), ENG-0003 (25 MB)
- `data/SME_Roy_attachments/`: 302 MB -- large WAR data text files (33-74 MB each, duplicated across dates)
- **Regenerable**: NO -- reference documents, SME-provided data, legacy artifacts

#### docs/data_science/ -- 437 MB (139 tracked files)
- Reference PDFs: 11-67 MB each (statistical_foundations, NLP, Starting_A_Data_Science_Project, etc.)
- **Regenerable**: NO -- third-party reference materials

#### docs/raw_data/ -- 150 MB
- `bsee/sands/2020 Atlas Update.xlsx`: 12 MB
- `bsee/other/Borehole-by-*.pdf`: 14 MB each
- `bsee/paleo/gepaldmp_Paleo.txt`: 26 MB (third copy!)
- `wind/2020_wind_energy_technology_data_update.xlsx`: 14 MB
- **Regenerable**: PARTIALLY -- some are public downloads, some are unique

#### results/modules/marine_safety/ -- 51 MB
- `hatch_incidents.csv`: 26 MB
- **Regenerable**: YES -- output of analysis pipeline

#### Other notable items in working tree (NOT in .git history):
- `.venv/`: 1.5 GB (already in .gitignore)
- `.swarm/memory.db`: 16 MB (already in .gitignore via `*.db`)
- `htmlcov/`: 56 MB (already in .gitignore)
- `.test_performance.db`: 34 MB (covered by `*.db` gitignore)

### 1.3 Git History Blob Distribution (>10 MB blobs by directory)

| Directory                          | Size (MB) | Blob Count | Notes                           |
|------------------------------------|-----------|------------|---------------------------------|
| data/modules/hse                   | 6,751     | 56         | Multiple versions of OSHA data  |
| data/modules/bsee                  | 2,731     | 138        | ZIP downloads + bin/csv files   |
| tests/modules/bsee                 | 1,099     | 43         | Test results and HTML reports   |
| data/modules/marine_safety         | 623       | 15         | Raw scraped data                |
| docs/modules/bsee                  | 557       | 19         | Legacy docs and SME data        |
| data/modules/posters               | 129       | 6          | Poster image files (deleted)    |
| docs/data_science/ref              | 125       | 4          | Reference PDFs                  |
| data/modules/sodir_zip_data        | 120       | 3          | Norwegian data CSVs             |
| docs/raw_data/bsee                 | 89        | 5          | Raw reference data              |
| results/modules/marine_safety      | 51        | 2          | Analysis output                 |
| **TOTAL (>10MB blobs)**            | **~12,400** | **~300** |                                 |

### 1.4 .gitignore Status

**CRITICAL ISSUE: Merge conflict markers present in .gitignore**

Lines 193-200 contain unresolved merge conflict markers:
```
<<<<<<< HEAD
*.bin

# Large BSEE data files (>100MB GitHub limit)
data/modules/bsee/zip/directional_survey/
data/modules/bsee/zip/war/eWellWARRawData.zip
=======
>>>>>>> origin/main
```

This means:
1. `*.bin` files are NOT being ignored (the rule is inside a conflict block)
2. The BSEE directional survey exclusion is NOT active
3. Any `git add .` operation risks staging bin files or large BSEE ZIPs

**Missing .gitignore rules for major data directories:**
- `data/modules/hse/raw/osha/` -- 6.6 GB of CSVs, no ignore rule
- `data/modules/marine_safety/raw/` -- 479 MB, no ignore rule
- `data/modules/sodir_zip_data/` -- 156 MB, no ignore rule
- `docs/data_science/` large PDFs -- no ignore rule
- `docs/modules/bsee/_legacy/` -- 723 MB, no ignore rule
- `docs/modules/bsee/data/SME_Roy_attachments/` -- 302 MB, no ignore rule
- `data/modules/bsee/bin/` -- no ignore rule (`.gitignore` `*.bin` is inside conflict)

### 1.5 LFS Status

- **git-lfs is NOT installed** on this system
- `.gitattributes` declares 9 LFS tracking rules (`.bin`, specific ZIPs, CSVs, tar.gz)
- Since LFS is not installed, these files are stored as regular git objects
- LFS pointer files may have been committed but actual content stored in regular pack files
- The `*.bin` LFS rule conflicts with the broken `.gitignore` `*.bin` rule

### 1.6 Duplicate Files in Repository

Several files exist in 2-3 locations simultaneously:
- `gepaldmp_Paleo.txt` (22-26 MB): 3 copies (docs/modules/bsee/_legacy/code/mitra/, _legacy/superseded/, docs/raw_data/bsee/paleo/)
- `mv_boreholes.txt` (13 MB): 2 copies (_legacy/code/mitra/, _legacy/superseded/)
- `Deepwater-Gulf-of-Mexico-Report-2014.pdf` (24 MB): 2 copies
- `First Original Development Plan.pdf` (34 MB): 2 copies
- `mv_war_main.txt` (74 MB): 2 copies (SME_Roy 2025-08-01 and 2025-08-20)
- `mv_war_main_prop.txt` (33-34 MB): 2 copies (SME_Roy 2025-08-01 and 2025-08-20)

---

## 2. Cleanup Strategy Recommendation

### Recommended: `git-filter-repo` (Modern, Preferred)

| Tool              | Pros                                        | Cons                                     |
|-------------------|---------------------------------------------|------------------------------------------|
| **git-filter-repo** | Fast, safe, Python-based, actively maintained, handles all edge cases, can filter by path/size/pattern | Requires full clone, rewrites ALL history |
| BFG Repo-Cleaner  | Simple CLI, fast for blob removal           | JVM dependency, less flexible path filtering, unmaintained since 2019 |
| `git filter-branch` | Built into git                             | Extremely slow, deprecated, error-prone  |

**Decision: Use `git-filter-repo`.**

Rationale:
1. We need path-based AND size-based filtering (git-filter-repo excels at both)
2. The repo has 601 commits -- rewrite will be fast
3. Python-based tool fits the project's tech stack
4. Can generate analysis reports before destructive operations
5. Handles `.gitattributes` LFS references cleanly

---

## 3. Pre-Cleanup Checklist

### 3.1 Backup
- [ ] Create a full clone backup: `git clone --mirror origin backup-worldenergydata-$(date +%Y%m%d).git`
- [ ] Archive the current working tree: `tar czf worldenergydata-working-tree-backup.tar.gz --exclude=.git --exclude=.venv .`
- [ ] Verify backup integrity: `cd backup-*.git && git fsck`

### 3.2 Verify Acquirer Scripts
- [ ] Test `osha_acquirer.py` -- can regenerate all 6.6 GB of OSHA data
- [ ] Test `bsee_acquirer.py` -- can regenerate BSEE INCs and incident data
- [ ] Test `dwnld_from_zipurl.py` -- can regenerate BSEE ZIP datasets
- [ ] Test `epa_tri_acquirer.py` -- can regenerate EPA TRI data
- [ ] Verify marine_safety scrapers for Canadian TSB, DLP, USCG data
- [ ] Document any datasets that cannot be regenerated automatically

### 3.3 Document Regenerable vs. Unique Files

| Directory                              | Size    | Regenerable? | Acquirer Script                     |
|----------------------------------------|---------|--------------|-------------------------------------|
| data/modules/hse/raw/osha/            | 6.6 GB  | YES          | osha_acquirer.py                    |
| data/modules/bsee/zip/               | 488 MB  | YES          | dwnld_from_zipurl.py, bsee_acquirer.py |
| data/modules/hse/raw/bsee/           | 33 MB   | YES          | bsee_acquirer.py                    |
| data/modules/hse/raw/epa_tri/        | 64 MB   | YES          | epa_tri_acquirer.py                 |
| data/modules/marine_safety/raw/       | 479 MB  | PARTIAL      | Various scrapers (verify each)      |
| data/modules/sodir_zip_data/          | 156 MB  | LIKELY       | Norwegian open data portal          |
| data/modules/bsee/bin/               | ~15 MB  | YES          | Derived from ZIP data               |
| data/modules/bsee/csv/               | ~63 MB  | YES          | Derived from ZIP data               |
| docs/data_science/                    | 437 MB  | NO           | Reference PDFs (keep out of git)    |
| docs/modules/bsee/_legacy/           | 723 MB  | NO           | Historical artifacts                |
| docs/modules/bsee/data/SME_Roy*/     | 302 MB  | NO           | SME-provided data (archive externally) |
| docs/raw_data/                        | 150 MB  | PARTIAL      | Some public downloads               |
| results/                              | 34 MB   | YES          | Analysis pipeline output            |
| data/modules/marine_safety/*.db       | 107 MB  | YES          | Built from raw data                 |
| tests/modules/bsee/ (large blobs)    | 1,099 MB| YES (mostly) | Test output, HTML reports           |
| data/modules/posters/ (deleted)       | 129 MB  | N/A          | Already deleted, in history only    |

### 3.4 Notify Collaborators
- [ ] Identify all users who have cloned the repo
- [ ] Draft notification explaining: history rewrite date, required actions (re-clone), why
- [ ] Set a rewrite date at least 7 days out
- [ ] Ensure all open PRs are merged or rebased before rewrite

---

## 4. Execution Plan (Phased)

### Phase 1: Fix .gitignore (Immediate, Non-Destructive)

**Objective:** Resolve merge conflict and add comprehensive ignore rules for large data.

1. Resolve the merge conflict at lines 193-200
2. Add ignore rules for all large data directories
3. Keep the `*.bin` rule (it was intended in the HEAD branch)

Proposed additions to `.gitignore`:
```gitignore
# === Large Data Files (regenerable via acquirer scripts) ===
# OSHA enforcement data (6.6 GB) - regenerate with osha_acquirer.py
data/modules/hse/raw/osha/*.csv
data/modules/hse/raw/osha/*.csv.zip

# BSEE raw data - regenerate with bsee_acquirer.py / dwnld_from_zipurl.py
data/modules/bsee/zip/
data/modules/bsee/bin/
data/modules/bsee/csv/online_query_raw_data/

# EPA TRI data - regenerate with epa_tri_acquirer.py
data/modules/hse/raw/epa_tri/*.csv

# Marine safety raw data
data/modules/marine_safety/raw/
data/modules/marine_safety/*.db
data/modules/marine_safety/database/

# Norwegian petroleum data
data/modules/sodir_zip_data/*.csv

# Binary data files
*.bin

# Database files (already partially covered)
*.db
*.db-journal
*.db-wal

# === Reference Documents (non-regenerable, archive externally) ===
docs/data_science/*.pdf
docs/modules/bsee/_legacy/
docs/modules/bsee/data/SME_Roy_attachments/
docs/raw_data/

# === Build/Analysis Outputs ===
results/modules/
htmlcov/
reports/marine_safety/*/*.html

# Large BSEE data files (>100MB GitHub limit)
data/modules/bsee/zip/directional_survey/
data/modules/bsee/zip/war/eWellWARRawData.zip
```

### Phase 2: Add README.md to Each .gitignored Data Directory

**Objective:** Ensure any developer can regenerate data after cloning.

Create `README.md` files in:
- `data/modules/hse/raw/osha/README.md` -- OSHA acquisition instructions
- `data/modules/bsee/zip/README.md` -- BSEE ZIP download instructions
- `data/modules/hse/raw/bsee/README.md` -- BSEE incident data instructions
- `data/modules/hse/raw/epa_tri/README.md` -- EPA TRI instructions
- `data/modules/marine_safety/raw/README.md` -- Marine safety scraper instructions
- `data/modules/sodir_zip_data/README.md` -- Norwegian data instructions
- `docs/data_science/README.md` -- Where to find reference PDFs (external link/drive)
- `docs/modules/bsee/_legacy/README.md` -- Legacy archive location
- `docs/modules/bsee/data/SME_Roy_attachments/README.md` -- SME data archive location

Each README should contain:
1. What data belongs in this directory
2. How to regenerate it (exact CLI command)
3. Expected size after regeneration
4. Source URL(s)
5. Last known successful acquisition date

### Phase 3: Remove Large Files from Working Tree (git rm --cached)

**Objective:** Untrack large files without deleting them from disk.

```bash
# Untrack OSHA data (6.6 GB)
git rm --cached -r data/modules/hse/raw/osha/*.csv
git rm --cached -r data/modules/hse/raw/osha/*.csv.zip

# Untrack BSEE ZIP data (488 MB)
git rm --cached -r data/modules/bsee/zip/

# Untrack BSEE binary data
git rm --cached -r data/modules/bsee/bin/

# Untrack BSEE CSV query results
git rm --cached -r data/modules/bsee/csv/online_query_raw_data/

# Untrack marine safety raw data (479 MB)
git rm --cached -r data/modules/marine_safety/raw/
git rm --cached data/modules/marine_safety/marine_safety.db
git rm --cached data/modules/marine_safety/database/marine_safety.db

# Untrack SODIR data (156 MB)
git rm --cached data/modules/sodir_zip_data/seaArea.csv
git rm --cached data/modules/sodir_zip_data/prlAreaSplitByBlock.csv
git rm --cached data/modules/sodir_zip_data/blkArea.csv

# Untrack large docs (437 + 723 + 302 + 150 MB)
git rm --cached -r docs/data_science/*.pdf
git rm --cached -r docs/modules/bsee/_legacy/
git rm --cached -r docs/modules/bsee/data/SME_Roy_attachments/
git rm --cached -r docs/raw_data/

# Untrack analysis results
git rm --cached -r results/modules/

# Untrack EPA TRI data
git rm --cached -r data/modules/hse/raw/epa_tri/*.csv

# De-duplicate: remove redundant copies
# (Already covered by the rm --cached above)

# Commit the untracking
git add .gitignore
git commit -m "chore: untrack large data files, fix .gitignore merge conflict

Untracked ~9 GB of regenerable data and reference documents.
Data can be regenerated using acquirer scripts in src/.
See README.md in each data directory for regeneration instructions."
```

**Estimated reduction in tracked content:** ~9.5 GB (but history still contains old blobs)

### Phase 4: Rewrite History with git-filter-repo

**Objective:** Remove all historical blobs of large data files, reducing .git/ from 6.8 GB to <500 MB.

#### 4.1 Install git-filter-repo
```bash
pip install git-filter-repo
# OR
uv tool install git-filter-repo
```

#### 4.2 Generate Analysis Report (dry run)
```bash
git filter-repo --analyze
# Review: .git/filter-repo/analysis/blob-shas-and-paths.txt
# Review: .git/filter-repo/analysis/path-all-sizes.txt
```

#### 4.3 Create path filter file
Create `filter-paths.txt` with paths to strip from history:
```
# Regenerable data
blob:data/modules/hse/raw/osha/
blob:data/modules/bsee/zip/
blob:data/modules/bsee/bin/
blob:data/modules/bsee/csv/online_query_raw_data/
blob:data/modules/bsee/archive/
blob:data/modules/marine_safety/raw/
blob:data/modules/marine_safety/marine_safety.db
blob:data/modules/marine_safety/database/
blob:data/modules/sodir_zip_data/
blob:data/modules/vessel_hull_models/
blob:data/modules/posters/
blob:data/modules/drilling_rigs/

# Reference documents
blob:docs/data_science/
blob:docs/modules/bsee/_legacy/
blob:docs/modules/bsee/data/SME_Roy_attachments/
blob:docs/raw_data/

# Analysis outputs
blob:results/modules/
blob:reports/marine_safety/

# Test output artifacts (HTML reports, large CSVs)
blob:tests/modules/bsee/analysis/comprehensive-report-system/results/
blob:tests/modules/bsee/analysis/results/
blob:tests/modules/bsee/data/results/
blob:tests/_archived/

# Agent-OS artifacts (deleted directory, still in history)
blob:.agent-os/

# Misc large files
blob:data/modules/lngc/103419-World_IGU_Report_no crops.pdf
blob:docs/modules/cement_as_barrier.pdf
blob:docs/project_management/EBOOK-10-Dysfunctions-of-Product-Management-V2.pdf
blob:.test_performance.db
blob:.swarm/
```

#### 4.4 Execute the rewrite
```bash
# IMPORTANT: Work on a fresh clone
git clone --no-local /path/to/worldenergydata worldenergydata-rewrite
cd worldenergydata-rewrite

# Run the filter
git filter-repo --invert-paths --paths-from-file filter-paths.txt

# Also strip any remaining blobs > 50MB not caught by path filtering
git filter-repo --strip-blobs-bigger-than 50M
```

**Note:** `git-filter-repo` will remove the `origin` remote as a safety measure. Re-add it after verifying results.

#### 4.5 Estimated Size Reduction

| Category                              | Before (history) | After (history) |
|---------------------------------------|-------------------|-----------------|
| data/modules/hse (OSHA + BSEE + EPA) | 6,751 MB          | 0 MB            |
| data/modules/bsee                     | 2,731 MB          | ~50 MB (configs)|
| tests/modules/bsee (large outputs)   | 1,099 MB          | ~20 MB          |
| data/modules/marine_safety            | 623 MB            | 0 MB            |
| docs/modules/bsee                     | 557 MB            | ~5 MB           |
| docs/data_science                     | 125 MB            | 0 MB            |
| data/modules/posters (deleted)        | 129 MB            | 0 MB            |
| data/modules/sodir_zip_data           | 120 MB            | 0 MB            |
| docs/raw_data                         | 89 MB             | 0 MB            |
| Other (results, agent-os, etc.)       | ~200 MB           | 0 MB            |
| Source code, configs, small files     | ~300 MB           | ~300 MB         |
| **TOTAL .git/ estimate**              | **6.8 GB**        | **~350-500 MB** |

### Phase 5: Configure LFS for Medium Files (10-100 MB) That Must Stay

**Objective:** Any files between 10-100 MB that genuinely need version control should use LFS.

#### 5.1 Install git-lfs
```bash
sudo apt-get install git-lfs  # or brew install git-lfs
git lfs install
```

#### 5.2 Update .gitattributes
Keep only the rules that are actually needed. The current `.gitattributes` references specific files that should instead be .gitignored. Proposed minimal `.gitattributes`:

```gitattributes
# LFS tracking for files that must be version-controlled but are large
# (Only use if specific large files genuinely need to be in the repo)
data/modules/bsee/archive/*.tar.gz filter=lfs diff=lfs merge=lfs -text
```

If no files between 10-100 MB need to remain in git, `.gitattributes` can be emptied or removed.

#### 5.3 Migrate existing tracked large files to LFS (if any remain)
```bash
git lfs migrate import --include="data/modules/bsee/archive/*.tar.gz" --everything
```

### Phase 6: Add Pre-Commit Hook to Block Large Files

**Objective:** Prevent future commits of files > 50 MB without LFS.

Create `.githooks/pre-commit` or use pre-commit framework:

```bash
#!/bin/bash
# Pre-commit hook: Block files larger than 50MB from being committed without LFS

MAX_SIZE=52428800  # 50 MB in bytes
BLOCKED=0

while read -r sha stage path; do
    if [ "$sha" = "0000000000000000000000000000000000000000" ]; then
        continue
    fi
    size=$(git cat-file -s "$sha" 2>/dev/null || echo 0)
    if [ "$size" -gt "$MAX_SIZE" ]; then
        echo "ERROR: $path is $(numfmt --to=iec $size), exceeds 50MB limit."
        echo "       Use git-lfs or add to .gitignore."
        BLOCKED=1
    fi
done < <(git diff --cached --diff-filter=d --format='')

# Check staged files
git diff --cached --name-status | while read status file; do
    if [ "$status" != "D" ] && [ -f "$file" ]; then
        size=$(stat -c%s "$file" 2>/dev/null || echo 0)
        if [ "$size" -gt "$MAX_SIZE" ]; then
            echo "ERROR: $file is $(numfmt --to=iec $size), exceeds 50MB limit."
            echo "       Use git-lfs or add to .gitignore."
            BLOCKED=1
        fi
    fi
done

exit $BLOCKED
```

Configure git to use it:
```bash
git config core.hooksPath .githooks
```

### Phase 7: Force Push and Notify Collaborators

**Objective:** Replace the remote history with the cleaned version.

```bash
# Re-add origin
git remote add origin https://github.com/vamseeachanta/worldenergydata.git

# Verify the cleanup
du -sh .git/
git log --oneline | wc -l  # Should still be ~601 commits

# Force push ALL branches
git push origin --force --all
git push origin --force --tags

# Clean up reflogs on the server (GitHub does this automatically after GC)
```

Post-push communication to all collaborators:
```
Subject: worldenergydata repository history rewritten -- please re-clone

The worldenergydata repository history has been rewritten to remove
large data files (~12 GB of historical blobs).

REQUIRED ACTION: Delete your local clone and re-clone:
    rm -rf worldenergydata
    git clone https://github.com/vamseeachanta/worldenergydata.git
    cd worldenergydata
    # Run acquirer scripts to regenerate data (see README.md in each data dir)

DO NOT attempt to pull or merge with your old clone -- the histories
are incompatible and will cause massive merge conflicts.
```

---

## 5. Risk Assessment

### 5.1 Impact on Forks/Clones

| Risk                                      | Severity | Mitigation                                    |
|-------------------------------------------|----------|-----------------------------------------------|
| Existing clones become incompatible       | HIGH     | All collaborators must re-clone                |
| Open PRs will be invalidated              | HIGH     | Merge/close all PRs before rewrite             |
| GitHub forks will have divergent history  | MEDIUM   | Notify fork owners; they must reset to upstream |
| CI/CD pipelines referencing commit SHAs   | LOW      | Update any pinned SHA references               |
| GitHub Issues referencing commits         | LOW      | Old SHA links will break (cosmetic)            |

### 5.2 Data Loss Risks

| Risk                                      | Severity | Mitigation                                       |
|-------------------------------------------|----------|--------------------------------------------------|
| Non-regenerable docs permanently lost     | HIGH     | Archive to external storage BEFORE cleanup        |
| Acquirer scripts fail (API changes, etc.) | MEDIUM   | Test ALL acquirer scripts before rewriting history |
| LFS migration corrupts files              | LOW      | Verify file checksums before and after            |
| git-filter-repo removes too much          | LOW      | Dry-run with `--analyze`; work on a clone         |

### 5.3 Rollback Strategy

1. **Before rewrite:** Mirror backup exists at `backup-worldenergydata-YYYYMMDD.git`
2. **If rewrite goes wrong locally:** Delete rewrite clone, start from backup
3. **If force push goes wrong on GitHub:**
   ```bash
   cd backup-worldenergydata-YYYYMMDD.git
   git push --mirror https://github.com/vamseeachanta/worldenergydata.git
   ```
4. **Point of no return:** After GitHub runs GC (~2 weeks after force push), old objects are permanently deleted. Ensure the mirror backup is retained for at least 30 days.

---

## 6. Verification Checklist

### 6.1 Size Targets

| Metric                  | Current   | Target    | Pass Criteria        |
|-------------------------|-----------|-----------|----------------------|
| `.git/` directory       | 6.8 GB    | < 500 MB  | `du -sh .git/ < 500M` |
| Working tree (no data)  | 19 GB     | < 500 MB  | Code + configs only   |
| Pack files              | 4.4 GB    | < 400 MB  | After `git gc`        |
| Loose objects           | 2.3 GB    | < 50 MB   | After `git gc`        |

### 6.2 Functional Verification

- [ ] `git clone` completes in < 60 seconds on broadband
- [ ] All tests pass: `uv run pytest`
- [ ] Source code is intact (no files accidentally removed from history)
- [ ] `.gitignore` has no merge conflict markers
- [ ] `.gitattributes` references only files that actually exist and use LFS
- [ ] All acquirer scripts successfully regenerate their datasets:
  - [ ] `uv run python -m worldenergydata.modules.hse.acquirers.osha_acquirer --output-dir data/modules/hse/raw/osha`
  - [ ] `uv run python -m worldenergydata.modules.hse.acquirers.bsee_acquirer --output-dir data/modules/hse/raw/bsee`
  - [ ] `uv run python -m worldenergydata.modules.hse.acquirers.epa_tri_acquirer --output-dir data/modules/hse/raw/epa_tri`
- [ ] Pre-commit hook blocks files > 50 MB
- [ ] LFS tracking works for any remaining large files
- [ ] `git lfs ls-files` lists only intentionally tracked files (or is empty)

### 6.3 History Verification

- [ ] `git log --oneline | wc -l` returns ~601 (commit count preserved)
- [ ] `git log --all --oneline -- src/` shows all source code commits intact
- [ ] `git log --all --oneline -- tests/` shows test commits intact (minus large artifacts)
- [ ] No orphaned references: `git fsck --no-reflogs`

---

## 7. Timeline Estimate

| Phase | Description                            | Effort    | Dependencies                    |
|-------|----------------------------------------|-----------|---------------------------------|
| 1     | Fix .gitignore                         | 30 min    | None                            |
| 2     | Add README.md to data directories      | 2 hours   | Phase 1                         |
| 3     | git rm --cached large files            | 1 hour    | Phase 1 + 2                     |
| 4     | git-filter-repo history rewrite        | 2-4 hours | Phase 3 + all acquirer tests    |
| 5     | Configure LFS                          | 1 hour    | Phase 4                         |
| 6     | Pre-commit hook                        | 30 min    | Phase 4                         |
| 7     | Force push + notify                    | 30 min    | Phase 4 + 5 + 6                |
| --    | **Total**                              | **7-9 hours** | Plus acquirer testing time  |

**Recommended sequencing:** Phases 1-3 can be done immediately as a normal commit. Phase 4 (the destructive rewrite) should be scheduled with advance notice to all collaborators.

---

## 8. Long-Term Maintenance Recommendations

1. **Data Catalog:** Maintain a `data/catalog/` manifest that lists all expected data files, their sizes, source URLs, and regeneration commands -- without storing the data itself in git.

2. **CI Size Gate:** Add a GitHub Actions check that fails if `.git/` exceeds 1 GB or any single file exceeds 50 MB.

3. **Periodic Audit:** Run `git rev-list --objects --all | git cat-file --batch-check | sort -k3 -rn | head -20` quarterly to catch size creep early.

4. **External Storage for Non-Regenerable Docs:** Large reference PDFs, SME-provided data, and legacy documents should be stored in:
   - A shared cloud drive (Google Drive, OneDrive, S3)
   - A git-annex or DVC-tracked external store
   - NOT in the git repository

5. **Acquirer CI:** Add scheduled CI jobs that verify acquirer scripts can still download data (monthly). API endpoints change; catching failures early prevents data loss.
