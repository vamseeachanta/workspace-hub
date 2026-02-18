# Spec Tasks

These are the tasks to be completed for the spec detailed in @specs/modules/analysis/drilling-completion-output-validation/spec.md

> Created: 2025-08-02
> Status: Ready for Implementation

## Tasks

- [x] 1. Modify Output Filename Configuration
  - [x] 1.1 Write tests to verify filename modification doesn't break existing functionality
  - [x] 1.2 Update the output filename in drilling_and_completion_days.py to include validation suffix
  - [x] 1.3 Check if any file exists with the new filename and handle appropriately
  - [x] 1.4 Verify the modified script can be imported without errors
  - [x] 1.5 Ensure all tests pass with the modified filename

- [x] 2. Execute Test and Generate Output
  - [x] 2.1 Run drilling_completion_days_test.py with the modified script
  - [x] 2.2 Verify the new output file is created in the expected location
  - [x] 2.3 Confirm the output file contains data and is not empty
  - [x] 2.4 Document the output file path and size

- [x] 3. Implement Data Comparison Logic
  - [x] 3.1 Write tests for the comparison functionality
  - [x] 3.2 Load both original and test output Excel files using pandas
  - [x] 3.3 Implement row count comparison between files
  - [x] 3.4 Develop cell-by-cell comparison logic for all columns
  - [x] 3.5 Calculate comparison metrics (exact matches, differences, percentages)
  - [x] 3.6 Handle any data type mismatches or formatting differences
  - [x] 3.7 Verify all comparison tests pass

- [x] 4. Generate Validation Report
  - [x] 4.1 Write tests for report generation functionality
  - [x] 4.2 Create markdown report structure with sections for each metric
  - [x] 4.3 Document row count comparison results
  - [x] 4.4 Include detailed cell-by-cell comparison findings
  - [x] 4.5 Calculate and display percentage accuracy metrics
  - [x] 4.6 List any discrepancies found with specific cell references
  - [x] 4.7 Add summary and conclusions section
  - [x] 4.8 Save the validation report in the results directory
  - [x] 4.9 Verify the complete validation workflow executes successfully