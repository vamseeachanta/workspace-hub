# Tests Specification

This is the tests coverage details for the spec detailed in @specs/modules/data-sources/sodir-integration/spec.md

> Created: 2025-07-23
> Version: 1.0.0

## Test Coverage

### Unit Tests

**SodirAPIClient (sodir/data/api/client.py)**
- test_client_initialization - Verify client initializes with correct base URL and rate limits
- test_rate_limiting - Ensure requests are properly rate limited to 10/second
- test_get_request_success - Test successful API requests with proper response handling
- test_get_request_with_parameters - Test parameterized requests with query strings
- test_http_error_handling - Test handling of 400, 404, 429, 500 HTTP errors
- test_retry_logic - Verify exponential backoff retry for transient failures
- test_cache_hit - Test cache retrieval for repeated requests
- test_cache_miss - Test API call when cache is empty or expired

**BlockProcessor (sodir/data/processors/blocks.py)**
- test_process_raw_data_valid - Test processing of valid block JSON data to DataFrame
- test_process_raw_data_missing_fields - Test handling of JSON with missing required fields
- test_geometry_validation_valid_wkt - Test validation of valid WKT geometry strings
- test_geometry_validation_invalid_wkt - Test rejection of malformed WKT geometry
- test_coordinate_conversion - Test UTM to WGS84 coordinate transformation accuracy
- test_data_type_enforcement - Verify correct pandas data types after processing
- test_empty_dataset_handling - Test behavior with empty API response

**WellboreProcessor (sodir/data/processors/wellbores.py)**
- test_process_wellbore_data - Test conversion of wellbore JSON to structured DataFrame
- test_unit_conversion_meters_to_feet - Test depth unit conversions for imperial compatibility
- test_coordinate_transformation - Test Norwegian UTM zone conversions to WGS84
- test_status_normalization - Test mapping of Norwegian status codes to standardized values
- test_date_parsing_multiple_formats - Test parsing of various Norwegian date formats
- test_invalid_coordinate_handling - Test handling of coordinates outside valid ranges

**FieldProcessor (sodir/data/processors/fields.py)**
- test_field_data_processing - Test field data conversion with resource calculations
- test_resource_unit_conversion - Test conversion of oil/gas volumes to standard units
- test_production_date_validation - Test validation of production start dates
- test_operator_name_standardization - Test company name normalization
- test_missing_resource_data - Test handling of fields with incomplete resource data

**ConfigurationValidator (sodir/data/validators/)**
- test_valid_configuration - Test acceptance of properly formatted YAML configuration
- test_invalid_dataset_ids - Test rejection of unsupported dataset identifiers
- test_date_range_validation - Test validation of start/end date parameters
- test_missing_required_parameters - Test handling of configurations missing required fields
- test_configuration_defaults - Test application of default values for optional parameters

### Integration Tests

**End-to-End Data Collection**
- test_complete_blocks_workflow - Test full workflow from API call to processed CSV output
- test_complete_wellbores_workflow - Test wellbore data collection and processing pipeline
- test_multiple_dataset_collection - Test simultaneous collection of multiple data types
- test_large_dataset_handling - Test processing of datasets exceeding 10,000 records
- test_api_rate_limit_compliance - Test that bulk data collection respects rate limits
- test_data_persistence - Test that processed data is correctly saved to filesystem

**Cross-Regional Integration**
- test_sodir_bsee_data_combination - Test creation of combined SODIR-BSEE analysis datasets
- test_coordinate_system_compatibility - Test coordinate alignment between Norwegian and US data
- test_unified_analysis_pipeline - Test existing analysis tools work with SODIR data
- test_visualization_integration - Test SODIR data works with existing plotting functions

**Configuration Integration**
- test_yaml_configuration_loading - Test loading of SODIR configuration from YAML files
- test_configuration_override - Test user configuration overrides default settings
- test_environment_specific_config - Test different configurations for dev/test/prod environments
- test_configuration_validation_integration - Test configuration validation in full workflow

**Error Recovery Integration**
- test_partial_api_failure_recovery - Test system behavior when some API endpoints fail
- test_network_interruption_recovery - Test resumption of data collection after network issues
- test_invalid_data_filtering - Test removal of invalid records without stopping pipeline
- test_cache_corruption_recovery - Test system recovery from corrupted cache files

### Feature Tests

**Complete SODIR Data Collection Scenario**
- User configures YAML file requesting blocks, wellbores, and fields data for specific date range
- System authenticates with SODIR API and collects data respecting rate limits
- Data is processed, validated, and stored in CSV format with proper schemas
- Analysis tools can successfully load and analyze the collected Norwegian data
- Visualizations display Norwegian Continental Shelf data with correct geographic projections

**Cross-Regional Analysis Scenario**
- User requests comparative analysis between Norwegian and US Gulf of Mexico operations
- System loads both SODIR and BSEE datasets with compatible data structures
- Analysis pipeline combines datasets using common field mappings
- Visualization tools display side-by-side comparisons of drilling success rates
- NPV analysis tools work with Norwegian field economics data

