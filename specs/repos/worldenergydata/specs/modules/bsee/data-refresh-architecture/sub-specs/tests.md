# Tests Specification

This is the tests coverage details for the spec detailed in @specs/modules/bsee/data-refresh-architecture/spec.md

> Created: 2025-08-06
> Version: 1.0.0

## Test Coverage Requirements

### Primary Testing Objectives
1. **API Research Validation:** Comprehensive tests if BSEE APIs are discovered
2. **Existing Architecture Integration:** Zero breaking changes to current execution paths
3. **Data Freshness Validation:** Eliminate "big variance" problem from stale data
4. **Repository Constraints:** Ensure no 100+ MB files stored in repository

### Coverage Targets
- **API Tests:** 100% coverage if APIs are found
- **Integration Tests:** All existing execution paths maintained
- **Compatibility Tests:** Existing binary format preservation
- **Fresh Data Tests:** Data currency validation

## API Research Tests

### API Discovery Tests
```python
class TestBSEEAPIResearch:
    """Test suite for comprehensive BSEE API research"""
    
    def test_developer_documentation_search(self):
        """Test systematic search for API documentation"""
        search_urls = [
            "https://www.data.bsee.gov/api/",
            "https://www.data.bsee.gov/developer/", 
            "https://www.data.bsee.gov/docs/",
            "https://api.bsee.gov/",
        ]
        # Test each URL for API documentation
        # Document findings in research report
        
    def test_government_api_standards_check(self):
        """Check BSEE compliance with federal API standards"""
        # Check Data.gov catalog integration
        # Search Federal API registry
        # Test common government API patterns
        
    def test_web_interface_network_analysis(self):
        """Analyze web interfaces for hidden API endpoints"""
        interfaces_to_analyze = [
            "https://www.data.bsee.gov/Production/OCSProduction/Default.aspx",
            "https://www.data.bsee.gov/Well/API/Default.aspx",
            "https://www.data.bsee.gov/Platform/PlatformStructures/Default.aspx"
        ]
        # Inspect network traffic during form submissions
        # Look for AJAX/JSON endpoints
        # Document any REST-like endpoints found
```

### API Testing (If APIs Found)
```python
class TestBSEEAPIImplementation:
    """Test suite for BSEE API access (if APIs exist)"""
    
    def test_well_data_api_access(self):
        """Test API access for well data (APDRawData)"""
        # Test basic API connection
        # Test data retrieval and format
        # Compare to expected daily update frequency
        # Validate data structure vs existing pickle format
        
    def test_production_data_api_access(self):
        """Test API access for production data"""
        # Test production data API endpoints
        # Verify bi-monthly update availability
        # Test large dataset handling
        # Validate against existing binary format
        
    def test_war_data_api_access(self):
        """Test API access for WAR data"""
        # Test WAR data API endpoints
        # Verify daily update availability
        # Test data consistency and format
        
    def test_api_authentication_and_rate_limits(self):
        """Test API authentication and rate limiting"""
        # Test authentication requirements
        # Document rate limits and quotas
        # Test error handling for limit exceeded
        
    def test_api_data_freshness(self):
        """Validate API data is fresher than zip files"""
        # Compare API data timestamps to zip file contents
        # Verify elimination of stale data problem
        # Document freshness improvement
```

## Existing Architecture Integration Tests

### Execution Path Compatibility
```python
class TestExistingExecutionPath:
    """Test compatibility with existing architecture"""
    
    def test_data_refresh_test_entry_point(self):
        """Test existing test entry point still works"""
        # Execute: tests/modules/bsee/data/refresh/data_refresh_test.py
        # Verify execution path: engine.py → bsee.py → bsee_data.py → data_refresh.py
        # Ensure no breaking changes to test execution
        
    def test_yaml_config_compatibility(self):
        """Test existing YAML configurations work"""
        # Test data_refresh.yml (data: refresh, apm flags)
        # Test base_configs/bsee.yml (file paths)
        # Verify flag-based processing maintained (apm, production)
        
    def test_binary_output_compatibility(self):
        """Test binary file format compatibility"""
        # Test output to data/modules/bsee/bin
        # Verify pickle serialization format preserved
        # Test compatibility with downstream analysis modules
        
    def test_from_zip_module_integration(self):
        """Test integration with existing _from_zip modules"""
        # Test well_data.py integration with fresh data
        # Test production_data.py integration with fresh data
        # Verify existing processing logic works with new data sources
```

