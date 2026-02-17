# Tests Specification

This is the tests coverage details for the spec detailed in @specs/modules/analysis/npv-data-source-comparison/spec.md

> Created: 2025-07-28
> Version: 1.0.0

## Test Coverage

### Unit Tests

**DataExtractionUtilities**
- Test Excel data extraction for production values (Row 22)
- Test Excel data extraction for oil prices (Row 2)
- Test handling of missing or invalid data
- Test data type conversions and formatting

**DataComparisonEngine**
- Test production volume comparison logic
- Test oil price comparison logic
- Test time period alignment detection
- Test scale difference detection (daily/monthly/annual)
- Test variance calculation methods

**ValidationUtilities**
- Test data integrity checks
- Test completeness validation
- Test range validation for prices and production

### Integration Tests

**Excel Data Integration**
- Test full Excel file reading workflow
- Test multi-sheet data extraction if needed
- Test data caching and retrieval
- Test error handling for corrupted/missing Excel files

**Manual Data Source Integration**
- Test BSEE production data extraction
- Test oil price data retrieval
- Test time period aggregation
- Test data format standardization

### Comparison Tests

**Production Data Comparison**
- Test exact match scenarios
- Test scale difference scenarios (1000x differences)
- Test time period misalignment scenarios
- Test missing data handling

**Price Data Comparison**
- Test exact price matching
- Test currency conversion if needed
- Test price source validation
- Test historical price alignment

### End-to-End Tests

**Complete Data Validation Workflow**
- Extract Excel benchmark data
- Extract manual analysis data
- Compare all data points
- Generate comparison report
- Validate NPV input data alignment

### Performance Tests

**Data Extraction Performance**
- Test extraction speed for large Excel files
- Test memory usage during extraction
- Test concurrent data processing

### Regression Tests

**Data Consistency**
- Test that data extraction produces consistent results
- Test that comparison logic remains stable
- Test backward compatibility with existing NPV tests

### Output File Tests

**File Generation**
- Test CSV file creation in `tests\modules\bsee\analysis\<spec_folder>\data\`
- Test visualization generation in `tests\modules\bsee\analysis\<spec_folder>\visualizations\`
- Test report generation in `tests\modules\bsee\analysis\<spec_folder>\reports\`
- Test proper file naming conventions
- Test directory creation if not exists

**File Content Validation**
- Test CSV files contain expected columns and data
- Test visualization files are valid image formats
- Test markdown reports have proper formatting
- Test JSON files have valid structure

## Mocking Requirements

- **Excel File Access:** Mock for unit tests, use real file for integration tests
- **BSEE Data Source:** Mock production data for isolated testing
- **Oil Price Service:** Mock external price data sources
- **File System:** Mock for file operations in unit tests