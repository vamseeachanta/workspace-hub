# Tests Specification

This is the tests coverage details for the spec detailed in @specs/modules/analysis/drilling-completion-days-comparison/spec.md

> Created: 2025-07-29
> Version: 1.0.0

## Test Coverage

### Unit Tests

**ComparisonDataLoader**
- Test loading Excel files from Method 1 (lease_num approach)
- Test loading CSV files from Method 2 (api12_num approach)
- Test handling of missing or corrupted files
- Test data type validation and conversion
- Test column name standardization

**ComparisonAnalyzer**
- Test API12 matching logic between datasets
- Test drilling days difference calculations
- Test completion days difference calculations
- Test percentage difference calculations
- Test discrepancy flagging logic (thresholds)

**MarkdownReportGenerator**
- Test markdown table formatting with specific columns: API number, drilling days lease method, drilling days api12 method, completion days lease method, completion days api12 method
- Test column alignment and spacing for the 5-column comparison table
- Test handling of missing data in reports
- Test file output and path handling

### Integration Tests

**End-to-End Comparison Workflow**
- Test complete workflow from test execution to report generation
- Test with actual output files from both methods
- Test comparison of Tiber field data (API12: 608084001500)
- Test handling of datasets with different well counts
- Test comparison accuracy with known reference data

**File System Integration**
- Test output directory creation and management
- Test file path resolution for both method outputs
- Test cleanup of temporary files and directories
- Test permission handling for output file creation

### Mocking Requirements

**Test Data Generation**
- Mock drilling_and_completion_days_by_api.xlsx with known test data
- Mock well_summ_goa_tiber.csv with corresponding test data
- Mock configuration files for reproducible test scenarios

**External Service Mocking**
- Mock file system operations for error condition testing
- Mock pandas Excel/CSV reading operations for exception testing
- Mock date/time functions for consistent test execution

## Test Data Requirements

### Baseline Test Dataset
- Minimum 5 wells with complete drilling and completion data
- Include wells with matching API12 numbers in both methods
- Include edge cases: wells with zero completion days, very high drilling days
- Include data quality scenarios: missing dates, invalid API12 formats

### Validation Scenarios
- **Perfect Match Scenario**: Both methods return identical results
- **Minor Difference Scenario**: Small variations within acceptable thresholds
- **Major Discrepancy Scenario**: Significant differences requiring investigation
- **Missing Data Scenario**: Wells present in one method but not the other

### Expected Test Outcomes
- Comparison test passes when API numbers can be matched between both methods
- Comparison test generates a markdown table with exactly 5 columns: API number, drilling days lease method, drilling days api12 method, completion days lease method, completion days api12 method
- Generated markdown report contains one row per API number with corresponding drilling and completion days from both methods
- Test validates that all required columns are present and properly formatted