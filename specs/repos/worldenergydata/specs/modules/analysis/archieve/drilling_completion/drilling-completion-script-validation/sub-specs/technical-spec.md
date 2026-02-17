# Technical Specification

This is the technical specification for the spec detailed in @specs/modules/analysis/drilling-completion-script-validation/spec.md

> Created: 2025-08-01
> Version: 1.0.0

## Technical Requirements

- **Exact Script Replication**: Create identical copy of extract_drilling_and_completion_days.py with zero code modifications
- **Input File Processing**: Use existing CSV and TXT files from docs/modules/bsee/data/SME_Roy_attachments/2025-08-01/ directory
- **Output File Generation**: Generate drilling_and_completion_days_by_api.xlsx in the same format as reference
- **Data Comparison Logic**: Compare all columns except total values in DRILLING_DAYS and COMPLETION_DAYS columns
- **Validation Framework**: Implement pandas-based comparison with row-by-row and column-by-column analysis
- **Executive Report Generation**: Create markdown summary report of validation results

## Approach Options

**Option A:** Direct Script Copy and Execution
- Pros: Exact replication, no interpretation errors, maintains original logic
- Cons: No integration with worldenergydata package structure

**Option B:** Integration with WorldEnergyData Package (Rejected)
- Pros: Better code organization, reusable components
- Cons: Requires code modifications, changes original script behavior

**Rationale:** Option A selected to ensure exact replication without any modifications that could introduce differences in output data.

## External Dependencies

- **pandas** - Already available for DataFrame operations and Excel file handling
- **openpyxl** - Already available for Excel file reading/writing operations
- **deepdiff** - Already available for detailed data comparison analysis

**Justification:** All required dependencies are already included in the project's existing tech stack, no new dependencies needed.

## Implementation Details

### Script Replication Process
1. Copy extract_drilling_and_completion_days.py to test directory
2. Ensure all input files are accessible in the same relative path structure
3. Execute script in isolated test environment
4. Capture and validate output file generation

### Data Comparison Strategy
1. Load both generated and reference Excel files using pandas
2. Compare column structures and data types
3. Perform row-by-row comparison excluding totals rows
4. Generate detailed difference report with specific cell-level analysis
5. Calculate match percentage and identify any discrepancies

### Output Validation Criteria
- Column names and order must match exactly
- Data types must be consistent
- Row count must match (excluding total rows)
- Cell values must be identical within floating-point precision
- Date formatting must be consistent