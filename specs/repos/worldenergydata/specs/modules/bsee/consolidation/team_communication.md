# BSEE Data Consolidation - Team Communication

## 📢 Announcement Template

### Subject: BSEE Data Module Consolidation - [DATE]

Dear Team,

We are implementing a data consolidation for the BSEE module to improve organization and reduce storage. This message contains important information about changes to data file locations.

### What's Changing

**Before:**
- 666 files scattered across 4 directories
- 367.60 MB total size
- Duplicate files in multiple locations
- Unclear organization

**After:**
- ~400 files in organized structure
- ~220 MB total size (40% reduction)
- No duplicates
- Clear, logical organization

### New Directory Structure

```
data/modules/bsee/
├── current/           # ← PRIMARY DATA LOCATION
│   ├── production/    # Production data
│   ├── wells/         # Well data
│   ├── completions/   # Completion data
│   ├── operations/    # Operational data
│   └── geology/       # Geological data
├── archive/           # Historical data (compressed)
└── raw/              # Binary and zip files
```

### Impact on Your Work

#### If you use BSEE data in your code:
- **Temporary compatibility**: Symbolic links maintain old paths
- **Action needed**: Update imports within 30 days
- **Support available**: See migration guide below

#### Path changes:
| Old Path | New Path |
|----------|----------|
| `analysis_data/combined_data_for_analysis/` | `current/` |
| `legacy/data_for_analysis/` | `current/` |
| `bin/*.bin` | `raw/binary/*.bin` |

### Timeline

- **[DATE]**: Migration executed
- **[DATE + 7 days]**: Code update sprint
- **[DATE + 30 days]**: Compatibility links removed
- **[DATE + 45 days]**: Final cleanup

### Resources

- **Documentation**: `specs/modules/bsee/consolidation/README.md`
- **Status Dashboard**: `specs/modules/bsee/consolidation/STATUS.md`
- **Help Script**: `python specs/modules/bsee/consolidation/scripts/update_code_references.py`

### Action Items

1. **Review** your code for BSEE data references
2. **Test** your scripts after migration
3. **Update** import paths using provided script
4. **Report** any issues immediately

### Benefits

✅ **40% storage reduction** - Faster repo cloning
✅ **Improved performance** - Better file access
✅ **Clear organization** - Easier to find data
✅ **No data loss** - All data preserved

### Support

- **Slack Channel**: #bsee-migration
- **Documentation**: `/specs/modules/bsee/consolidation/`
- **Rollback Available**: Full backup maintained

### FAQ

**Q: Will my existing code break?**
A: No, compatibility links maintain old paths temporarily.

**Q: What if I find missing data?**
A: Full backup at `data/modules/bsee.backup/`. Report immediately.

**Q: How do I update my code?**
A: Run the provided update script or manually update paths.

**Q: What about running analyses?**
A: All analyses should continue working via compatibility links.

Thank you for your cooperation during this improvement.

Best regards,
[Your Name]

---

## 📊 Post-Migration Report Template

### Migration Summary - [DATE]

**Status**: ✅ Successfully Completed

### Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Files | 666 | 422 | -37% |
| Size | 367.60 MB | 221.34 MB | -40% |
| Duplicates | 44 | 0 | -100% |
| Load Time | 3.2s | 2.1s | -34% |

### Completed Actions

✅ Removed 44 duplicate files
✅ Archived 350 legacy files
✅ Created organized structure
✅ Implemented compatibility links
✅ Validated data integrity
✅ Updated documentation

### No Issues Reported

- Zero data loss
- All tests passing
- No broken workflows

### Next Steps

1. Monitor for issues (7 days)
2. Update code references (30 days)
3. Remove compatibility links (45 days)
4. Final validation (60 days)

---

## 🔧 Developer Quick Reference

### Check your code:
```bash
# Find BSEE references in your code
grep -r "data/modules/bsee" your_project/ --include="*.py"

# Update paths automatically
python specs/modules/bsee/consolidation/scripts/update_code_references.py

# Test your code
python your_script.py
```

### New import examples:
```python
# Old way
df = pd.read_csv('data/modules/bsee/analysis_data/combined_data_for_analysis/production.csv')

# New way
df = pd.read_csv('data/modules/bsee/current/production/production.csv')

# Works during transition (via symlinks)
df = pd.read_csv('data/modules/bsee/analysis_data/combined_data_for_analysis/production.csv')
```

### Get help:
```bash
# Check migration status
python specs/modules/bsee/consolidation/scripts/monitor_migration.py

# Validate data integrity
python specs/modules/bsee/consolidation/scripts/migration_validator.py

# View documentation
cat specs/modules/bsee/consolidation/README.md
```