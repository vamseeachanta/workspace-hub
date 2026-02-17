# API Research and Implementation Specification

This is the API research specification for the spec detailed in @specs/modules/bsee/data-refresh-architecture/spec.md

> Created: 2025-08-06
> Version: 1.0.0

## Primary Research Objective

**HARD RESEARCH REQUIRED:** Determine if BSEE offers any web APIs that can replace direct zip file downloads to eliminate the stale data problem and GitHub file size constraints.

## BSEE Data Sources to Research

### Primary Data Sources (Known)

**WELL_DATA (Application for Permit to Drill)**
- **Direct Link:** https://www.data.bsee.gov/Well/Files/APDRawData.zip
- **Update Frequency:** Daily
- **Size:** 100+ MB
- **Current Issue:** Stale data causing analysis variance

**PRODUCTION_DATA (Production Data)**
- **Direct Link:** https://www.data.bsee.gov/Production/Files/ProductionRawData.zip  
- **Update Frequency:** Bi-monthly
- **Size:** 100+ MB
- **Current Issue:** Stale data causing analysis variance

**WAR_DATA (eWell Submissions WAR)**
- **Direct Link:** https://www.data.bsee.gov/Well/Files/eWellWARRawData.zip
- **Update Frequency:** Daily
- **Size:** 100+ MB  
- **Current Issue:** Stale data causing analysis variance

### Main Portal Information
- **Portal:** https://www.data.bsee.gov/Main/RawData.aspx
- **Location:** Links appear in "Raw Data" column under "Delimited" button
- **Display Names:** Use specific names listed in "Online Query Name" column

## API Research Strategy

### Step 1: Developer Documentation Search
1. **Search for API Documentation:**
   - Check https://www.data.bsee.gov/ for developer/API sections
   - Look for `/api/`, `/developer/`, `/docs/` endpoints
   - Search site for terms: "API", "REST", "JSON", "developer", "programmatic access"

2. **Common Government API Patterns:**
   - Check for `api.bsee.gov` subdomain
   - Look for `/v1/`, `/v2/` version endpoints
   - Search for GraphQL endpoints
   - Check for OpenAPI/Swagger documentation

### Step 2: Web Interface Analysis
1. **Analyze Web Query Systems:**
   - Inspect network traffic when using web forms
   - Look for AJAX/JSON endpoints behind web interfaces
   - Check if web queries use REST-like endpoints internally

2. **Specific Areas to Investigate:**
   - Production data query interface: https://www.data.bsee.gov/Production/OCSProduction/Default.aspx
   - Well data interface: https://www.data.bsee.gov/Well/API/Default.aspx
   - Platform data interface: https://www.data.bsee.gov/Platform/PlatformStructures/Default.aspx

### Step 3: Government API Standards Check
1. **Federal API Standards:**
   - Check compliance with https://api.data.gov standards
   - Look for Data.gov catalog integration
   - Search Federal API registry

2. **Bureau Standards:**
   - Check other DOI (Department of Interior) APIs
   - Look for consistent API patterns across BSEE systems

## API Test Implementation Requirements

### If APIs Are Found
Create comprehensive test suite demonstrating:

1. **Authentication Testing:**
```python
def test_bsee_api_authentication():
    """Test API key/authentication if required"""
    # Test valid authentication
    # Test invalid authentication  
    # Test authentication renewal
```

2. **Data Retrieval Testing:**
```python
def test_well_data_api():
    """Test well data API access"""
    # Test basic data retrieval
    # Test date range filtering
    # Test pagination handling
    # Test response format validation

def test_production_data_api():
    """Test production data API access"""
    # Test bi-monthly data access
    # Test data freshness validation
    # Test large dataset handling

def test_war_data_api():
    """Test WAR data API access"""
    # Test daily data updates
    # Test data format consistency
```