### Configuration Integration
```python
class TestConfigurationIntegration:
    """Test integration with existing configuration system"""
    
    def test_apm_flag_processing(self):
        """Test apm flag processing for well data"""
        # Test apm=true triggers well data processing
        # Test integration with _from_zip/well_data.py
        # Verify pickle dumping to bin folder
        
    def test_production_flag_processing(self):
        """Test production flag processing"""
        # Test production=true triggers production processing
        # Test integration with _from_zip/production_data.py
        # Verify pickle dumping maintains format
        
    def test_data_refresh_flag(self):
        """Test data refresh flag controls execution"""
        # Test data.refresh=true initiates refresh process
        # Test flag combinations (refresh + apm + production)
        # Verify existing logic flow maintained
```

## Web Scraping Fallback Tests (If No APIs)

### In-Memory Processing Tests
```python
class TestInMemoryDataProcessing:
    """Test in-memory processing of large files"""
    
    def test_well_data_zip_in_memory_processing(self):
        """Test processing APDRawData.zip in memory"""
        # Mock 100+ MB zip file download
        # Test in-memory extraction and processing
        # Verify no local zip file storage
        # Test memory usage stays within limits
        
    def test_production_data_zip_processing(self):
        """Test processing ProductionRawData.zip in memory"""
        # Test bi-monthly production data processing
        # Verify large file handling without disk storage
        # Test compatibility with existing production_data.py
        
    def test_war_data_zip_processing(self):
        """Test processing eWellWARRawData.zip in memory"""
        # Test daily WAR data processing
        # Verify in-memory processing capabilities
        # Test output to existing binary format
```

### Web Scraping Implementation Tests
```python
class TestBSEEWebScraper:
    """Test web scraper implementation for direct file access"""
    
    def test_direct_file_url_access(self):
        """Test access to known BSEE file URLs"""
        urls = {
            'well_data': 'https://www.data.bsee.gov/Well/Files/APDRawData.zip',
            'production_data': 'https://www.data.bsee.gov/Production/Files/ProductionRawData.zip',
            'war_data': 'https://www.data.bsee.gov/Well/Files/eWellWARRawData.zip'
        }
        # Test direct access to each URL
        # Verify file availability and size
        # Test download streaming capabilities
        
    def test_main_portal_link_validation(self):
        """Test links from main portal page"""
        # Test https://www.data.bsee.gov/Main/RawData.aspx
        # Verify "Delimited" button links to known URLs
        # Validate display names match expected values
        # Test link stability and availability
```

## Data Freshness and Quality Tests

### Stale Data Problem Resolution
```python
class TestDataFreshnessImprovement:
    """Test elimination of stale data causing analysis variance"""
    
    def test_fresh_vs_stale_data_comparison(self):
        """Compare fresh data access vs old zip files"""
        # Load old zip file data (if available)
        # Fetch fresh data via new implementation
        # Compare timestamps and record counts
        # Document variance reduction achieved
        
    def test_update_frequency_compliance(self):
        """Test data freshness matches BSEE update schedules"""
        # Test well data daily updates
        # Test production data bi-monthly updates  
        # Test WAR data daily updates
        # Verify data currency vs update schedules
        
    def test_analysis_variance_reduction(self):
        """Test reduction in analysis variance"""
        # Run same analysis with old vs new data
        # Measure variance in results
        # Document improvement in analysis consistency
```

### Repository Constraint Tests
```python
class TestRepositoryConstraints:
    """Test compliance with GitHub file size limits"""
    
    def test_no_large_file_storage(self):
        """Verify no 100+ MB files stored in repository"""
        # Test data processing without local zip storage
        # Verify repository size stays within GitHub limits
        # Test clean temp file handling
        
    def test_binary_file_size_optimization(self):
        """Test binary file sizes are reasonable"""
        # Test pickle file sizes are acceptable
        # Verify compression efficiency
        # Test binary files under reasonable size limits
```