**Large-Scale Data Processing Scenario**
- User requests complete historical dataset covering 10+ years of Norwegian data
- System processes request in chunks to manage memory usage
- Rate limiting prevents API overload during bulk data collection
- Progress monitoring provides feedback during long-running operations
- Final dataset contains validated, cleaned data ready for analysis

**Real-Time Data Update Scenario**
- User configures automatic daily data refresh for monitoring current operations
- System checks cache validity and only requests updated data
- New data is integrated with existing datasets maintaining data integrity
- Alert system notifies of significant changes in Norwegian operations
- Dashboard updates automatically with latest Norwegian Continental Shelf activity

### Mocking Requirements

**External API Services**
- **SODIR REST API:** Mock all endpoint responses (1001, 5000, 7100, 7000, 4000) with realistic Norwegian data
- **Strategy:** Use responses library to mock HTTP requests with configurable response scenarios
- **Test Data:** Include valid responses, error responses (400, 404, 429, 500), and edge cases

**File System Operations**
- **Cache Files:** Mock filesystem cache operations for predictable test environments
- **Strategy:** Use unittest.mock.patch for file I/O operations, temporary directories for integration tests
- **Configuration:** Mock YAML configuration loading to test various configuration scenarios

**Time-Based Operations**
- **Date/Time Functions:** Mock datetime.now() for consistent timestamp testing
- **Strategy:** Use freezegun library to freeze time for cache TTL and date range testing
- **Cache Expiry:** Test cache expiration logic with controlled time advancement

**Network Conditions**
- **Rate Limiting:** Mock network delays to test rate limiting behavior
- **Strategy:** Use time.sleep mocks and response delays to simulate rate limiting scenarios
- **Connection Failures:** Mock network timeouts and connection errors for resilience testing

**Geographic Coordinate Systems**
- **Coordinate Transformations:** Mock pyproj coordinate system transformations
- **Strategy:** Pre-calculate expected coordinate transformations for deterministic testing
- **Edge Cases:** Test coordinate conversion at Norwegian Continental Shelf boundaries

## Test Data Management

### Mock SODIR API Responses

**Blocks Test Data (1001 endpoint)**
```json
{
  "npdidBlock": 12345,
  "blockName": "30/11",
  "blockArea": 625.0,
  "blockStatus": "AWARDED",
  "blockGeometry": "POLYGON((2.5 60.5, 3.0 60.5, 3.0 61.0, 2.5 61.0, 2.5 60.5))",
  "allocationDate": "2020-01-15T00:00:00Z",
  "operatorCompany": "Equinor ASA"
}
```

**Wellbores Test Data (5000 endpoint)**
```json
{
  "npdidWellbore": 67890,
  "wellboreName": "30/11-1",
  "wellboreType": "EXPLORATION",
  "drillingOperator": "Equinor ASA",
  "spudDate": "2020-03-15T00:00:00Z",
  "totalDepth": 3500.0,
  "waterDepth": 120.0,
  "nsDeg": 60.75,
  "ewDeg": 2.75
}
```

### Test Configuration Files

**Valid SODIR Configuration (test_sodir_valid.yml)**
```yaml
basename: sodir
type:
  data: True
  analysis: False
parameters:
  datasets:
    - blocks
    - wellbores
    - fields
  date_range:
    start: "2020-01-01"
    end: "2020-12-31"
  output_format: csv
```

**Invalid Configuration for Error Testing (test_sodir_invalid.yml)**
```yaml
basename: sodir
type:
  data: True
parameters:
  datasets:
    - invalid_dataset
  date_range:
    start: "invalid-date"
```

## Continuous Integration Requirements

### GitHub Actions Integration
- Run all tests on Python 3.9, 3.10, 3.11 across Windows, macOS, Linux
- Execute tests in parallel where possible to optimize CI runtime
- Generate coverage reports using pytest-cov with minimum 85% coverage requirement
- Cache pip dependencies and mock data files to improve CI performance

### Pre-commit Hooks
- Run black code formatting check before allowing commits
- Execute isort import sorting validation
- Run ruff linting with project-specific rules
- Execute fast unit tests (< 30 seconds total) as pre-commit validation

### Performance Testing
- Benchmark API client performance with concurrent requests
- Memory usage profiling for large dataset processing
- Cache performance measurement with various cache sizes
- Integration test timing to ensure reasonable execution times (< 5 minutes total)

## Test Environment Setup

### Development Environment
- Use pytest fixtures for common test data and mock objects
- Implement teardown methods to clean temporary files and reset mocks
- Provide test data generators for creating realistic Norwegian petroleum data
- Use environment variables to configure test API endpoints and credentials

### CI/CD Environment  
- Configure test environment variables for GitHub Actions
- Use matrix testing for multiple Python versions and operating systems
- Implement artifact storage for test reports and coverage data
- Set up notifications for test failures and coverage regressions