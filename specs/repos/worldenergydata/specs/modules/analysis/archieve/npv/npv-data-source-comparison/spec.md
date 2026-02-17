# Spec Requirements Document

> Spec: NPV Data Source Comparison and Validation
> Created: 2025-07-28
> Status: Planning

## Overview

Identify and resolve differences between manual analysis data sources (oil production and prices) from the worldenergydata modules and the legacy Excel benchmark data (docs\modules\bsee\data\NPV_JStM-WELL-Production-Data-thru-2019.xlsx) to ensure NPV calculations use identical input data, building upon the completed NPV calculation accuracy improvements from spec 2025-07-25-npv-calculation-accuracy.

### Future Update Prompt

For future modifications to this spec, use the following prompt:
```
Update the NPV data source comparison spec to include:
- Additional data sources beyond the legacy Excel file
- New validation requirements for data accuracy
- Extended time periods beyond 2019
- Additional fields or metrics for comparison
Maintain compatibility with existing data extraction utilities and ensure all changes preserve the ability to compare legacy Excel data with worldenergydata outputs.
```

## User Stories

### Data Source Alignment

As an energy analyst, I want to ensure that manual NPV calculations use the exact same production data and oil prices as the Excel benchmarks, so that NPV variance is solely due to calculation methodology rather than input data differences.

The completed NPV accuracy spec showed a 44.55% variance even with improved calculation methodology. This spec focuses on identifying and eliminating data source differences to further reduce this variance to the target <20%.

### Production Data Validation

As a data scientist, I want to validate that production volumes extracted from BSEE systems via worldenergydata modules match the production data used in the legacy Excel analysis file (NPV_JStM-WELL-Production-Data-thru-2019.xlsx, Row 22 - JSM Total AVGMoly), so that cash flow calculations are based on identical production inputs.

Current implementation may be using different production data sources or time periods, leading to significant NPV differences even with correct calculation methodology.

## Spec Scope

1. **Production Data Source Analysis** - Compare worldenergydata module production data extraction with legacy Excel benchmark (docs\modules\bsee\data\NPV_JStM-WELL-Production-Data-thru-2019.xlsx) production volumes
2. **Oil Price Data Validation** - Verify worldenergydata oil price sources match Excel BRENT prices (Row 2) exactly
3. **Time Period Alignment** - Ensure worldenergydata and Excel analyses cover identical time periods (through 2019) with same aggregation
4. **Data Extraction Utilities** - Create robust utilities to extract and validate data from the legacy Excel benchmark file
5. **Comprehensive Comparison Tests** - Build test suite that validates data alignment between worldenergydata and legacy Excel sources before NPV calculation

## Out of Scope

- Changes to NPV calculation methodology (already addressed in spec 2025-07-25)
- Modifications to underlying BSEE data processing logic
- Changes to production data collection from original sources
- UI or visualization updates

## Expected Deliverable

1. **Data comparison report** showing exact differences between worldenergydata and legacy Excel data sources (NPV_JStM-WELL-Production-Data-thru-2019.xlsx)
2. **Automated test suite** that validates production and price data alignment between both sources
3. **Data extraction utilities** that reliably extract benchmark data from the legacy Excel file for comparison with worldenergydata outputs
4. **Output files** organized in `tests\modules\bsee\analysis\<spec_folder>\` including:
   - CSV files with extracted data and comparisons
   - Visualization charts (PNG/PDF) showing data differences
   - Markdown reports documenting findings
   - JSON files with structured comparison results

## Spec Documentation

- Tasks: @specs/modules/analysis/npv-data-source-comparison/tasks.md
- Technical Specification: @specs/modules/analysis/npv-data-source-comparison/sub-specs/technical-spec.md
- Tests Specification: @specs/modules/analysis/npv-data-source-comparison/sub-specs/tests.md