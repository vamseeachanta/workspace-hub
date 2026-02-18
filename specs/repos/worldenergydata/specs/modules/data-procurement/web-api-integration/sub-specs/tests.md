# Tests Specification

This is the tests coverage details for the spec detailed in @specs/modules/data-procurement/web-api-integration/spec.md

> Created: 2025-09-01
> Version: 1.0.0

## Test Coverage

### Unit Tests

**APIClient Base Class**
- Test initialization with various configurations
- Test authentication header generation for different auth types
- Test request building with query parameters and headers
- Test response parsing for JSON, XML, and CSV formats
- Test error handling for network failures
- Test timeout and retry logic
- Test circuit breaker state transitions

**Response Transformer**
- Test JSON to DataFrame conversion
- Test XML parsing and transformation
- Test CSV parsing with various delimiters
- Test field mapping with configuration
- Test data type conversion and validation
- Test handling of missing fields with defaults
- Test nested JSON flattening

**Cache Manager**
- Test cache key generation from request parameters
- Test TTL-based expiration
- Test LRU eviction when cache is full
- Test cache invalidation patterns
- Test concurrent access and race conditions
- Test Redis connection failures with fallback
- Test cache statistics calculation

**Rate Limiter**
- Test token bucket algorithm
- Test rate limit enforcement
- Test burst handling
- Test per-API rate limit configuration
- Test rate limit headers parsing
- Test backoff calculation

### Integration Tests

**BSEE API Integration**
- Test production data retrieval with valid API numbers
- Test well data query with block filters
- Test lease data aggregation
- Test handling of BSEE-specific error codes
- Test pagination for large result sets
- Test data consistency across related endpoints
- Test fallback to cached data on API failure

**EIA API Integration**
- Test energy price series retrieval
- Test multiple series aggregation
- Test date range queries
- Test frequency conversion (daily to monthly)
- Test API key authentication
- Test rate limit compliance

**NOAA API Integration**
- Test weather data by coordinates
- Test historical data retrieval
- Test forecast data (if available)
- Test station-based queries
- Test data quality indicators

**Multi-Source Aggregation**
- Test combining BSEE production with EIA prices
- Test temporal alignment of different data sources
- Test handling of missing data from one source
- Test correlation calculations
- Test aggregation performance with large datasets

### Feature Tests

**End-to-End Data Retrieval**
```python
def test_complete_data_pipeline():
    """Test complete flow from API request to DataFrame output"""
    # 1. Request production data for specific well
    # 2. Verify API is called (or cache is used)
    # 3. Transform response to DataFrame
    # 4. Validate data schema and completeness
    # 5. Verify caching for subsequent request
    # 6. Test cache expiration and refresh
```

**API Failure Resilience**
```python
def test_api_failure_handling():
    """Test system behavior when external APIs fail"""
    # 1. Simulate BSEE API timeout
    # 2. Verify retry attempts with backoff
    # 3. Verify circuit breaker activation
    # 4. Verify fallback to cached data
    # 5. Test recovery when API comes back online
```

**Configuration Hot Reload**
```python
def test_configuration_updates():
    """Test adding new API without restart"""
    # 1. Add new API configuration
    # 2. Verify discovery of new endpoints
    # 3. Test immediate availability of new API
    # 4. Verify no disruption to existing APIs
```

### Performance Tests

**Load Testing**
- Test 100 concurrent API requests
- Measure cache hit rate under load
- Test memory usage with full cache
- Benchmark response times (p50, p95, p99)
- Test connection pool efficiency

**Stress Testing**
- Test behavior at rate limits
- Test with slow external APIs
- Test with intermittent network issues
- Test cache performance with 100K entries

### Mocking Requirements

**External API Responses**
- **VCR.py**: Record and replay HTTP interactions for consistent testing
- **Responses library**: Mock specific API scenarios (errors, timeouts)
- **WireMock**: For complex API behavior simulation in integration tests

**Time-based Tests**
- **freezegun**: Mock time for cache expiration tests
- **time-machine**: Test rate limiting over time periods

**Network Conditions**
- **pytest-timeout**: Test request timeout handling
- **socket mocking**: Simulate connection failures

## Test Data Sets

### Sample API Responses
```python
# BSEE Production Response
SAMPLE_BSEE_RESPONSE = {
    "result": {
        "records": [
            {
                "API_WELL_NUMBER": "177164011400",
                "PRODUCTION_DATE": "2024-01-01",
                "OIL_VOLUME": 15234.5,
                "GAS_VOLUME": 8923.2
            }
        ]
    }
}

# EIA Price Response
SAMPLE_EIA_RESPONSE = {
    "series": [
        {
            "series_id": "PET.RWTC.D",
            "data": [
                ["20240101", 73.25],
                ["20240102", 74.10]
            ]
        }
    ]
}
```

### Error Scenarios
```python
# API Error Responses
ERROR_SCENARIOS = {
    "rate_limit": {"status": 429, "message": "Rate limit exceeded"},
    "auth_failure": {"status": 401, "message": "Invalid API key"},
    "not_found": {"status": 404, "message": "No data found"},
    "server_error": {"status": 500, "message": "Internal server error"}
}
```

## Test Execution Strategy

### Test Organization
```
tests/modules/data_procurement/
├── unit/
│   ├── test_api_client.py
│   ├── test_transformer.py
│   ├── test_cache.py
│   └── test_rate_limiter.py
├── integration/
│   ├── test_bsee_api.py
│   ├── test_eia_api.py
│   ├── test_noaa_api.py
│   └── test_aggregation.py
├── feature/
│   ├── test_end_to_end.py
│   └── test_resilience.py
├── performance/
│   ├── test_load.py
│   └── test_stress.py
└── fixtures/
    ├── api_responses.json
    └── test_configs.yaml
```

### CI/CD Integration
- Run unit tests on every commit
- Run integration tests on pull requests
- Run performance tests nightly
- Generate coverage reports (target: &gt;90%)
- Fail builds if tests don't pass

### Test Environment Setup
```yaml
# test_env.yaml
test_apis:
  bsee:
    base_url: "http://mock-bsee:8080"
    api_key: "test_key_123"
  cache:
    redis_url: "redis://test-redis:6379"
    ttl_seconds: 60
```