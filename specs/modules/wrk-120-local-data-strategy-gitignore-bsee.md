# WRK-120: Local Data Strategy — Gitignore BSEE Bins, Keep Repo Lean

## Context

After WRK-098 cleaned git history (4.1 GB → 177 MB) and the parallel refresh script regenerated all 135 `.bin` files (2.1 GB) locally, these binary files must be excluded from git tracking. The Data Residence Policy (`docs/DATA_RESIDENCE_POLICY.md`) already mandates >100 MB datasets use `.gitignore` + pipeline regeneration. Currently **133 .bin files are tracked by git** (all real data, no stubs). Five additional .bin files exist untracked.

## Approach

Single-phase execution: update `.gitignore`, untrack files, add `.gitkeep` placeholders, fix 2 loaders, add Makefile target, document the pattern.

## Files to Modify

| File | Action | Purpose |
|------|--------|---------|
| `.gitignore` | Edit | Add `data/modules/bsee/bin/**/*.bin`, clean up 13 obsolete paths |
| `Makefile` | Edit | Add `data` target to run refresh script |
| `src/worldenergydata/bsee/data/loaders/block/war_data.py` | Edit | Add try/except + actionable error message |
| `src/worldenergydata/bsee/data/apm_data.py` | Edit | Add try/except + actionable error message |
| `docs/data/LOCAL_DATA_PATTERN.md` | New ~80 lines | Document the local-data-only pattern |
| 30x `data/modules/bsee/bin/<dir>/.gitkeep` | New (empty) | Preserve directory structure in git |

## Step 1: Update .gitignore

Replace the 13 obsolete individual BSEE bin directory entries (lines 165-177) with one blanket pattern:

```gitignore
# BSEE binary data — regenerate via: python3 scripts/refresh_bsee_all.py
data/modules/bsee/bin/**/*.bin
```

The 13 old paths (`data/modules/bsee/bin/production/`, `bin/war/`, `bin/api/`, etc.) no longer exist post-WRK-096 flatten. Remove them.

## Step 2: Untrack .bin files from git index

```bash
git rm --cached data/modules/bsee/bin/**/*.bin
# Expected: 133 files removed from index
# Verify: git ls-files '*.bin' returns empty
```

The files remain on disk (local analysis continues to work), they're just no longer tracked.

## Step 3: Add .gitkeep to 30 bin subdirectories

Create empty `.gitkeep` in each of the 30 directories so `git clone` preserves the directory structure:

```
apichanges, apiraw, approvals, assignments, companydetails, decomcost,
deepqual, dsptsdelimit, fmp, historical_production_yearly, incinv, incs,
lab, leaseowner, mcpflow, nonrequired, ocsprod, offshorestats, osfr,
permstruc, pipeloc, platstruc, production_plan_area, production_raw,
rig_fleet, rowdesc, royaltyref, scanneddocs, serialreg, Well_APD_Default
```

## Step 4: Fix 2 loaders for graceful degradation

**6 of 8 loaders already handle missing files gracefully** (try/except → empty DataFrame). Two need fixing:

### `war_data.py` (~line 59)
Current: `df = pd.read_pickle(filepath)` — crashes if file missing.
Fix: Wrap in try/except, return empty DataFrame with warning:
```python
try:
    df = pd.read_pickle(filepath)
except (FileNotFoundError, OSError) as e:
    logger.warning(f"BSEE data not found: {filepath}. "
                   "Run: python3 scripts/refresh_bsee_all.py")
    return pd.DataFrame()
```

### `apm_data.py` (~lines 16-32)
Current: `os.listdir(folder_path_bin)` + `pickle.load()` — crashes if directory empty/missing.
Fix: Check directory exists and has files, wrap pickle.load in try/except:
```python
if not os.path.isdir(folder_path_bin) or not os.listdir(folder_path_bin):
    logger.warning(f"BSEE data not found: {folder_path_bin}. "
                   "Run: python3 scripts/refresh_bsee_all.py")
    return pd.DataFrame()
```

## Step 5: Add Makefile `data` target

Add to existing `Makefile`:
```makefile
.PHONY: data
data:  ## Download BSEE datasets (~300 MB, ~8 min)
	python3 scripts/refresh_bsee_all.py

data-dry:  ## Show what data would be downloaded
	python3 scripts/refresh_bsee_all.py --dry-run
```

## Step 6: Document pattern

Create `docs/data/LOCAL_DATA_PATTERN.md` (~80 lines):
- Problem: binary data too large for git, freely re-downloadable
- Pattern: gitignore + refresh script + graceful loader degradation
- How to populate: `make data` or `python3 scripts/refresh_bsee_all.py`
- How to verify: `python3 scripts/refresh_bsee_all.py --dry-run`
- When to apply: any module where source data >100 MB and is publicly re-downloadable
- Reference: Data Residence Policy Tier 1

## Verification

```bash
# 1. No .bin files tracked
git ls-files '*.bin' | wc -l
# Expected: 0

# 2. All 30 directories have .gitkeep
find data/modules/bsee/bin -name .gitkeep | wc -l
# Expected: 30

# 3. Local data still works (files still on disk)
python3 -c "import pickle; pickle.load(open('data/modules/bsee/bin/apichanges/mv_apichanges_all.bin','rb'))"
# Expected: no error

# 4. Dry run works
python3 scripts/refresh_bsee_all.py --dry-run
# Expected: shows all dirs as "already real data"

# 5. Tests still pass
PYTHONPATH="src:../assetutilities/src" python3 -m pytest tests/unit/bsee/test_url_registry.py tests/unit/bsee/test_refresh_bsee.py -v --tb=short --noconftest

# 6. Makefile target works
make data-dry
```

## Step 7: Fresh Clone / New Machine Setup Guide

Add a section to `docs/data/LOCAL_DATA_PATTERN.md` and update `README.md` with a clear "Getting Started with Data" workflow for someone cloning the repo on a new machine:

```markdown
## First-Time Setup (New Clone / New Machine)

1. Clone the repository:
   git clone https://github.com/vamseeachanta/worldenergydata.git
   cd worldenergydata

2. Install dependencies:
   pip install pandas requests

3. Populate BSEE data (~300 MB download, ~8 minutes):
   make data
   # or: python3 scripts/refresh_bsee_all.py

4. Verify data is available:
   make data-dry
   # Should show all directories as "already real data"

5. (Optional) Refresh a single dataset:
   python3 scripts/refresh_bsee_all.py --dir platstruc
```

Also update `README.md` Quick Start section to include `make data` as step 2 after install, with a note that BSEE analysis modules require local data that is not stored in git.

## Estimated Scope

- `.gitignore`: ~5 lines changed
- `.gitkeep` files: 30 empty files
- `war_data.py`: ~8 lines added
- `apm_data.py`: ~8 lines added
- `Makefile`: ~6 lines added
- `LOCAL_DATA_PATTERN.md`: ~80 lines new
- `git rm --cached`: 133 files untracked
- **Total new code: ~110 lines**
