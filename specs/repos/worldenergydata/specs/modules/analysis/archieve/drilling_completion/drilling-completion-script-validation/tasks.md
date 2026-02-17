# Spec Tasks

These are the tasks to be completed for the spec detailed in @specs/modules/analysis/drilling-completion-script-validation/spec.md

> Created: 2025-08-01
> Status: Ready for Implementation

## Tasks

- [x] 1. Script Replication and Test Setup
  - [x] 1.1 Create exact copy of extract_drilling_and_completion_days.py in test directory
  - [x] 1.2 Create test to run script with original input files
  - [x] 1.3 use different file name for test output file to avoid overwriting existing files
  - [x] 1.4 Verify test pass for script setup

- [x] 2. Script Execution and Output Generation
  - [x] 2.1 Execute replicated script with original input files
  - [x] 2.2 Capture and log any execution errors or warnings
  - [x] 2.3 Verify output Excel file is successfully generated
  - [x] 2.4 Verify all tests pass for script execution

- [x] 3. Data Comparison Implementation
  - [x] 3.1 Write tests for data comparison logic
  - [x] 3.2 Implement Excel file loading and structure validation
  - [x] 3.3 Create comparison logic for drilling and completion days data excluding total values
  - [x] 3.4 Implement row-by-row and cell-by-cell comparison analysis
  - [x] 3.5 Verify all tests pass for data comparison

- [x] 4. Validation Results Analysis
  - [x] 4.1 Write tests for results analysis 
  - [x] 4.2 Generate detailed comparison report with difference analysis
  - [x] 4.3 Create executive summary markdown report
  - [x] 4.4 Verify all tests pass for validation results