# Tests Specification

This is the tests coverage details for the spec detailed in @specs/modules/bsee/financial-analysis-sme-code/spec.md

> Created: 2025-08-19
> Version: 1.0.0

## Test Coverage Requirements

Target coverage: >90% for all financial calculation modules

## Unit Tests

### FinancialAnalyzer Tests
**File:** `test_financial_analyzer.py`
- Test initialization with config file
- Test initialization with config dictionary
- Test analyze method with valid data
- Test analyze method with missing data
- Test error handling for invalid inputs
- Test results dictionary structure

### LeaseProcessor Tests
**File:** `test_lease_processor.py`
- Test lease grouping with valid mappings
- Test lease grouping with unmapped leases
- Test aggregation by group
- Test handling of empty DataFrames
- Test duplicate lease handling
- Test group name validation

### CashFlowCalculator Tests
**File:** `test_cash_flow_calculator.py`
- Test monthly cash flow calculation
- Test NPV calculation with various discount rates
- Test tax application
- Test handling of negative cash flows
- Test edge cases (zero production, zero prices)
- Test array dimension mismatches

### ReportGenerator Tests
**File:** `test_report_generator.py`
- Test workbook creation
- Test README sheet generation
- Test summary sheet creation
- Test lease group sheet creation
- Test Excel formatting application
- Test file writing permissions

### Validators Tests
**File:** `test_validators.py`
- Test input data validation
- Test configuration validation
- Test output validation
- Test data type checking
- Test range validation
- Test required columns validation

### Formatters Tests
**File:** `test_formatters.py`
- Test column width formatting
- Test number format application
- Test date format application
- Test header styling
- Test worksheet ordering

## Integration Tests

### End-to-End Analysis Tests
**File:** `test_integration_analysis.py`
- Test complete analysis pipeline with sample data
- Test multi-lease processing
- Test grouped analysis generation
- Test Excel output generation and validation
- Test configuration override handling

### Data Flow Tests
**File:** `test_integration_data_flow.py`
- Test data loading from Excel files
- Test data transformation pipeline
- Test calculation accuracy against known results
- Test output file structure validation

### Performance Tests
**File:** `test_integration_performance.py`
- Test processing 100+ leases within time limit
- Test memory usage under 2GB threshold
- Test parallel processing capabilities
- Test large dataset handling

## Feature Tests

### Financial Analysis Workflow
**File:** `test_feature_financial_workflow.py`
- Test analyst workflow from data load to report generation
- Test consultant workflow with multiple lease groups
- Test engineer workflow with automated processing
- Test error recovery and partial results

### Report Generation Workflow
**File:** `test_feature_report_generation.py`
- Test Excel report completeness
- Test formatting consistency
- Test README content accuracy
- Test multi-sheet workbook structure

## Test Data Requirements

### Sample Data Files
```
tests/modules/bsee/analysis/financial-analysis-sme-code/
├── fixtures/
│   ├── sample_exec_summary.xlsx
│   ├── sample_cf_debug.xlsx
│   ├── sample_lease_data.csv
│   ├── expected_output_v18.xlsx
│   └── config_test.yaml
```

### Test Data Characteristics
- Minimum 10 leases with varied characteristics
- At least 24 months of production data
- Mix of positive and negative cash flows
- Various drilling and completion cost scenarios
- Edge cases (zero production months, missing data)

## Mocking Requirements

### External Dependencies
- **File System:** Mock file I/O for unit tests
- **Excel Operations:** Mock openpyxl operations for speed
- **Date/Time:** Mock datetime for consistent test results

### Data Sources
- **Input Excel Files:** Use fixture files or mock DataFrames
- **Configuration Files:** Use test-specific YAML configurations
- **Output Paths:** Use temporary directories for test outputs

## Test Utilities

### Helper Functions
```python
# tests/modules/bsee/analysis/financial-analysis-sme-code/test_utils.py

def create_sample_lease_data(num_leases=10, num_months=24):
    """Generate sample lease data for testing."""
    
def create_sample_cash_flow_data(lease_name, months):
    """Generate sample cash flow data."""
    
def compare_excel_files(file1, file2, tolerance=0.01):
    """Compare two Excel files for testing."""
    
def validate_output_structure(excel_path):
    """Validate Excel output structure."""
```

### Test Fixtures
```python
@pytest.fixture
def sample_analyzer():
    """Create a configured FinancialAnalyzer instance."""
    
@pytest.fixture
def sample_lease_data():
    """Provide sample lease DataFrame."""
    
@pytest.fixture
def temp_output_dir():
    """Provide temporary directory for test outputs."""
```

## Continuous Integration

### Test Execution
```bash
# Run all tests for this spec
pytest tests/modules/bsee/analysis/financial-analysis-sme-code/ -v

# Run with coverage
pytest tests/modules/bsee/analysis/financial-analysis-sme-code/ --cov=worldenergydata.bsee.analysis.sme_financial --cov-report=html

# Run specific test categories
pytest tests/modules/bsee/analysis/financial-analysis-sme-code/ -m "unit"
pytest tests/modules/bsee/analysis/financial-analysis-sme-code/ -m "integration"
pytest tests/modules/bsee/analysis/financial-analysis-sme-code/ -m "not slow"
```

### Test Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Tests that take >1 second
- `@pytest.mark.requires_excel` - Tests requiring Excel files

## Validation Criteria

### Calculation Accuracy
- NPV calculations match expected values within 0.01%
- Cash flow calculations match manual calculations exactly
- Tax calculations follow specified rates accurately
- Aggregations sum correctly across groups

### Output Quality
- All required sheets present in Excel output
- Formatting applied consistently
- No data loss during processing
- Column headers match specification

### Performance Benchmarks
- Unit tests complete in <5 seconds total
- Integration tests complete in <30 seconds total
- Memory usage stays within specified limits
- No memory leaks detected

## Test Documentation

Each test file should include:
- Docstrings explaining test purpose
- Comments for complex test logic
- References to requirements being tested
- Expected vs actual comparisons

## Known Test Scenarios

### Success Cases
1. Standard multi-lease analysis
2. Single lease processing
3. Large dataset processing
4. Custom configuration override
5. Partial data availability

### Error Cases
1. Missing required columns
2. Invalid configuration
3. Corrupted input data
4. Insufficient permissions
5. Memory constraints exceeded

### Edge Cases
1. Zero production for all months
2. Single month of data
3. Extremely large NPV values
4. Negative prices
5. Missing lease in grouping