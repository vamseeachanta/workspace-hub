# Technical Specification

This is the technical specification for the spec detailed in @specs/modules/data-sources/sodir-integration/spec.md

> Created: 2025-07-23
> Version: 1.0.0

## Technical Requirements

### SODIR REST API Integration
- Implement HTTP client for factmaps.sodir.no/api/rest endpoint with proper authentication handling
- Rate limiting implementation to respect API usage limits (maximum 10 requests per second based on typical Norwegian government API patterns)
- Comprehensive error handling for HTTP status codes (400, 401, 403, 404, 429, 500, 503)
- Response caching mechanism using filesystem-based cache with configurable TTL
- Request retry logic with exponential backoff for transient failures

### Data Type Support 
- Blocks data collection (dataset ID: 1001) including licensing, allocation dates, and geographic boundaries
- Wellbores data retrieval (dataset ID: 5000) covering drilling parameters, status, and completion details
- Fields data processing (dataset ID: 7100) with discovery dates, operators, and resource estimates
- Discoveries data integration (dataset ID: 7000) including geological formations and reserve classifications
- Surveys data collection (dataset ID: 4000) covering seismic surveys, geological studies, and acquisition parameters
- Facilities data retrieval including platforms, FPSOs, and subsea infrastructure

### Data Processing Framework
- JSON to pandas DataFrame conversion with automatic data type inference
- Coordinate system transformation from Norwegian UTM zones to WGS84 decimal degrees
- Date parsing for multiple Norwegian date formats (ISO 8601, DD.MM.YYYY, DD/MM/YYYY)
- Unit conversion from metric to imperial units for cross-regional compatibility
- Data validation using pandas data profiling and custom validation rules

### Configuration System
- YAML-based configuration following existing BSEE patterns in src/worldenergydata/base_configs/modules/
- Parameterized data collection with configurable dataset selection, date ranges, and geographic filters
- Environment-specific settings for development, testing, and production deployments
- User-customizable output formats and file paths

## Approach Options

**Option A:** Mirror BSEE Architecture Exactly
- Pros: Consistent with existing codebase patterns, leverages proven architecture, minimal learning curve
- Cons: May not optimize for SODIR API-specific characteristics, REST-focused vs file-based patterns

**Option B:** REST-Native Architecture with BSEE Integration Points (Selected)
- Pros: Optimized for REST API patterns, better performance for real-time data, cleaner separation of concerns
- Cons: Requires adaptation of existing analysis tools, some architectural divergence

**Option C:** Unified API Architecture Refactor  
- Pros: Future-proofs for additional API integrations, creates reusable components
- Cons: Significant refactoring of existing BSEE code, extended development timeline

**Rationale:** Option B balances optimization for SODIR's REST API architecture while maintaining integration points with existing BSEE analysis capabilities. This approach enables efficient data collection from SODIR while reusing proven analysis and visualization components.

## External Dependencies

### HTTP and API Libraries
- **requests** (already present) - HTTP client for REST API communication
- **urllib3** (already present) - Low-level HTTP connection management
- **Justification:** Standard Python HTTP libraries for reliable API communication with connection pooling and retry capabilities

### Data Processing Libraries  
- **pandas** (already present) - DataFrame operations for data manipulation and analysis
- **numpy** (already present) - Numerical operations for coordinate transformations and calculations
- **pyproj** - Coordinate system transformations between Norwegian UTM and WGS84
- **Justification:** pyproj is the standard library for geodetic transformations, essential for converting Norwegian coordinate systems

### Caching and Performance
- **diskcache** - Persistent filesystem caching for API responses
- **Justification:** Provides simple, reliable caching to reduce API calls and improve performance during development and analysis

### Configuration and Validation
- **pyyaml** (already present) - YAML configuration file processing  
- **jsonschema** - JSON response validation against SODIR API schemas
- **Justification:** jsonschema ensures data integrity and provides early detection of API response changes

## Architecture Design

### Module Structure
```
src/worldenergydata/modules/sodir/
├── sodir.py                    # Main router following BSEE pattern
├── data/
│   ├── sodir_data.py          # Main data collection orchestrator
│   ├── api/
│   │   ├── client.py          # HTTP client with rate limiting
│   │   ├── endpoints.py       # API endpoint definitions
│   │   └── auth.py            # Authentication handling
│   ├── processors/
│   │   ├── blocks.py          # Block data processing
│   │   ├── wellbores.py       # Wellbore data processing
│   │   ├── fields.py          # Field data processing
│   │   ├── discoveries.py     # Discovery data processing
│   │   └── surveys.py         # Survey data processing
│   └── validators/
│       ├── data_quality.py    # Data validation rules
│       └── schemas.py         # Response schema definitions
└── analysis/
    ├── sodir_analysis.py      # Analysis integration point
    └── cross_regional.py      # SODIR-BSEE comparison tools
```

### Configuration Structure  
```
src/worldenergydata/base_configs/modules/sodir/
└── sodir.yml                  # Main configuration file

data/modules/sodir/
├── cache/                     # API response cache
├── raw/                       # Raw JSON responses
└── processed/                 # Processed CSV/Excel files
```

### Integration Points
- Leverage existing visualization tools in src/worldenergydata/modules/bsee/analysis/
- Reuse NPV analysis framework for Norwegian field economics
- Integrate with existing YAML configuration patterns
- Utilize established testing patterns with pytest framework

## Performance Considerations

### API Rate Limiting
- Implement connection pooling for efficient HTTP connections
- Batch requests where possible to minimize API calls
- Use conditional requests (If-Modified-Since headers) for unchanged data

### Memory Management
- Process large datasets in chunks to prevent memory overflow
- Implement lazy loading for data that may not be needed
- Use generators for streaming data processing

### Caching Strategy
- Cache API responses for 24 hours by default (configurable)
- Implement cache invalidation for real-time analysis needs
- Store processed data in compressed formats to reduce disk usage