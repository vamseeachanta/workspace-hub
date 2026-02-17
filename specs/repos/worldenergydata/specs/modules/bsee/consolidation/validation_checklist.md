# BSEE Data Consolidation - Validation Checklist

## Pre-Migration Checklist

### 1. Backup Verification
- [ ] Full backup created at `data/modules/bsee.backup/`
- [ ] Backup size matches original (367.60 MB)
- [ ] Backup file count matches (666 files)
- [ ] Test restore from backup works

### 2. Approval Confirmation
- [ ] Cleanup proposal reviewed
- [ ] Approval JSON file created
- [ ] Approval status set to "APPROVED"
- [ ] Excluded files list reviewed

### 3. Code Impact Assessment
- [ ] All Python files using BSEE data identified
- [ ] Test suite ready to run
- [ ] Compatibility link script ready

## Migration Execution Checklist

### 4. Dry Run Validation
- [ ] Dry run completed successfully
- [ ] Operations log reviewed
- [ ] No unexpected deletions
- [ ] File counts match expected

### 5. Actual Migration
- [ ] Migration executor run with `--execute`
- [ ] All operations completed without errors
- [ ] Rollback script generated
- [ ] Operation log saved

### 6. File Structure Validation
- [ ] New directory structure created:
  - [ ] `current/production/`
  - [ ] `current/wells/`
  - [ ] `current/completions/`
  - [ ] `current/operations/`
  - [ ] `current/geology/`
  - [ ] `current/reference/`
  - [ ] `archive/`
  - [ ] `raw/binary/`
  - [ ] `raw/compressed/`

## Post-Migration Validation

### 7. Data Integrity Checks
- [ ] All moved files have matching checksums
- [ ] Row counts preserved in CSV files
- [ ] No data corruption detected
- [ ] File sizes match expected

### 8. Duplicate Removal Verification
- [ ] 44 duplicate files removed
- [ ] No unique data lost
- [ ] Space savings achieved (28.45 MB)

### 9. Archive Validation
- [ ] Legacy directory archived successfully
- [ ] Archive is extractable
- [ ] Archive size as expected

### 10. Compatibility Testing
- [ ] Symbolic links created
- [ ] Old paths still accessible
- [ ] Existing code runs without errors

## Code Testing

### 11. Import Path Testing
Run these test imports:
```python
# Test that critical data files are accessible
import pandas as pd

# Original paths (via symlinks)
df1 = pd.read_csv('data/modules/bsee/analysis_data/combined_data_for_analysis/production.csv')
df2 = pd.read_csv('data/modules/bsee/analysis_data/combined_data_for_analysis/well_data.csv')

# New paths
df3 = pd.read_csv('data/modules/bsee/current/production/production.csv')
df4 = pd.read_csv('data/modules/bsee/current/wells/well_data.csv')

# Verify data matches
assert len(df1) == len(df3)
assert len(df2) == len(df4)
print("✅ Path compatibility verified")
```

### 12. Module Testing
- [ ] Run BSEE module unit tests
- [ ] Run integration tests
- [ ] Verify no import errors
- [ ] Check data loading functions

## Performance Validation

### 13. Performance Metrics
- [ ] Directory traversal faster
- [ ] File access times improved
- [ ] Repository size reduced
- [ ] Clone time decreased

### 14. Space Savings
| Metric | Before | After | Target | Achieved |
|--------|--------|-------|--------|----------|
| Total Files | 666 | ? | ~400 | [ ] |
| Total Size | 367.60 MB | ? | ~220 MB | [ ] |
| Duplicates | 44 | ? | 0 | [ ] |

## Documentation Updates

### 15. Documentation Tasks
- [ ] Update README.md with new structure
- [ ] Document data catalog
- [ ] Update import examples
- [ ] Create migration notes

### 16. Communication
- [ ] Notify team of changes
- [ ] Share new data paths
- [ ] Provide transition guide
- [ ] Schedule code update session

## Rollback Readiness

### 17. Rollback Preparation
- [ ] Rollback script tested
- [ ] Backup verified accessible
- [ ] Restore procedure documented
- [ ] Team knows rollback process

## Sign-Off

### 18. Final Approval
- [ ] All validation checks passed
- [ ] No data loss confirmed
- [ ] Performance improvements verified
- [ ] Team satisfied with new structure

**Migration Status**: ⏸️ PENDING APPROVAL

**Validated By**: _________________
**Date**: _________________
**Notes**: 
```
[Add any validation notes here]
```

---

## Quick Commands Reference

```bash
# Run inventory
python specs/modules/bsee/consolidation/scripts/inventory_generator.py

# Run duplicate analysis
python specs/modules/bsee/consolidation/scripts/duplicate_detector.py

# Dry run migration
python specs/modules/bsee/consolidation/scripts/migration_executor.py

# Execute migration (after approval)
python specs/modules/bsee/consolidation/scripts/migration_executor.py --execute

# Create compatibility links
python specs/modules/bsee/consolidation/scripts/create_compatibility_links.py

# Validate migration
python specs/modules/bsee/consolidation/scripts/migration_validator.py

# Rollback if needed
python specs/modules/bsee/consolidation/rollback.py
```