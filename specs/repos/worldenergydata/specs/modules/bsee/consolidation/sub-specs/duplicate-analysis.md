# BSEE Duplicate Analysis Report

## Executive Summary

- **Exact Duplicates Found**: 34 sets
- **Files That Can Be Removed**: 44
- **Potential Space Savings**: 28.45 MB (7.7%)
- **CSV Files with Identical Structure**: 62 groups

## Exact Duplicates

These files have identical content (same checksum):

### Duplicate Set (Checksum: 218f3667...)

- `analysis_data/combined_data_for_analysis/all_bsee_blocks.csv` (0.0 MB)
- `legacy/data_for_analysis/all_bsee_blocks.csv` (0.0 MB)

### Duplicate Set (Checksum: 21a9ede6...)

- `analysis_data/combined_data_for_analysis/completion_perforations.csv` (0.0 MB)
- `legacy/data_for_analysis/completion_perforations.csv` (0.0 MB)

### Duplicate Set (Checksum: 141444d5...)

- `analysis_data/combined_data_for_analysis/completion_properties.csv` (0.01 MB)
- `legacy/data_for_analysis/completion_properties.csv` (0.01 MB)

### Duplicate Set (Checksum: 1c1a14fb...)

- `analysis_data/combined_data_for_analysis/completion_summary.csv` (0.0 MB)
- `legacy/data_for_analysis/completion_summary.csv` (0.0 MB)

### Duplicate Set (Checksum: 0d4840f2...)

- `analysis_data/combined_data_for_analysis/cut_casings.csv` (0.0 MB)
- `legacy/data_for_analysis/cut_casings.csv` (0.0 MB)

### Duplicate Set (Checksum: ccf99983...)

- `analysis_data/combined_data_for_analysis/geology_markers.csv` (0.0 MB)
- `legacy/data_for_analysis/geology_markers.csv` (0.0 MB)

### Duplicate Set (Checksum: 966879b3...)

- `analysis_data/combined_data_for_analysis/hydrocarbon_bearing_interval.csv` (0.01 MB)
- `legacy/data_for_analysis/hydrocarbon_bearing_interval.csv` (0.01 MB)

### Duplicate Set (Checksum: 5fec7842...)

- `analysis_data/combined_data_for_analysis/production.csv` (0.0 MB)
- `legacy/data_for_analysis/production.csv` (0.0 MB)

### Duplicate Set (Checksum: a05c8335...)

- `analysis_data/combined_data_for_analysis/ST_BP_and_tree_height.csv` (0.0 MB)
- `legacy/data_for_analysis/ST_BP_and_tree_height.csv` (0.0 MB)

### Duplicate Set (Checksum: e1c7ede4...)

- `analysis_data/combined_data_for_analysis/well_activity_bop_tests.csv` (0.0 MB)
- `legacy/data_for_analysis/well_activity_bop_tests.csv` (0.0 MB)

*... and 24 more duplicate sets*

## Files with Similar Structure

These CSV files have identical column structures:

### Structure: BOTM_FLD_NAME_CD...

- `analysis_data/combined_data_for_analysis/all_bsee_blocks.csv` (100 rows)
- `legacy/data_for_analysis/all_bsee_blocks.csv` (100 rows)

### Structure: API_WELL_NUMBER, PERF_BASE_MD, PERF_BOTM_TVD, PERF_TOP_MD, PERF_TOP_TVD...

- `analysis_data/combined_data_for_analysis/completion_perforations.csv` (100 rows)
- `legacy/data_for_analysis/completion_perforations.csv` (100 rows)

### Structure: API_WELL_NUMBER, COMP_INTERVAL_NAME, COMP_LATITUDE, COMP_LONGITUDE, COMP_RSVR_NAME...

- `analysis_data/combined_data_for_analysis/completion_properties.csv` (100 rows)
- `legacy/data_for_analysis/completion_properties.csv` (100 rows)

### Structure: API_WELL_NUMBER, COMP_AREA_CODE, COMP_BLOCK_NUMBER, COMP_STATUS_CD, INTERVAL...

- `analysis_data/combined_data_for_analysis/completion_summary.csv` (100 rows)
- `legacy/data_for_analysis/completion_summary.csv` (100 rows)

### Structure: API_WELL_NUMBER, CASING_CUT_DATE, CASING_CUT_DEPTH, CASING_CUT_MDL_IND, CASING_CUT_METHOD_CD...

- `analysis_data/combined_data_for_analysis/cut_casings.csv` (100 rows)
- `legacy/data_for_analysis/cut_casings.csv` (100 rows)

## Data Redundancy Patterns

Files grouped by data type showing potential redundancy:

### Production Files: 93 files
- `analysis_data/combined_data_for_analysis/`: 1 files
- `bin/ocsprod/`: 4 files
- `bin/production_plan_area/`: 1 files
- `bin/production_raw/`: 4 files
- `bin/historical_production_yearly/`: 30 files
- `legacy/Julia_prod_data/`: 1 files
- `legacy/data_for_analysis/`: 1 files
- `legacy/online_raw_well_data/`: 18 files
- `zip/historical_production_yearly/`: 30 files
- `zip/ocsprod/`: 1 files
- `zip/production_plan_area/`: 1 files
- `zip/production_raw/`: 1 files

### Well Files: 368 files
- `analysis_data/combined_data_for_analysis/`: 7 files
- `bin/Well_APD_Default/`: 1 files
- `bin/apiraw/`: 1 files
- `bin/apm/`: 1 files
- `bin/decomcost/`: 2 files
- `bin/ewellapd/`: 8 files
- `bin/offshorestats/`: 2 files
- `bin/scanneddocs/`: 2 files
- `legacy/`: 2 files
- `legacy/Jack_well_data/`: 11 files
- `legacy/data_for_analysis/`: 7 files
- `legacy/julia_by_block/`: 2 files
- `legacy/online_raw_well_data/`: 302 files
- `legacy/stmalo_well_data/`: 15 files
- `zip/apm/`: 1 files
- `zip/eor/`: 1 files
- `zip/ewellapd/`: 1 files
- `zip/frs/`: 1 files
- `zip/war/`: 1 files

### Completion Files: 17 files
- `analysis_data/combined_data_for_analysis/`: 3 files
- `bin/companydetails/`: 2 files
- `bin/eor/`: 4 files
- `bin/osfr/`: 1 files
- `bin/plans/`: 1 files
- `bin/scanneddocs/`: 1 files
- `bin/serialreg/`: 1 files
- `legacy/data_for_analysis/`: 3 files
- `zip/companydetails/`: 1 files

### Lease Files: 15 files
- `bin/deepqual/`: 1 files
- `bin/lab/`: 1 files
- `bin/leaseowner/`: 1 files
- `bin/mcpflow/`: 1 files
- `bin/offshorestats/`: 1 files
- `bin/platstruc/`: 1 files
- `bin/scanneddocs/`: 3 files
- `bin/serialreg/`: 5 files
- `zip/leaseowner/`: 1 files

### Survey Files: 2 files
- `bin/bhps/`: 1 files
- `bin/scanneddocs/`: 1 files

## Recommendations

1. **Immediate Actions**:
   - Remove 44 exact duplicate files
   - Save 28.45 MB immediately

2. **Consolidation Opportunities**:
   - Merge production data from multiple directories
   - Consolidate well data into single authoritative source
   - Combine fragmented completion data files

3. **Archive Strategy**:
   - Move legacy/ files to compressed archive
   - Keep only latest versions in analysis_data/
   - Remove extracted files that exist in zip archives
