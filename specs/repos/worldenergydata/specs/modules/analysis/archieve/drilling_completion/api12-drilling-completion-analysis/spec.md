# Spec Requirements Document

> Spec: API12 Drilling and Completion Days Analysis
> Created: 2025-08-05
> Status: Planning

## User Prompt

> This spec was initiated based on the following user request:

```
for analysis on difference between api12 wells of two different bsee methods for drilling and completion days.
follow below points:
1. refer lease method output file:"tests\modules\bsee\analysis\results\drilling_and_completion_days_by_api_validation_20250805_191100.xlsx"
2. refer api12 method output:"tests\modules\bsee\analysis\results\well_summ_multiple_wells.csv"
3. refer implementation scripts:
  lease: src\worldenergydata\modules\bsee\analysis\custom_scripts\Roy\july\drilling_and_completion_days.py
  api12: src\worldenergydata\modules\bsee\analysis\well_api12.py
4. do analysis for 2 api12 wells from both outputs
  4.1 one well with high difference
  4.2 one well with small difference 
5. analysis includes:
  5.1 how drilling and completion days are being calculated
  5.2 what are root causes for differences between drilling , completion days.
6. create one markdown file which describes the drilling, completion days calculated strategy of both methods  and root causes for differences
```

## Overview

Perform a comparative analysis of drilling and completion days calculations between two different BSEE methods (lease-based and API12-based) to identify discrepancies, understand calculation methodologies, identifying input data source for both methods and document root causes for differences in the results.

## User Stories

### Drilling and Completion Days Methodology Analysis

As a petroleum engineer analyzing well data, I want to understand how different methods calculate drilling and completion days, so that I can identify which approach provides more accurate timelines and make informed decisions about well performance metrics.

The analysis will examine two specific API12 wells - one with high differences between methods and one with small differences - to understand the calculation logic in both the lease-based method (drilling_and_completion_days.py) and the API12 method (well_api12.py). This will help identify systematic biases or calculation errors that could affect well economics and performance evaluations.

### Root Cause Analysis Documentation

As a data analyst working with BSEE data, I want comprehensive documentation of why the two methods produce different results for drilling and completion days, so that I can recommend the most appropriate method for future analyses and ensure data consistency across projects.

## Spec Scope

1. **Comparative Data Analysis** - Analyze drilling and completion days from both lease method output and API12 method output files
2. **Well Selection and Comparison** - Identify and analyze two specific API12 wells representing high and low difference scenarios
3. **Methodology Documentation** - Document the calculation strategies and input data sources used by both drilling_and_completion_days.py and well_api12.py scripts
4. **Root Cause Analysis** - Identify the fundamental reasons causing differences in drilling and completion day calculations
5. **Analysis Report Generation** - Create a comprehensive markdown report documenting findings, methodologies, and recommendations

## Out of Scope

- Modification of existing calculation methods or scripts
- Analysis of wells beyond the two selected representative cases
- Development of new calculation algorithms
- Integration with other BSEE data analysis modules

## Expected Deliverable

1. **Comparative Analysis Results** - Detailed comparison of drilling and completion days for two selected API12 wells showing high and low differences
2. **Methodology Documentation** - Clear documentation of how each method calculates drilling and completion days, including data sources and processing logic
3. **Root Cause Analysis Report** - Comprehensive markdown report identifying why differences occur between the two methods and their implications for well analysis

## Spec Documentation

- Tasks: @specs/modules/analysis/api12-drilling-completion-analysis/tasks.md
- Technical Specification: @specs/modules/analysis/api12-drilling-completion-analysis/sub-specs/technical-spec.md
- Tests Specification: @specs/modules/analysis/api12-drilling-completion-analysis/sub-specs/tests.md