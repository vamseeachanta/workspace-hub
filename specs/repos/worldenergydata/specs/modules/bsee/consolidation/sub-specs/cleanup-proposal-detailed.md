# BSEE Data Cleanup Proposal - Detailed

> **IMPORTANT**: This document requires user approval before any deletions or moves
> Generated: 2025-08-21
> Based on analysis of 666 files totaling 367.60 MB

## Executive Summary

Based on the inventory and duplicate analysis completed, we propose the following cleanup actions:

- **Files to Delete**: 44 exact duplicates from legacy/
- **Files to Archive**: 350 legacy files (after duplicate removal)
- **Files to Move/Rename**: 16 files from analysis_data/ to current/
- **Expected Space Savings**: 28.45 MB immediate + ~150 MB after archival

## Proposed Actions

### 1. Delete Exact Duplicates

**Approval Required**: ☐ Yes ☐ No

These files are exact duplicates (identical checksum) and can be safely removed:

| File to Delete | Keep Original At | Size (MB) | Reason |
|---------------|------------------|-----------|---------|
| legacy/data_for_analysis/all_bsee_blocks.csv | analysis_data/combined_data_for_analysis/all_bsee_blocks.csv | 0.00 | Exact duplicate |
| legacy/data_for_analysis/completion_perforations.csv | analysis_data/combined_data_for_analysis/completion_perforations.csv | 0.00 | Exact duplicate |
| legacy/data_for_analysis/completion_properties.csv | analysis_data/combined_data_for_analysis/completion_properties.csv | 0.01 | Exact duplicate |
| legacy/data_for_analysis/completion_summary.csv | analysis_data/combined_data_for_analysis/completion_summary.csv | 0.00 | Exact duplicate |
| legacy/data_for_analysis/cut_casings.csv | analysis_data/combined_data_for_analysis/cut_casings.csv | 0.00 | Exact duplicate |
| legacy/data_for_analysis/geology_markers.csv | analysis_data/combined_data_for_analysis/geology_markers.csv | 0.00 | Exact duplicate |
| legacy/data_for_analysis/hydrocarbon_bearing_interval.csv | analysis_data/combined_data_for_analysis/hydrocarbon_bearing_interval.csv | 0.01 | Exact duplicate |
| legacy/data_for_analysis/production.csv | analysis_data/combined_data_for_analysis/production.csv | 0.00 | Exact duplicate |
| legacy/data_for_analysis/ST_BP_and_tree_height.csv | analysis_data/combined_data_for_analysis/ST_BP_and_tree_height.csv | 0.00 | Exact duplicate |
| legacy/data_for_analysis/well_activity_bop_tests.csv | analysis_data/combined_data_for_analysis/well_activity_bop_tests.csv | 0.00 | Exact duplicate |
| legacy/data_for_analysis/well_activity_open_hole.csv | analysis_data/combined_data_for_analysis/well_activity_open_hole.csv | 0.00 | Exact duplicate |
| legacy/data_for_analysis/well_activity_remarks.csv | analysis_data/combined_data_for_analysis/well_activity_remarks.csv | 0.00 | Exact duplicate |
| legacy/data_for_analysis/well_activity_summary.csv | analysis_data/combined_data_for_analysis/well_activity_summary.csv | 0.00 | Exact duplicate |
| legacy/data_for_analysis/well_data.csv | analysis_data/combined_data_for_analysis/well_data.csv | 3.27 | Exact duplicate |
| legacy/data_for_analysis/well_directional_surveys.csv | analysis_data/combined_data_for_analysis/well_directional_surveys.csv | 15.48 | Exact duplicate |
| legacy/data_for_analysis/well_tubulars.csv | analysis_data/combined_data_for_analysis/well_tubulars.csv | 0.00 | Exact duplicate |

**Plus 28 more duplicate files in legacy/online_raw_well_data/ directory**

Total duplicates to delete: **44 files**
Total space saved: **28.45 MB**

### 2. Archive Legacy Data

**Approval Required**: ☐ Yes ☐ No

Move these legacy files to compressed archive:

| Directory | Files | Size (MB) | Archive Location |
|-----------|-------|-----------|------------------|
| legacy/ (entire directory) | 350 files (after duplicates removed) | ~120 MB | archive/2025-08-21-legacy.tar.gz |