## Integration and System Tests

### End-to-End Fresh Data Flow
```python
class TestEndToEndFreshDataFlow:
    """Test complete fresh data processing workflow"""
    
    def test_complete_refresh_workflow(self):
        """Test full refresh from source to binary output"""
        # Execute complete refresh process
        # Verify data flows through existing architecture
        # Test binary output in correct locations
        # Validate downstream module compatibility
        
    def test_git_bash_execution_compatibility(self):
        """Test execution via git bash environment"""
        # Test command execution in git bash
        # Verify output and error handling
        # Test path handling in git bash context
```

## Mocking and Test Data

### Mock BSEE Services
```python
@pytest.fixture
def mock_bsee_api_responses():
    """Mock API responses if APIs are found"""
    # Mock successful API responses
    # Mock error conditions and rate limits
    # Mock authentication scenarios

@pytest.fixture  
def mock_bsee_file_downloads():
    """Mock large file downloads"""
    # Create test zip files with realistic structure
    # Mock network conditions and interruptions
    # Test resumable download scenarios

@pytest.fixture
def sample_bsee_data():
    """Generate sample BSEE data for testing"""
    # Create well data samples
    # Create production data samples
    # Create WAR data samples
    # Match existing data structure formats
```

### Test Environment Setup
```python
class TestEnvironmentSetup:
    """Setup and teardown for test environments"""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self, tmp_path):
        """Setup isolated test environment"""
        # Create temporary data directories
        # Mock existing configuration files
        # Setup test binary output locations
        
    def test_cleanup_after_tests(self):
        """Verify proper cleanup after test execution"""
        # Test no temporary files left behind
        # Test no large files in test directories
        # Verify original system state restored
```

## Performance and Validation Tests

### Memory Usage Tests
```python
class TestMemoryUsage:
    """Test memory efficiency during large file processing"""
    
    def test_memory_usage_during_processing(self):
        """Monitor memory usage during 100+ MB file processing"""
        # Profile memory usage during processing
        # Verify memory stays within reasonable limits
        # Test garbage collection effectiveness
        
    def test_streaming_performance(self):
        """Test streaming performance vs full download"""
        # Compare streaming vs full download memory usage
        # Test processing speed with streaming
        # Verify data integrity with streaming approach
```

### Data Integrity Tests
```python
class TestDataIntegrity:
    """Test data integrity throughout processing pipeline"""
    
    def test_pickle_format_integrity(self):
        """Test pickle serialization maintains data integrity"""
        # Test round-trip pickle serialization
        # Verify data types preserved
        # Test compatibility with existing readers
        
    def test_cross_module_compatibility(self):
        """Test compatibility with existing analysis modules"""
        # Test binary files work with existing analysis code
        # Verify no breaking changes to data consumers
        # Test field names and structure compatibility
```

## Test Execution Strategy

### Test Categories
- **Research Tests:** API discovery and documentation (always run)
- **API Tests:** Only if APIs are found during research
- **Integration Tests:** Existing architecture compatibility (always run)  
- **Scraping Tests:** Only if no APIs found (fallback implementation)
- **Performance Tests:** Memory usage and data freshness validation

### CI/CD Integration
```yaml
# Test execution in GitHub Actions
- name: Run API Research Tests
  run: uv run pytest tests/api_research/ -v

- name: Run Integration Tests  
  run: uv run pytest tests/integration/ -v --cov

- name: Run Implementation Tests
  run: uv run pytest tests/implementation/ -v
  condition: based on API research results
```

## Success Criteria

1. **API Research:** Complete documentation of BSEE API availability
2. **Zero Breaking Changes:** All existing tests pass with new implementation  
3. **Data Freshness:** Demonstrable reduction in analysis variance
4. **Repository Compliance:** No large files stored, memory-efficient processing
5. **Architecture Compatibility:** Seamless integration with existing execution paths