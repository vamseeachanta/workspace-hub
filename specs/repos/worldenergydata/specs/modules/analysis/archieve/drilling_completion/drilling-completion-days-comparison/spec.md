# Spec Requirements Document

> Spec: Drilling Days Comparison Test
> Created: 2025-08-04
> Status: Planning

## User Prompt

> This spec was initiated based on the following user request:

```
I need to create a spec for a drilling days test comparison between two methods (lease_num vs api12_num). The spec should compare the outputs of these two different approaches and generate a comparison table in markdown format.

**Details:**
- Method 1 (lease_num): Uses lease number approach with test 'tests\modules\bsee\analysis\drilling_completion_days_test.py' and implementation in "src\worldenergydata\modules\bsee\analysis\custom_scripts\Roy\july\drilling_and_completion_days.py"
- Method 2 (api12_num): Uses API12 number approach with test 'tests\modules\bsee\analysis\query_api_01_wells_api12_rig_days_Tiber_test.py' and implementation in "src\worldenergydata\modules\bsee\analysis\well_api12.py"
- Key columns for comparison: api12 number, drilling days, completion days
- Goal: Write a test that compares both methods' output files and creates comparison table in markdown format
```

## Overview

Implement a comprehensive comparison test framework that validates and compares drilling days and completion days analysis outputs from two different BSEE data processing methods. This feature will enable quality assurance, method validation, and help identify discrepancies between lease-based and API12-based drilling and completion days calculations, providing detailed statistical analysis of time variance between both approaches.

## User Stories

### Data Analyst Validation Story

As a **BSEE Data Analyst**, I want to compare drilling days outputs from different calculation methods, so that I can validate data accuracy and identify potential issues in drilling days analysis before using results for economic evaluation or reporting.

**Detailed Workflow:**
1. Execute both lease_num and api12_num drilling days tests
2. Load and process output files from both methods
3. Perform side-by-side comparison of key metrics (API12, drilling days, completion days)
4. Generate a comprehensive markdown comparison table
5. Identify and flag any significant discrepancies between methods
6. Export comparison results for further analysis or reporting

### Quality Assurance Story

As a **Data Quality Engineer**, I want to automate the comparison of different drilling days calculation approaches, so that I can ensure consistency and reliability of drilling days analysis across different data processing workflows.

**Detailed Workflow:**
1. Set up automated test execution for both methods
2. Implement data validation checks for output consistency
3. Generate automated comparison reports highlighting differences
4. Create alerts for significant discrepancies that require investigation

## Spec Scope

1. **Comparison Test Framework** - Create a comprehensive test that executes both drilling days methods and compares their outputs
2. **Data Loading and Processing** - Implement robust data loading from both method outputs with appropriate error handling
3. **Comparison Analysis Engine** - Develop comparison logic to identify differences in API12, drilling days, and completion days
4. **Drilling and Completion Days Comparison** - Implement detailed comparison of drilling and completion days between both methods with statistical analysis
5. **Markdown Report Generation** - Create formatted markdown tables showing side-by-side comparison of results with drilling/completion days variance analysis
6. **Discrepancy Detection** - Implement logic to flag significant differences and potential data quality issues in drilling and completion days calculations

## Out of Scope

- Modification of existing drilling days calculation methods
- Performance optimization of the underlying analysis engines
- Integration with external reporting systems
- Real-time comparison monitoring
- Historical comparison trending analysis

## Expected Deliverable

1. **Functional Comparison Test** - A pytest-based test that successfully executes both methods and generates comparison output
2. **Comprehensive Drilling and Completion Days Comparison Report** - Markdown-formatted comparison table showing API12 numbers with their corresponding drilling/completion days from both methods:
   - API number column
   - Drilling days lease method column
   - Drilling days api12 method column  
   - Completion days lease method column
   - Completion days api12 method column
   - Each row represents one API number with its corresponding drilling and completion days from both approaches
3. **Data Quality Validation** - Automated identification and reporting of discrepancies between the two methods for drilling and completion days calculations

## Spec Documentation

- Tasks: @specs/modules/analysis/drilling-completion-days-comparison/tasks.md
- Technical Specification: @specs/modules/analysis/drilling-completion-days-comparison/sub-specs/technical-spec.md
- Tests Specification: @specs/modules/analysis/drilling-completion-days-comparison/sub-specs/tests.md