# Spec Requirements Document

> Spec: Drilling Completion Output Validation
> Created: 2025-08-02
> Status: Planning

## User Prompt

> This spec was initiated based on the following user request:

```
to validate original drilling completion days output with worldenergydata test output .
refer: main test file for worldenergydata:"tests\modules\bsee\analysis\drilling_completion_days_test.py"
refer test script:"src\worldenergydata\modules\bsee\analysis\custom_scripts\Roy\july\drilling_and_completion_days.py"
refer original output:"docs\modules\bsee\data\SME_Roy_attachments\2025-08-01\drilling_and_completion_days_by_api.xlsx"
follow below instrcutions for output validation:
1. use different output file name to not override existing files and check any file exists with the new file name.
2. run the test and check whether output file is generated or not
3. compare the test output with original output
4. create summary file of what have achieved in markdown format.

Additional clarification:
1. No , update the file name in "src\worldenergydata\modules\bsee\analysis\custom_scripts\Roy\july\drilling_and_completion_days.py" and run test i have given "tests\modules\bsee\analysis\drilling_completion_days_test.py"
2. For comparison , check total row count and also cell by cell analysis for right values.
3. Yes , include specific metrics like % , exact matches.
4. one-time check
```

## Overview

Validate the worldenergydata drilling completion days analysis output against the original reference output to ensure accuracy and consistency of the implementation. This one-time validation will verify that the test framework produces identical results to the original script.

## User Stories

### Data Validation Engineer

As a data validation engineer, I want to verify that the worldenergydata test implementation produces identical results to the original drilling completion days script, so that I can ensure data accuracy and reliability of the analysis.

The workflow involves modifying the output filename in the script, running the existing test, comparing outputs cell-by-cell, and documenting the validation results with specific metrics including percentage matches and exact value comparisons.

## Spec Scope

1. **Output File Configuration** - Modify the drilling_and_completion_days.py script to use a new output filename that doesn't override existing files and check if any file exists with this new name.
2. **Test Execution** - Run the drilling_completion_days_test.py to generate new output with the modified filename
3. **Data Comparison** - Perform comprehensive comparison between test output and original output including row counts and cell-by-cell analysis
4. **Validation Report** - Create a detailed markdown summary with metrics including exact matches, percentage accuracy, and any discrepancies

## Out of Scope

- Modifying the core logic of the drilling completion analysis
- Creating new test cases or test frameworks
- Integrating this validation as a permanent test fixture
- Analyzing or fixing any discrepancies found (only reporting them)

## Expected Deliverable

1. Modified script with new output filename that successfully generates output without overwriting existing files
2. Comprehensive comparison report showing row counts, cell-by-cell matches, percentage accuracy, and detailed metrics
3. Markdown summary document with validation results, metrics, and conclusions

## Spec Documentation

- Tasks: @specs/modules/analysis/drilling-completion-output-validation/tasks.md
- Technical Specification: @specs/modules/analysis/drilling-completion-output-validation/sub-specs/technical-spec.md
- Tests Specification: @specs/modules/analysis/drilling-completion-output-validation/sub-specs/tests.md