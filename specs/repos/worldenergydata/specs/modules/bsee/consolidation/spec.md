# Spec Requirements Document

> Spec: BSEE Data Consolidation and Cleanup
> Created: 2025-08-21
> Status: Planning
> Module: Data Management
> Priority: High

## Overview

Consolidate and improve the BSEE (Bureau of Safety and Environmental Enforcement) data organization in `data/modules/bsee/`, identifying and removing duplicates, redundant data, and proposing a clean, efficient data structure. This will reduce the 369MB data footprint, improve data access performance, and establish clear data governance for the BSEE module.

## User Stories

### Data Engineer Story

As a data engineer working with WorldEnergyData, I want a clean, well-organized BSEE data structure without duplicates, so that I can efficiently access and process energy production data without confusion or redundant storage costs.

The workflow involves:
1. Analyzing current data structure across 666 files
2. Identifying duplicate and redundant data
3. Proposing consolidation strategy
4. Getting approval before any deletions
5. Implementing approved consolidation
6. Documenting new data structure

### Data Analyst Story

As a data analyst using BSEE data, I want a single source of truth for each data type, so that I always know which file to use and don't accidentally analyze outdated or duplicate data.

The workflow includes:
1. Clear data catalog showing available datasets
2. Consistent file naming conventions
3. Documented data freshness/update dates
4. Easy access to production, well, and lease data
5. No confusion between legacy and current data

### DevOps Engineer Story

As a DevOps engineer, I want to reduce the 369MB BSEE data footprint by eliminating duplicates, so that repository cloning is faster and storage costs are reduced.

The workflow involves:
1. Identifying duplicate files by content hash
2. Finding redundant data across directories
3. Proposing archival strategy for legacy data
4. Implementing Git LFS for large binary files
5. Optimizing data formats (CSV vs binary)

## Spec Scope

1. **Data Inventory and Analysis** - Complete catalog of all 666 BSEE files with metadata
2. **Duplicate Detection** - Identify exact duplicates and near-duplicates across directories
3. **Redundancy Analysis** - Find overlapping data between legacy/, bin/, and analysis_data/
4. **Consolidation Strategy** - Propose unified data structure with clear hierarchy
5. **Cleanup Proposal** - Document all proposed deletions/moves for approval
6. **Data Migration** - Move and reorganize approved changes
7. **Documentation** - Create data catalog and access guide
8. **Validation** - Ensure no data loss and all tests still pass

## Out of Scope

- Modifying data content or formats (only organizing)
- Changing existing API or analysis code (will maintain compatibility)
- Downloading new data from BSEE (only organizing existing)
- Converting between data formats (CSV to Parquet, etc.)
- Implementing data versioning system (future enhancement)

## Expected Deliverable

1. Comprehensive data inventory report showing all 666 files with sizes, types, and content summaries
2. Duplicate analysis report identifying exact matches and redundancies (estimated 30-40% reduction)
3. Proposed new directory structure with clear separation of concerns
4. Cleanup proposal document for user approval before any deletions
5. Migration script to safely reorganize approved changes
6. Updated data catalog documentation in `data/modules/bsee/README.md`
7. Validation report confirming no data loss and all tests passing

## Current Data Structure Analysis

```
data/modules/bsee/  (369MB total)
├── analysis_data/  (16 files)
│   └── combined_data_for_analysis/  (consolidated CSVs)
├── bin/  (189 files)
│   ├── production_raw/  (binary files via Git LFS)
│   └── well_raw/  (binary files via Git LFS)
├── legacy/  (394 files - likely contains duplicates)
│   ├── data_for_analysis/
│   ├── Julia_prod_data/
│   ├── online_raw_well_data/
│   └── various Excel/CSV files
└── zip/  (67 files - compressed archives)
```

## Preliminary Observations

1. **Likely Duplicates**: 
   - `legacy/data_for_analysis/production.csv` vs `analysis_data/combined_data_for_analysis/production.csv`
   - Multiple production data files with different naming conventions
   - Binary files in `bin/` may duplicate CSV data
   
2. **Specific Examples Found**:
   - Production data in 3+ locations: `analysis_data/`, `legacy/`, `bin/production_raw/`
   - Well data scattered: `well_data.csv`, `well_directional_surveys.csv`, binary well files
   - Completion data fragmented: `completion_perforations.csv`, `completion_properties.csv`, `completion_summary.csv`

2. **Redundancy Issues**:
   - 394 files in legacy/ suggests accumulation over time
   - Zip files may contain duplicates of extracted data
   - Different date formats and naming conventions for same data

3. **Organization Issues**:
   - No clear versioning or date strategy
   - Mixed formats (CSV, Excel, binary, zip)
   - Unclear which data is authoritative

## Proposed Approach

1. **Phase 1**: Inventory and catalog all files
2. **Phase 2**: Calculate checksums and identify exact duplicates
3. **Phase 3**: Analyze content overlap in non-identical files
4. **Phase 4**: Propose consolidated structure
5. **Phase 5**: Get user approval for cleanup actions
6. **Phase 6**: Execute approved migration
7. **Phase 7**: Validate and document

## Risk Mitigation

1. **Data Loss Prevention**: Create full backup before any changes
2. **Compatibility**: Ensure all existing code continues to work
3. **Rollback Plan**: Keep archived copy of original structure
4. **Incremental Changes**: Move files in small batches with validation
5. **User Approval**: No deletions without explicit approval

## Success Metrics

- Reduce data footprint by 30-40% (from 369MB to ~220MB)
- Zero data loss (all unique data preserved)
- All existing tests continue to pass
- Clear documentation for data access
- Improved data loading performance

## Spec Documentation

- Tasks: @specs/modules/bsee/consolidation/tasks.md
- Technical Specification: @specs/modules/bsee/consolidation/sub-specs/technical-spec.md
- Data Inventory: @specs/modules/bsee/consolidation/sub-specs/data-inventory.md
- Cleanup Proposal: @specs/modules/bsee/consolidation/sub-specs/cleanup-proposal.md
- Migration Plan: @specs/modules/bsee/consolidation/sub-specs/migration-plan.md