# Technical Specification

This is the technical specification for the spec detailed in @specs/modules/analysis/npv-data-source-comparison/spec.md

> Created: 2025-07-28
> Version: 1.0.0

## Technical Requirements

### Data Source Identification

#### Legacy Calculation Data Sources
- **Excel Benchmark File**: `docs\modules\bsee\data\NPV_JStM-WELL-Production-Data-thru-2019.xlsx`
  - Production data location (Row 22 - JSM Total AVGMoly)
  - Oil price data location (Row 2 - BRENT prices)
  - Time period coverage: Through 2019
  - Contains historical production and pricing data used in original NPV calculations

#### WorldEnergyData Sources
- Production data extraction from BSEE database
  - Direct API/database queries
  - Oil production volumes by field and well
- Oil price data sources (internal vs external APIs)
- Time period coverage and aggregation methods
- Data processing through worldenergydata modules

### Data Extraction Requirements
- Excel data extraction utilities must:
  - Read specific rows/columns from docs\modules\bsee\data\NPV_JStM-WELL-Production-Data-thru-2019.xlsx
  - Handle different data formats (numbers, currency, percentages)
  - Validate data integrity and completeness
  - Support multiple sheet extraction if needed

### Data Comparison Framework

#### Comparison Methodology
- Extract production data from both sources:
  - Legacy: Excel file Row 22 (JSM Total AVGMoly)
  - WorldEnergyData: BSEE module production data for Jack/St. Malo field
- Extract oil price data from both sources:
  - Legacy: Excel file Row 2 (BRENT prices)
  - WorldEnergyData: Oil price API/module data
  
#### Comparison Points
- Compare production volumes month-by-month
- Compare oil prices period-by-period
- Identify:
  - Missing data points
  - Scale differences (e.g., daily vs monthly production)
  - Time period misalignments
  - Unit differences (BBL vs MMBBL)
  - Aggregation method differences
  - Data precision differences

### Performance Requirements
- Data extraction should complete within 2 seconds
- Comparison analysis should handle up to 360 months of data
- Memory efficient processing for large datasets

### Output File Management
- All output files must be saved to: `tests\modules\bsee\analysis\<spec_folder>\`
- Output file types include:
  - CSV files for data comparisons and extracted values
  - PNG/PDF files for visualization charts
  - Markdown files for comparison reports
  - JSON files for structured comparison results
- Directory structure:
  ```
  tests\modules\bsee\analysis\<spec_folder>\
  ├── data\           # CSV and JSON data files
  ├── visualizations\ # Charts and graphs
  └── reports\        # Markdown and text reports
  ```
- Note: `<spec_folder>` should match the spec folder name (e.g., `npv-data-source-comparison` for this spec)

## Approach Options

**Option A:** Direct Excel Integration
- Pros: Exact data match, single source of truth
- Cons: Excel dependency, slower processing

**Option B:** Cached Data Approach (Selected)
- Pros: Fast processing, version control for data, testable
- Cons: Requires synchronization with Excel updates

**Rationale:** Option B selected for better testing capabilities and performance while maintaining data accuracy through validation.

## External Dependencies

- **openpyxl** - Already in use for Excel file reading
- **pandas** - Already in use for data manipulation
- **numpy** - Already in use for numerical operations

No new external dependencies required.