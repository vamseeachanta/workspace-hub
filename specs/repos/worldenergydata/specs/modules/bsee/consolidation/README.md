# BSEE Data Consolidation Project

## Overview

This specification implements a comprehensive consolidation and cleanup of the BSEE (Bureau of Safety and Environmental Enforcement) data module, which currently contains 666 files totaling 369MB across multiple directories with significant duplication and redundancy.

## Quick Start

### 1. Generate Inventory (5 minutes)
```bash
cd /mnt/github/github/worldenergydata
python specs/modules/bsee/consolidation/scripts/inventory_generator.py
```
This creates:
- `sub-specs/inventory.json` - Complete file inventory
- `sub-specs/data-inventory.md` - Human-readable summary

### 2. Analyze Duplicates (2 minutes)
```bash
python specs/modules/bsee/consolidation/scripts/duplicate_detector.py
```
This creates:
- `sub-specs/duplicate-analysis.md` - Duplicate report
- `sub-specs/duplicate-analysis.json` - Detailed findings

### 3. Review & Approve Changes
1. Review the reports in `sub-specs/`
2. Edit `sub-specs/cleanup-proposal.md` with your decisions
3. Create `sub-specs/cleanup-proposal-approved.json` with approved changes

### 4. Execute Migration (Dry Run First)
```bash
# Dry run - see what would change
python specs/modules/bsee/consolidation/scripts/migration_executor.py

# Execute for real (after review)
python specs/modules/bsee/consolidation/scripts/migration_executor.py --execute
```

### 5. Validate Results
```bash
python specs/modules/bsee/consolidation/scripts/migration_validator.py
```

## Project Structure

```
specs/modules/bsee/consolidation/
├── README.md                    # This file
├── spec.md                      # Main specification
├── tasks.md                     # Task breakdown (8 tasks, 48 subtasks)
├── scripts/                     # Automation scripts
│   ├── inventory_generator.py   # Creates file inventory
│   ├── duplicate_detector.py    # Finds duplicates
│   ├── migration_executor.py    # Executes changes
│   └── migration_validator.py   # Validates migration
└── sub-specs/                   # Detailed specifications
    ├── technical-spec.md        # Technical approach
    ├── cleanup-proposal.md      # User approval template
    └── [Generated Files]        # Created by scripts
```

## Expected Outcomes

### Before Consolidation
- **Files**: 666 files
- **Size**: 369 MB
- **Structure**: Scattered across 4 directories
- **Issues**: Duplicates, redundancy, unclear organization

### After Consolidation
- **Files**: ~400 files (40% reduction)
- **Size**: ~220 MB (40% reduction)
- **Structure**: Clean, organized hierarchy
- **Benefits**: Single source of truth, faster access, clear documentation

### New Directory Structure
```
data/modules/bsee/
├── current/           # Latest, authoritative data
│   ├── production/    # All production data
│   ├── wells/         # All well data
│   ├── leases/        # All lease data
│   ├── completions/   # All completion data
│   └── surveys/       # All directional surveys
├── archive/           # Historical/legacy data (compressed)
├── raw/               # Original downloads
│   ├── binary/        # Git LFS tracked binaries
│   └── compressed/    # Zip archives
└── README.md          # Data catalog and guide
```

## Safety Features

### 1. **Full Backup**
- Automatic backup before any changes
- Stored in `data/modules/bsee.backup/`

### 2. **Dry Run Mode**
- Test all changes without modifying files
- Review operations log before execution

### 3. **Rollback Capability**
- Generated rollback script
- Can undo all changes if needed

### 4. **Validation**
- Checksum verification
- Row count validation
- Code compatibility testing

### 5. **User Approval Required**
- No deletions without explicit approval
- Review and sign-off process

## Data Categories Identified

### Production Data
- Multiple files across directories
- Different formats (CSV, Excel, Binary)
- Consolidation opportunity: Single master file

### Well Data
- Scattered across `well_data.csv`, directional surveys, etc.
- Can be organized by data type

### Completion Data
- Fragmented into perforations, properties, summary
- Can be consolidated or linked

### Legacy Data
- 394 files in legacy directory
- Most can be archived
- Keep only unique historical data

## Key Statistics

| Metric | Current | Target | Savings |
|--------|---------|--------|---------|
| Total Files | 666 | ~400 | 40% |
| Total Size | 369 MB | ~220 MB | 40% |
| Duplicate Files | TBD | 0 | 100% |
| Legacy Files | 394 | Archived | N/A |
| CSV Files | Many | Consolidated | 50%+ |

## Automation Scripts

### `inventory_generator.py`
- Scans all BSEE files
- Extracts metadata (size, type, checksums)
- Samples data content
- Generates comprehensive inventory

### `duplicate_detector.py`
- Finds exact duplicates (by checksum)
- Identifies similar CSV structures
- Analyzes redundancy patterns
- Calculates space savings

### `migration_executor.py`
- Executes approved changes
- Supports dry-run mode
- Creates audit trail
- Generates rollback script

### `migration_validator.py`
- Creates backup
- Validates file integrity
- Tests code compatibility
- Generates certification report

## Decision Points

1. **Which duplicates to keep?**
   - Keep files in `current/` or `analysis_data/`
   - Remove from `legacy/`

2. **How to handle legacy data?**
   - Archive as compressed file
   - Keep accessible but separate

3. **Consolidation strategy?**
   - Merge similar CSV files
   - Maintain separate files for different time periods

4. **Naming conventions?**
   - Use consistent patterns
   - Include data type in filename

## Risk Mitigation

| Risk | Mitigation | Status |
|------|------------|--------|
| Data Loss | Full backup before changes | ✅ Implemented |
| Breaking Code | Test import paths | ✅ Validator included |
| Wrong Deletion | User approval required | ✅ Approval template |
| Corruption | Checksum validation | ✅ In validator |
| No Rollback | Rollback script generated | ✅ Automated |

## Next Steps

1. **Run inventory generator** to understand current state
2. **Review duplicate analysis** to identify savings
3. **Get stakeholder approval** for proposed changes
4. **Execute migration** with validation
5. **Update documentation** for new structure
6. **Notify team** of changes

## Support

For questions or issues with this consolidation:
1. Review the detailed reports in `sub-specs/`
2. Check the validation report for errors
3. Use rollback script if needed
4. Keep backup until confident in new structure

---

*This consolidation follows data management best practices while maintaining complete data integrity and providing full rollback capability.*