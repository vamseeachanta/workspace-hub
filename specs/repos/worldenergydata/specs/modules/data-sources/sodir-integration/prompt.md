# Prompt Evolution Document

> Spec: SODIR Integration
> Created: 2025-07-23
> Module: data-sources
> Last Updated: 2025-09-02

## Initial Prompt

**Date:** 2025-07-23  
**User:** Initial spec creation request

```
Create a comprehensive integration with SODIR (Norwegian Offshore Directorate) data sources to expand WorldEnergyData's geographical coverage from US Gulf of Mexico to include Norwegian Continental Shelf operations. This should enable cross-regional analysis between BSEE and SODIR data.
```

## Prompt Evolution

### Update 1: Define Data Types and API Integration
**Date:** 2025-07-23  
**User:** Technical specification refinement

```
The SODIR integration should use the factmaps.sodir.no/api/rest endpoint and support multiple data types:
- Blocks (1001) - Norwegian Continental Shelf block allocations and licensing
- Wellbores (5000) - Drilling data including trajectories and completion details  
- Fields (7100) - Production field information and resource estimates
- Discoveries (7000) - New discovery data and evaluation results
- Surveys (4000) - Seismic and geological survey metadata
- Facilities - Infrastructure and installation data

Implement proper rate limiting (10 requests/second) and caching strategy.
```

### Update 2: Configuration System Requirements
**Date:** 2025-07-23  
**User:** Integration pattern alignment

```
Follow the existing BSEE module patterns for consistency:
- Use YAML configuration files for data collection parameters
- Match the data storage structure (data/modules/sodir/)
- Implement similar routing architecture through sodir.py main module
- Create processors for each data type similar to BSEE processors
```

### Update 3: Cross-Regional Analysis Features
**Date:** 2025-07-23  
**User:** Analysis capabilities expansion

```
Enable cross-regional comparative analysis between SODIR and BSEE:
- Normalize data formats for compatibility
- Support production comparison between regions
- Enable drilling metrics comparison
- Integrate with existing NPV analysis tools
- Add visualization support for Norwegian Continental Shelf maps
```

### Update 4: Data Processing Requirements
**Date:** 2025-07-23  
**User:** Technical processing details

```
Implement comprehensive data processing:
- Coordinate system conversion from UTM to WGS84
- Unit conversions between metric and imperial systems
- Data validation and quality assurance
- Temporal alignment for cross-regional time series
- Handle Norwegian-specific field naming conventions
```

## Curated Reuse Prompt

For future enhancements or similar integrations:

```
Implement a comprehensive data source integration for [DATA_SOURCE] following the WorldEnergyData module architecture pattern. 

Requirements:
1. API Integration:
   - Connect to [API_ENDPOINT] with proper authentication
   - Implement rate limiting ([RATE_LIMIT])
   - Add caching mechanism with [TTL] expiry
   - Handle all HTTP status codes and implement retry logic

2. Data Types Support:
   - [List all data types with their IDs/endpoints]
   - Create processor classes for each data type
   - Implement data validation and normalization

3. Configuration System:
   - YAML-based configuration in base_configs/modules/[module]/
   - Support flexible parameter selection
   - Enable batch processing configurations

4. Data Processing:
   - Coordinate system transformations if needed
   - Unit conversions for cross-system compatibility
   - Data quality validation
   - Temporal alignment for time series data

5. Storage Structure:
   - Follow data/modules/[module]/ pattern
   - Organize by data type and temporal granularity
   - Support both raw and processed data storage

6. Analysis Integration:
   - Compatible with existing analysis tools
   - Support cross-regional comparisons with [OTHER_SOURCES]
   - Enable visualization and reporting capabilities

7. Testing Requirements:
   - Unit tests for all components
   - Integration tests for API interactions
   - Data validation tests
   - Performance tests for large datasets

Follow existing module patterns from BSEE implementation for consistency.
```

## Key Decisions and Rationale

1. **API Architecture**: REST-based integration chosen for stability and comprehensive documentation
2. **Caching Strategy**: 24-hour TTL filesystem cache to reduce API load while maintaining data freshness
3. **Data Normalization**: Convert all coordinates to WGS84 and provide dual unit support (metric/imperial)
4. **Module Pattern**: Follow BSEE architecture for consistency and maintainability
5. **Cross-Regional Focus**: Design for comparative analysis from the start rather than retrofitting

## Success Criteria

- Successfully collect all SODIR data types through configuration
- Achieve >95% data validation pass rate
- Enable seamless cross-regional analysis between SODIR and BSEE
- Maintain API rate limits without failures
- Provide comprehensive test coverage (>90%)