Compression expected to reduce 120 MB to ~40 MB archived.

### 3. Consolidate and Reorganize

**Approval Required**: ☐ Yes ☐ No

Move files to new organized structure:

| Current Location | New Location | Reason |
|-----------------|--------------|---------|
| analysis_data/combined_data_for_analysis/*.csv | current/master/*.csv | Establish as authoritative source |
| bin/*.bin | raw/binary/*.bin | Separate raw binary data |
| zip/*.zip | raw/compressed/*.zip | Organize compressed archives |

### 4. Create New Directory Structure

**Approval Required**: ☐ Yes ☐ No

```
data/modules/bsee/
├── current/                    # Latest authoritative data
│   ├── production/            # Production-related data
│   │   └── production.csv
│   ├── wells/                 # Well-related data
│   │   ├── well_data.csv
│   │   └── well_directional_surveys.csv
│   ├── completions/           # Completion data
│   │   ├── completion_perforations.csv
│   │   ├── completion_properties.csv
│   │   └── completion_summary.csv
│   ├── operations/            # Operational data
│   │   ├── well_activity_bop_tests.csv
│   │   ├── well_activity_open_hole.csv
│   │   ├── well_activity_remarks.csv
│   │   └── well_activity_summary.csv
│   └── geology/               # Geological data
│       ├── geology_markers.csv
│       └── hydrocarbon_bearing_interval.csv
├── archive/                   # Historical/legacy data (compressed)
│   └── 2025-08-21-legacy.tar.gz
├── raw/                       # Original format data
│   ├── binary/               # Git LFS tracked .bin files
│   └── compressed/           # Original .zip files
└── README.md                 # Data catalog and documentation
```

## Risk Assessment

### Low Risk Actions (Recommended)
✅ Removing exact duplicates (identical checksums)
✅ Archiving legacy data (keeping compressed copy)
✅ Creating new directory structure

### Medium Risk Actions (Review Carefully)
⚠️ Moving files to new locations (update code references)
⚠️ Consolidating similar files

### High Risk Actions (Not Recommended)
❌ No high-risk actions proposed

## Validation Strategy

Before executing changes:
1. ✅ Create full backup in `data/modules/bsee.backup/`
2. ✅ Generate checksums for all files
3. ✅ Create rollback script

After executing changes:
1. ✅ Verify file counts match expected
2. ✅ Validate checksums for moved files
3. ✅ Run all existing tests
4. ✅ Check data loading in code

## Code Impact Analysis

Files that may need path updates in code:
- `src/worldenergydata/modules/bsee/analysis/production_api12.py`
- Any scripts referencing `analysis_data/combined_data_for_analysis/`
- Any scripts referencing `legacy/` directory

Recommended: Create symbolic links during transition period.

## Approval Checklist

Please review and approve each action category:

- [ ] **Exact Duplicate Deletion**: I approve removing 44 duplicate files
- [ ] **Legacy Data Archival**: I approve archiving the legacy directory
- [ ] **Structure Reorganization**: I approve the new directory structure
- [ ] **File Movements**: I approve moving files to new locations
- [ ] **Backup Created**: Confirm backup should be created before proceeding

## Specific Files NOT to Touch

If there are any files that should be preserved exactly as-is, please list them:
```
[User to specify any files to exclude]
```

## User Decision

**Overall Approval**: ☐ APPROVED ☐ REJECTED ☐ PARTIAL (specify below)

**Comments/Modifications**:
```
[User comments here]
```

---

## Summary Statistics

| Metric | Current | After Cleanup | Improvement |
|--------|---------|---------------|-------------|
| Total Files | 666 | ~240 | 64% reduction |
| Total Size | 367.60 MB | ~180 MB | 51% reduction |
| Duplicate Files | 44 | 0 | 100% cleaned |
| Directory Depth | 4 levels | 3 levels | Simplified |
| Organization | Scattered | Categorized | Clear structure |

## Next Steps After Approval

1. **Backup Creation** - Full backup of current structure
2. **Dry Run** - Test all operations without changes
3. **Execute Migration** - Perform approved changes
4. **Validation** - Verify data integrity
5. **Documentation Update** - Update README with new structure
6. **Code Updates** - Update any broken references

---

*This proposal is based on automated analysis. Please review carefully before approval.*