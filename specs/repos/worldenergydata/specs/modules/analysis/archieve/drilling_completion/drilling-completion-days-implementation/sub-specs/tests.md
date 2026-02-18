# Tests Specification

This is the tests coverage details for the spec detailed in @specs/modules/analysis/drilling-completion-days-implementation/spec.md

> Created: 2025-07-30
> Version: 1.0.0

## Test Coverage

### Unit Tests

**DrillingCompletionDaysFramework Class**
- Test router method accepts valid configuration
- Test router method handles missing configuration gracefully
- Test file path validation and error handling
- Test configuration parsing from YAML structure

**CustomRouter Class Enhancement**
- Test routing condition detects drilling_n_completion_days flag correctly
- Test routing skips drilling analysis when flag is False
- Test routing handles missing drilling_n_completion_days configuration
- Test integration with existing custom analysis routing

### Integration Tests

**End-to-End Workflow**
- Test complete workflow from YAML configuration to Excel output
- Test engine routing with "bsee_custom" basename to custom router
- Test custom router routing to drilling completion days analysis
- Test binary file reading from data/modules/bsee/bin/war directory
- Test lease data processing from tests/modules/bsee/analysis/leases.csv
- Test Excel file generation in configured output directory

**File Processing Integration**
- Test pickle binary file loading (mv_war_main.bin, mv_war_main_prop.bin, mv_war_main_prop_remark.bin, mv_war_boreholes_view.bin)
- Test lease CSV file processing integration
- Test output Excel file structure and content validation
- Test error handling for missing or corrupted binary files

### Feature Tests

**Drilling and Completion Days Analysis**
- Test complete analysis produces expected Excel output with correct columns (API_WELL_NUMBER, WELL_NAME, WELL_SPUD_DATE, TOTAL_DEPTH_DATE, DRILLING_DAYS, COMPLETION_DAYS)
- Test analysis results match expected data types and formats
- Test analysis handles edge cases (missing dates, gaps in data)

**Configuration Management**
- Test YAML configuration parsing through framework
- Test file path resolution for relative and absolute paths
- Test output directory creation and file writing permissions

## Mocking Requirements

- **File System Operations:** Mock file existence checks and permissions for test isolation
- **Binary File Content:** Mock pickle file loading to provide controlled test data
- **Excel File Writing:** Mock Excel output operations to verify correct data structure without actual file creation
- **Logger Operations:** Mock loguru logger to capture and verify log messages during testing

## Test Data Requirements

### Test Binary Files
- Create minimal test versions of WAR binary files with known data for validation
- Include edge cases: wells with gaps in drilling, wells with missing completion data
- Ensure test data covers the lease numbers in the test leases.csv file

### Expected Output Structure
- Define expected Excel file structure with sample data
- Create validation rules for data types, date formats, and calculations
- Establish baseline comparison files for regression testing

## Test Execution Strategy

1. **Unit Tests First:** Validate individual components work correctly in isolation
2. **Integration Tests:** Verify components work together through the framework
3. **End-to-End Tests:** Validate complete user workflow from configuration to output
4. **Regression Tests:** Compare outputs with baseline results to ensure consistency

## Performance Tests

- **Memory Usage:** Verify analysis completes within reasonable memory constraints when processing large WAR datasets
- **Processing Time:** Establish baseline processing times for standard lease sets
- **File I/O Efficiency:** Monitor binary file reading performance compared to CSV processing