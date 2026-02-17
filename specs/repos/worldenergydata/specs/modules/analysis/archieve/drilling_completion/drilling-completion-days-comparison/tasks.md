# Spec Tasks

These are the tasks to be completed for the spec detailed in @specs/modules/analysis/drilling-completion-days-comparison/spec.md

> Created: 2025-07-29
> Status: Ready for Implementation

## Tasks

- [x] 1. Run Both Method Tests and Validate Output
  - [x] 1.1 Execute lease method test (tests/modules/bsee/analysis/drilling_completion_days_test.py)
  - [x] 1.2 Execute api12 method test (tests/modules/bsee/analysis/query_api_01_wells_api12_rig_days_Tiber_test.py)
  - [x] 1.3 Verify both tests generate output files
  - [x] 1.4 Check that output files are not empty and contain required columns
  - [x] 1.5 Validate data integrity of both method outputs

- [x] 2. Create Comparison Logic
  - [x] 2.1 Write tests for comparison logic functions
  - [x] 2.2 Implement data loading for both method outputs
  - [x] 2.3 Create API12 matching logic between datasets
  - [x] 2.4 Implement drilling days and completion days comparison
  - [x] 2.5 Verify comparison logic tests pass

- [x] 3. Develop Markdown Report Generator
  - [x] 3.1 Write tests for MarkdownReportGenerator class
  - [x] 3.2 Implement markdown table formatting logic
  - [x] 3.3 Create column alignment and spacing functionality
  - [x] 3.4 Add status flag generation (OK/REVIEW/ERROR)
  - [x] 3.5 Implement file output handling
  - [x] 3.6 Verify all tests pass

- [x] 4. CSV Output Generation for Future Use
  - [x] 4.1 Write tests for CSV export functionality
  - [x] 4.2 Implement CSV export for comparison results with all drilling/completion days data
  - [x] 4.3 Create standardized CSV format with columns:
    - API12_number, Well_name, lease_method_drilling_days, api12_method_drilling_days
    - lease_method_completion_days, api12_method_completion_days
    - Drilling_days_difference, Completion_days_difference
    - Drilling_days_percent_diff, Completion_days_percent_diff
    - Status_flag, Notes
  - [x] 4.4 Save individual method outputs as separate CSV files:
    - drilling_days_lease_method_YYYYMMDD.csv
    - drilling_days_api12_method_YYYYMMDD.csv
    - drilling_days_comparison_YYYYMMDD.csv
  - [x] 4.5 Implement CSV file naming with timestamps for version control
  - [x] 4.6 Add CSV metadata headers with processing date and method details
  - [x] 4.7 Create CSV files in results directory for easy access and future analysis
  - [x] 4.8 Verify CSV output accuracy and data integrity
  - [x] 4.9 Test CSV import/export compatibility with Excel and pandas
  - [x] 4.10 Verify all CSV generation tests pass