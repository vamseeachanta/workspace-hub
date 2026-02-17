# Technical Specification

This is the technical specification for the spec detailed in @specs/modules/bsee/financial-analysis-sme-code/spec.md

> Created: 2025-08-19
> Version: 1.0.0

## Technical Requirements

### Core Functionality
- Process BSEE lease data with production volumes and financial metrics
- Calculate monthly cash flows including CAPEX (drilling and completion) and OPEX
- Apply tax calculations and net revenue computations
- Generate grouped lease-level analysis based on configurable mappings
- Export formatted Excel workbooks with multiple analysis tabs

### Data Processing Requirements
- Handle large datasets (100+ leases, 10+ years of monthly data)
- Support batch processing with error recovery
- Validate input data formats and ranges
- Calculate NPV and other economic indicators
- Maintain data integrity throughout processing pipeline

### Integration Requirements
- Integrate with existing worldenergydata module structure
- Use established data loading patterns from BSEE module
- Follow project's YAML configuration approach
- Utilize pandas and openpyxl for data manipulation and Excel generation
- Maintain compatibility with UV package management

### Performance Criteria
- Process 100 leases in under 60 seconds
- Memory usage under 2GB for typical runs
- Support incremental processing for large datasets
- Enable parallel processing where applicable

## Approach Options

**Option A: Direct Port of Existing Scripts**
- Pros: Quick implementation, proven logic, minimal risk
- Cons: Limited extensibility, code duplication, harder maintenance

**Option B: Refactored Modular Architecture** (Selected)
- Pros: Maintainable, testable, extensible, follows project patterns
- Cons: More initial development time, requires comprehensive testing

**Rationale:** Option B provides better long-term maintainability and aligns with the project's modular architecture. It enables easier testing, debugging, and future enhancements.

## Implementation Architecture

### Module Structure
```
worldenergydata/modules/bsee/analysis/sme_financial/
├── __init__.py
├── financial_analyzer.py      # Main analyzer class
├── lease_processor.py          # Lease data processing
├── cash_flow_calculator.py     # Cash flow calculations
├── report_generator.py         # Excel report generation
├── formatters.py               # Excel formatting utilities
├── validators.py               # Data validation
└── config.py                   # Configuration and constants
```

### Key Classes and Components

1. **FinancialAnalyzer** - Main orchestrator class
   - Methods: `analyze()`, `process_leases()`, `generate_reports()`
   - Manages the complete analysis pipeline

2. **LeaseProcessor** - Handles lease data and grouping
   - Methods: `load_lease_data()`, `apply_grouping()`, `aggregate_by_group()`
   - Manages lease-to-group mappings

3. **CashFlowCalculator** - Financial calculations engine
   - Methods: `calculate_monthly_cash_flow()`, `calculate_npv()`, `apply_taxes()`
   - Implements V18 financial methodology

4. **ReportGenerator** - Excel report creation
   - Methods: `create_workbook()`, `add_summary_sheet()`, `add_lease_sheets()`
   - Generates formatted Excel outputs

5. **ExcelFormatter** - Formatting utilities
   - Methods: `format_columns()`, `apply_number_formats()`, `style_headers()`
   - Applies consistent formatting

## External Dependencies

### Existing Project Dependencies (Already Available)
- **pandas** (>=1.3.0) - Data manipulation and analysis
- **numpy** - Numerical computations
- **openpyxl** - Excel file generation and formatting
- **pyyaml** - Configuration file parsing

### New Dependencies (None Required)
All required functionality can be implemented using existing project dependencies.

## Configuration Schema

```yaml
# sme_financial_config.yaml
financial_analysis:
  version: "V18_011"
  
  lease_groups:
    Stones: "Stones"
    Cascade: "Cascade Chinook"
    Chinook: "Cascade Chinook"
    Julia: "Julia"
    Anchor: "Anchor"
    Jack: "Jack"
    St Malo: "St Malo"
    Kaskida: "Kaskida"
    Tiber: "Tiber"
    Shenandoah: "Shenandoah"
    North Platte: "North Platte"
    Big Foot: "Big Foot"
  
  output:
    excel_filename: "financial_analysis_V18_011.xlsx"
    include_readme: true
    format_dates: true
    format_numbers: true
    
  calculations:
    tax_rate: 0.35
    discount_rate: 0.10
    include_drilling_costs: true
    include_completion_costs: true
```

## Error Handling Strategy

1. **Input Validation**
   - Verify required columns exist in input data
   - Check data types and ranges
   - Validate lease names against configuration

2. **Processing Errors**
   - Log errors with context for debugging
   - Continue processing other leases on individual failures
   - Collect and report all errors at end

3. **Output Validation**
   - Verify all expected sheets created
   - Check for data completeness
   - Validate calculated totals

## Logging and Monitoring

- Use Python's logging module with appropriate levels
- Log processing progress for long-running operations
- Include timing metrics for performance monitoring
- Provide summary statistics on completion