# Spec Requirements Document

> Spec: drilling-script-validation
> Created: 2025-08-01
> Status: Planning

## User Prompt

> This spec was initiated based on the following user request:

```
to check whether the latest already implemented script with war files generates exact same ouput data by implementing in worldenergydata.
refer implemented script:"docs\modules\bsee\data\SME_Roy_attachments\2025-08-01\extract_drilling_and_completion_days.py",
refer output file for comparison:"docs\modules\bsee\data\SME_Roy_attachments\2025-08-01\drilling_and_completion_days_by_api.xlsx" ,
follow below process:
1. create new script with same content of implemented script with no any code modifications.
2. use input files from folder "docs\modules\bsee\data\SME_Roy_attachments\2025-08-01".
3. run the script to check whether output file generated.
4. if generates, compare the generated script with executed output file .
5. if the output matches , create markdown which gives executive summary of what we have achieved.
```

## Overview

Validate that the existing drilling and completion days extraction script produces identical output to the executed file by creating a test implementation that replicates the exact functionality and compares the generated output against the known reference data.

## User Stories

### Script Validation and Output Verification

As an energy data analyst, I want to verify that the drilling and completion days extraction script produces consistent and accurate results, so that I can trust the data processing pipeline for production analysis and economic evaluation.

This involves creating an identical copy of the existing script, running it with the same input data files (leases.csv, mv_war_main.txt, mv_war_boreholes_view.txt, mv_war_main_prop.txt), and systematically comparing the generated output against the reference Excel file to ensure data consistency and accuracy.

## Spec Scope

1. **Script Replication** - Create exact copy of extract_drilling_and_completion_days.py with no code modifications
2. **Test Execution** - Run the replicated script using input files from the 2025-08-01 folder
3. **Output Generation Verification** - Confirm that the script successfully generates drilling_and_completion_days_by_api.xlsx
4. **Data Comparison Analysis** - Compare generated output with reference file, excluding total values in DRILLING_DAYS and COMPLETION_DAYS columns
5. **Executive Summary Documentation** - Create markdown report summarizing validation results and achievements

## Out of Scope

- Modifying or improving the existing script logic
- Adding new features or functionality to the script
- Performance optimization or code refactoring
- Analysis of data quality or accuracy improvements
- Integration with worldenergydata package structure

## Expected Deliverable

1. Successful replication and execution of the drilling and completion days extraction script
2. Generated output file data that matches the reference output file data 
3. Comprehensive comparison report documenting data consistency between generated and reference outputs

## Spec Documentation

- Tasks: @specs/modules/analysis/drilling-completion-script-validation/tasks.md
- Technical Specification: @specs/modules/analysis/drilling-completion-script-validation/sub-specs/technical-spec.md
- Tests Specification: @specs/modules/analysis/drilling-completion-script-validation/sub-specs/tests.md