3. **Integration Testing:**
```python
def test_api_vs_existing_binary_format():
    """Ensure API data matches existing binary format"""
    # Compare API data structure to existing pickle format
    # Test conversion compatibility
    # Validate data completeness
```

4. **Error Handling Testing:**
```python
def test_api_error_scenarios():
    """Test API error conditions and retry logic"""
    # Test rate limiting
    # Test network failures
    # Test malformed requests
    # Test service unavailability
```

## Fallback Implementation: Web Scraping

### If No APIs Exist
Implement web scraping solution with these specifications:

#### Direct File Access Strategy
```python
class BSEEDataScraper:
    """In-memory processing of BSEE data files"""
    
    URLS = {
        'well_data': 'https://www.data.bsee.gov/Well/Files/APDRawData.zip',
        'production_data': 'https://www.data.bsee.gov/Production/Files/ProductionRawData.zip',
        'war_data': 'https://www.data.bsee.gov/Well/Files/eWellWARRawData.zip'
    }
    
    def fetch_and_process(self, data_type, memory_limit=500_000_000):
        """Fetch zip file and process in-memory without local storage"""
        # Stream download without saving to disk
        # Extract and process data in memory
        # Output binary files using existing pickle format
        # Maintain compatibility with existing _from_zip modules
```

#### Integration Points with Existing Architecture
1. **Enhance `data_refresh.py`:**
   - Add API client fallback logic
   - Maintain existing flag-based processing (apm, production)
   - Preserve existing binary output format

2. **Maintain Existing Execution Path:**
   - Keep `tests/modules/bsee/data/refresh/data_refresh_test.py` as entry point
   - Preserve `engine.py` → `bsee.py` → `bsee_data.py` → `data_refresh.py` flow
   - Support existing YAML configurations

3. **Binary File Compatibility:**
   - Use existing pickle serialization in `_from_zip/well_data.py`
   - Use existing pickle serialization in `_from_zip/production_data.py`
   - Output to existing `data/modules/bsee/bin` directory

## Testing Requirements

### Research Documentation Test
```python
def test_api_research_documentation():
    """Document all findings from API research"""
    # Document what APIs were found (if any)
    # Document API endpoints, authentication, rate limits
    # Document why APIs were/weren't suitable
    # Provide recommendations for implementation
```

### Integration Test with Existing System
```python
def test_integration_with_existing_architecture():
    """Test new implementation with existing system"""
    # Test with existing config files
    # Test with existing test entry points
    # Validate binary file compatibility
    # Test flag-based processing (apm, production)
```

### Performance Comparison Test  
```python
def test_performance_vs_stale_data():
    """Compare new fresh data vs old stale data approach"""
    # Measure data freshness improvement
    # Compare analysis result variance
    # Document repository size impact
```

## Deliverable Specification

### Primary Deliverable: API Research Report
```markdown
# BSEE API Research Results

## Executive Summary
[Found APIs: Yes/No]
[Recommendation: API Implementation / Web Scraping Fallback]

## API Discovery Results
### APIs Found
- [List any APIs discovered with endpoints, documentation, limitations]

### APIs Not Found
- [Document areas searched, methods used, government API standards checked]

## Implementation Plan
[Detailed plan based on research results]

## Test Results
[Results of API tests if APIs were found]
```

### Secondary Deliverable: Implementation
- **If APIs found:** API client with comprehensive tests
- **If no APIs found:** In-memory web scraper maintaining existing architecture compatibility
- **Always:** Fresh data access eliminating "big variance" problem from stale zip files

## Quality Criteria

1. **Research Thoroughness:** Documentation of all BSEE web properties searched for APIs
2. **Test Coverage:** 100% test coverage if APIs are found, comprehensive integration tests
3. **Architecture Compatibility:** Zero breaking changes to existing execution paths and binary formats  
4. **Data Freshness:** Elimination of stale data problem causing analysis variance
5. **Repository Constraints:** No 100+ MB zip files stored in GitHub repository