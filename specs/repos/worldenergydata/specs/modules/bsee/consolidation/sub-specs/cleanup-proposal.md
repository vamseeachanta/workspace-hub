# BSEE Data Cleanup Proposal

> **IMPORTANT**: This document requires user approval before any deletions or moves

## Executive Summary

Based on the inventory and duplicate analysis, we propose the following cleanup actions for the BSEE data module:

- **Files to Delete**: [TO BE FILLED AFTER ANALYSIS]
- **Files to Archive**: [TO BE FILLED AFTER ANALYSIS]  
- **Files to Move/Rename**: [TO BE FILLED AFTER ANALYSIS]
- **Expected Space Savings**: [TO BE FILLED] MB

## Proposed Actions

### 1. Delete Exact Duplicates

**Approval Required**: ☐ Yes ☐ No

These files are exact duplicates (identical checksum) and can be safely removed:

| File to Delete | Keep Original At | Size (MB) | Reason |
|---------------|------------------|-----------|---------|
| [TO BE FILLED FROM ANALYSIS] | | | Exact duplicate |

### 2. Archive Legacy Data

**Approval Required**: ☐ Yes ☐ No

Move these legacy files to compressed archive:

| File to Archive | Archive Location | Size (MB) | Last Modified |
|-----------------|------------------|-----------|---------------|
| legacy/[file] | archive/2025-08-21-legacy.tar.gz | | |

### 3. Consolidate Redundant Data

**Approval Required**: ☐ Yes ☐ No

Merge these similar files into single authoritative source:

| Files to Merge | Target File | Combined Size | Data Loss Risk |
|----------------|-------------|---------------|----------------|
| production files | current/production/master_production.csv | | None - all data preserved |

### 4. Reorganize File Structure

**Approval Required**: ☐ Yes ☐ No

Move files to new organized structure:

| Current Location | New Location | Reason |
|-----------------|--------------|---------|
| analysis_data/combined_data_for_analysis/*.csv | current/[type]/*.csv | Better organization |

## Risk Assessment

### Low Risk Actions (Recommended)
- Removing exact duplicates (identical checksums)
- Archiving legacy data (keeping compressed copy)
- Renaming files for consistency

### Medium Risk Actions (Review Carefully)
- Consolidating similar files
- Moving files to new structure
- Converting formats

### High Risk Actions (Not Recommended)
- Deleting unique data
- Removing files without backup
- Changing data content

## Validation Strategy

Before executing changes:
1. Create full backup in `data/modules/bsee.backup/`
2. Generate checksums for all files
3. Create rollback script

After executing changes:
1. Verify file counts match expected
2. Validate checksums for moved files
3. Run all existing tests
4. Check data loading in code

## Approval Checklist

Please review and approve each action category:

- [ ] **Exact Duplicate Deletion**: I approve removing exact duplicate files
- [ ] **Legacy Data Archival**: I approve archiving legacy directory
- [ ] **Data Consolidation**: I approve merging redundant files
- [ ] **Structure Reorganization**: I approve the new directory structure
- [ ] **Backup Created**: Confirm backup exists before proceeding

## User Decision

**Overall Approval**: ☐ APPROVED ☐ REJECTED ☐ PARTIAL (specify below)

**Comments/Modifications**:
```
[User comments here]
```

**Specific Exclusions** (files NOT to touch):
```
[List any files that should not be modified]
```

---

*Sign-off*

Date: _______________
Approved by: _______________