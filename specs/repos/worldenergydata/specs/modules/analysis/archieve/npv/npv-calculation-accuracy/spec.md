# Spec Requirements Document

> Spec: NPV Calculation Accuracy Improvement
> Created: 2025-07-25
> Status: Planning

## Overview

Improve NPV calculation accuracy to achieve within 10-20% variance from Excel analysis results, eliminating the current ~50% discrepancy between manual analysis and Excel NPV calculations with the same 10% discount rate.

Relevant files:
[npv test file](../../../tests/modules/bsee/analysis/query_field_jack_stmalo_npv_test.py)
[example NPV file](../../../docs/modules/bsee/data/NPV_JStM-WELL-Production-Data-thru-2019.xlsx)

## User Stories

### Accurate Economic Analysis

As an energy analyst, I want to perform NPV calculations that closely match Excel reference results, so that I can trust the economic evaluation for investment decisions and regulatory reporting.

The current implementation shows significant variance (up to 50%) from Excel NPV analysis using the same input parameters (10% discount rate, same production data, same oil prices). This creates uncertainty in economic evaluation and reduces confidence in automated analysis results.

### Consistent Calculation Methodology

As a data scientist, I want the NPV calculation methodology to exactly mirror Excel's NPV function behavior, so that results are reproducible and can be verified against standard financial analysis tools.

The calculation should handle cash flow timing, discount rate application, and period aggregation in the same manner as Excel's built-in NPV function, ensuring identical results given identical inputs.

## Spec Scope

1. **NPV Calculation Engine Refactoring** - Redesign the NPV calculation to exactly match Excel NPV function behavior
2. **Cash Flow Alignment** - Ensure cash flow construction matches Excel analysis methodology 
3. **Discount Rate Application** - Implement precise discount rate timing and compounding as used in Excel
4. **Data Input Validation** - Verify production data, oil prices, and cost parameters match Excel inputs exactly
5. **Results Validation Framework** - Create automated testing to verify NPV results within 10% of Excel benchmarks

suggested steps: 
- Create a workflow document which contains the following detailed steps:
  - additional Input parameters required for NPV calculation (goes to .yml input file)
  - Identify existing historical production data logic
  - Map out cash flow construction process
  - calculate npv
  - Create a detailed comparison of the current NPV calculation logic with Excel's NPV function

- Create a plan to update the existing calculation following detailed steps above
  - Should update existing npv calculation logic in src\worldenergydata\modules\bsee\analysis\production_api12.py
    - Economics Functions
      - generate_revenue_table(self, cfg, api12_df)
      - perform_npv_calculation(self, cfg, revenue_df)
      - perform_excel_aligned_npv_calculation(self, cfg, revenue_df)
    - Should ensure cash flow construction aligns with Excel methodology
  - Should implement precise discount rate timing and compounding as used in Excel
- Implement the new NPV calculation engine with comprehensive tests
- Create a validation test to compare against Excel output to benchmark

## Out of Scope

- Major changes to production data collection methodology
- Modification of underlying BSEE data processing
- Changes to visualization or reporting components unrelated to NPV accuracy

## Expected Deliverable

1. **NPV calculation accuracy within 10-20% of Excel results** when using identical input parameters
2. **Automated test suite** that validates NPV calculations against Excel benchmarks for multiple scenarios
3. **Documentation** explaining the alignment methodology and any remaining variance sources

## Spec Documentation

- Tasks: @specs/modules/analysis/npv-calculation-accuracy/tasks.md
- Technical Specification: @specs/modules/analysis/npv-calculation-accuracy/sub-specs/technical-spec.md
- Tests Specification: @specs/modules/analysis/npv-calculation-accuracy/sub-specs/tests.md