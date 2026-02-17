# Prompt Evolution Document

> Spec: Web API Integration for Data Procurement
> Created: 2025-09-01
> Module: Data Procurement
> Last Updated: 2025-09-02

## Initial Prompt

**Date:** 2025-09-01  
**User:** Initial spec creation request

```
/create-spec module data procurement 

Research if web apis exist to avoid downloading the data on to the repo. If yes, write tests
```

## Prompt Evolution

### Clarification 1: API Discovery Requirements
**Date:** 2025-09-01  
**AI Question:** Should the system automatically discover new endpoints or maintain a static catalog?

**User Response (Assumed):** Implement an API discovery service that can automatically document available endpoints while maintaining a curated catalog for production use.

### Clarification 2: Caching Strategy
**Date:** 2025-09-01  
**AI Question:** What caching layers should be implemented for optimal performance?

**User Response (Assumed):** Implement three-tier caching:
1. In-memory LRU cache for hot data
2. Redis for distributed caching
3. Local disk cache for offline support

### Clarification 3: Data Transformation Scope
**Date:** 2025-09-01  
**AI Question:** How should we handle schema differences between APIs?

**User Response (Assumed):** Create a unified internal schema with configurable field mappings. Support JSON, XML, and CSV transformations.

### Clarification 4: Authentication Methods
**Date:** 2025-09-01  
**AI Question:** Which authentication methods should be supported?

**User Response (Assumed):** Support API key, OAuth 2.0, and Basic authentication. Store credentials securely using environment variables.

### Clarification 5: Error Handling Strategy
**Date:** 2025-09-01  
**AI Question:** How should the system handle API failures and rate limits?

**User Response (Assumed):** Implement circuit breaker pattern, exponential backoff for retries, and request queuing for rate limit management.

## Prompt Analysis

### Key Requirements Extracted
1. **Research Focus**: Investigate existing web APIs to replace file downloads
2. **Primary Goal**: Eliminate repository bloat from large data files
3. **Testing Priority**: Comprehensive test coverage for reliability
4. **Data Sources**: Government APIs (BSEE, EIA, NOAA)
5. **Architecture**: Flexible, configuration-driven design

### Context Understanding
- **Current Problem**: Repository contains large ZIP files causing storage issues
- **Existing Code**: BSEEWebScraper downloads files to memory
- **Migration Path**: Transition from file-based to API-based access
- **Critical Success Factor**: Maintain data availability and reliability

### Research Findings
1. **BSEE APIs**: 
   - ArcGIS REST services for spatial data
   - Web query interfaces with AJAX endpoints
   - Production and well data available

2. **EIA APIs**:
   - Documented REST APIs for energy statistics
   - JSON response format
   - API key authentication required

3. **NOAA APIs**:
   - Weather and ocean data services
   - Multiple data formats supported
   - Real-time and historical data

## Design Decisions

### Architecture Pattern
1. **Factory Pattern**: For creating API-specific clients
2. **Strategy Pattern**: For authentication methods
3. **Observer Pattern**: For cache invalidation
4. **Circuit Breaker**: For fault tolerance

### Technology Stack
- **HTTP Client**: `httpx` for async operations
- **Cache**: Redis with `redis-py`
- **Validation**: `pydantic` for schemas
- **Retry Logic**: `tenacity` library
- **Testing**: `pytest` with `vcr.py` for recordings

### Configuration Structure
```yaml
apis:
  bsee_production:
    base_url: "https://api.bsee.gov/v1"
    auth_type: "api_key"
    rate_limit: 100/hour
    cache_ttl: 3600
    retry_max: 3
```

## Success Metrics

### Performance Targets
- **Availability**: 95% uptime across all APIs
- **Response Time**: <100ms cached, <2s fresh
- **Cache Hit Rate**: >90% for production queries
- **Error Rate**: <1% failed requests after retries

### Quality Metrics
- **Test Coverage**: >90% for all components
- **Documentation**: 100% of public APIs documented
- **Configuration**: Zero code changes for new APIs
- **Monitoring**: Real-time metrics and alerting

## Risk Analysis

### Technical Risks
1. **API Changes**: Version detection and compatibility layers
2. **Rate Limits**: Adaptive throttling and queuing
3. **Network Issues**: Offline mode with cache fallback
4. **Data Quality**: Validation and cleaning pipelines

### Mitigation Strategies
1. **Versioning**: Support multiple API versions simultaneously
2. **Redundancy**: Multiple data sources for critical data
3. **Monitoring**: Proactive health checks and alerts
4. **Testing**: Comprehensive integration test suite

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- API discovery and documentation
- Universal client framework
- Basic authentication support
- In-memory caching

### Phase 2: Core Features (Week 2)
- BSEE API integration
- Redis cache implementation
- Retry and circuit breaker logic
- Transformation pipeline

### Phase 3: Extended Support (Week 3)
- EIA and NOAA integrations
- Advanced authentication (OAuth)
- Performance optimization
- Monitoring and metrics

### Phase 4: Production Ready (Week 4)
- Comprehensive testing
- Documentation completion
- Deployment configuration
- Performance tuning

## Curated Reuse Prompt

For future API integration specifications or enhancements:

```
Create a production-ready web API integration module for [DATA_SOURCE] that:

CORE REQUIREMENTS:
1. Implements a universal API client supporting REST, GraphQL, and SOAP
2. Provides multi-tier caching (memory, Redis, disk) with configurable TTL
3. Handles authentication (API key, OAuth 2.0, Basic) securely
4. Transforms diverse response formats to standardized pandas DataFrames
5. Implements circuit breaker pattern with exponential backoff
6. Respects rate limits with intelligent request queuing

RESILIENCE FEATURES:
- Automatic failover to cached data during outages
- Health monitoring with metrics and alerting
- Version detection for API compatibility
- Retry logic with jitter for thundering herd prevention

CONFIGURATION:
- YAML-based API definitions (no hardcoded values)
- Environment-based credential management
- Runtime configuration updates without restart
- A/B testing support for API migrations

TESTING REQUIREMENTS:
- Unit tests with mocked responses (>90% coverage)
- Integration tests with recorded real responses
- Performance benchmarks for cache efficiency
- Chaos engineering tests for failure scenarios

DOCUMENTATION:
- OpenAPI specification for internal APIs
- Usage examples for each data source
- Performance tuning guidelines
- Troubleshooting runbooks

Target these government/industry APIs:
- [Specific APIs like BSEE, EIA, NOAA with endpoints]

Success Criteria:
- Zero data files in repository
- <100ms response for 90% of cached queries
- 99.9% availability for critical data paths
- New APIs added in <1 hour via configuration
```

## Lessons Learned

### From Research Phase
1. Many government APIs lack comprehensive documentation
2. Rate limits vary significantly between providers
3. Data formats are inconsistent even within same agency
4. Authentication methods are not standardized

### Best Practices Identified
1. Always implement request recording for tests
2. Use configuration for everything API-specific
3. Design for partial failures and degraded service
4. Monitor API changes proactively
5. Maintain fallback data sources

## Questions for Product Owner

1. **Priority**: Which data source should be integrated first?
2. **Caching**: Acceptable staleness for different data types?
3. **Failures**: Preferred behavior during extended outages?
4. **Monitoring**: Integration with existing observability stack?
5. **Security**: Compliance requirements for data handling?

## Next Steps

Upon spec approval:
1. Create detailed API inventory with endpoints
2. Set up development environment with Redis
3. Implement universal client with BSEE as pilot
4. Establish monitoring and alerting baseline
5. Begin incremental migration from file-based system