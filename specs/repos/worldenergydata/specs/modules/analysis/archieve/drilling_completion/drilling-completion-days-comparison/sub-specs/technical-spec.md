# Technical Specification

This is the technical specification for the spec detailed in @specs/2025-07-29-drilling-days-comparison/spec.md

> Created: 2025-07-29
> Version: 1.0.0

## Technical Requirements

- **Test Framework Integration** - Use existing pytest framework with deepdiff for data comparison
- **Output File Processing** - Handle Excel (.xlsx) and CSV file formats from both methods
- **Data Alignment** - Match wells by API12 number across both methods' outputs
- **Comparison Metrics** - Calculate absolute and percentage differences for drilling and completion days
- **Markdown Generation** - Create well-formatted markdown tables with proper alignment and formatting
- **Error Handling** - Robust handling of missing files, empty datasets, and data format inconsistencies
- **Configuration Flexibility** - Support for different test configurations and output locations

## Approach Options

**Option A: Sequential Test Execution**
- Pros: Simple implementation, clear separation of concerns, easier debugging
- Cons: Longer execution time, potential for inconsistent state between tests

**Option B: Parallel Test Execution** (Selected)
- Pros: Faster execution, efficient resource usage, realistic production scenario
- Cons: More complex synchronization, potential for resource conflicts

**Option C: Mock Data Comparison**
- Pros: Fast execution, consistent test data, no dependency on actual data files
- Cons: Doesn't test real data scenarios, may miss actual implementation issues

**Rationale:** Option B provides the most realistic testing scenario while maintaining efficiency. The comparison test should validate actual output from both methods running under realistic conditions.

## External Dependencies

- **pandas** - DataFrame operations and Excel/CSV file handling
- **openpyxl** - Excel file reading for Method 1 outputs
- **pathlib** - Modern file path handling and validation
- **pytest** - Test framework integration
- **deepdiff** - Data comparison utilities (already available)

**Justification:** All dependencies are already part of the existing tech stack, ensuring no additional package management overhead.

## Implementation Architecture

### Test Structure
```
tests/modules/bsee/analysis/
├── drilling_days_comparison_test.py      # Main comparison test
└── drilling_days_comparison_config.yml   # Test configuration
```

### Method Output Analysis
- **Method 1 Output**: `drilling_and_completion_days_by_api.xlsx`
  - Columns: API_WELL_NUMBER, WELL_NAME, WELL_SPUD_DATE, TOTAL_DEPTH_DATE, DRILLING_DAYS, COMPLETION_DAYS
- **Method 2 Output**: `well_summ_*.csv` 
  - Columns: API12, WELL_NAME, Drilling Days, Completion Days, plus additional metadata

### Comparison Algorithm
1. Load both output files with appropriate error handling
2. Standardize column names and data types
3. Perform inner join on API12/API_WELL_NUMBER
4. Calculate differences and percentage variations
5. Generate markdown comparison table
6. Flag significant discrepancies (>10% difference or >5 days absolute difference)

### Output Format
The comparison will generate a markdown table with the following structure:
- API12 Number
- Well Name
- Method 1 Drilling Days
- Method 2 Drilling Days  
- Drilling Days Difference
- Method 1 Completion Days
- Method 2 Completion Days
- Completion Days Difference
- Status (OK/REVIEW/ERROR)