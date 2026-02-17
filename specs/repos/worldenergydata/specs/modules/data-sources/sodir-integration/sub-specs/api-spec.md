# API Specification

This is the API specification for the spec detailed in @specs/modules/data-sources/sodir-integration/spec.md

> Created: 2025-07-23
> Version: 1.0.0

## SODIR REST API Integration

### Base Configuration

**Base URL:** https://factmaps.sodir.no/api/rest
**Authentication:** None required (public API)
**Rate Limiting:** 10 requests/second (conservative estimate)
**Content-Type:** application/json
**Response Format:** JSON

### Dataset Endpoints

#### GET /api/rest/1001 - Block Data

**Purpose:** Retrieve Norwegian Continental Shelf block information including licensing, allocation, and geographic boundaries
**Parameters:** 
- `startdate` (optional): Filter by allocation start date (YYYY-MM-DD)
- `enddate` (optional): Filter by allocation end date (YYYY-MM-DD)
- `format`: json (default)
**Response:** JSON array of block objects with properties:
- `npdidBlock`: Unique block identifier
- `blockName`: Block name (e.g., "30/11")
- `blockArea`: Block area in square kilometers
- `blockStatus`: Current status (Open, Awarded, etc.)
- `blockGeometry`: WKT geometry definition
**Errors:** 
- 400: Invalid date format
- 404: No blocks found for criteria
- 429: Rate limit exceeded

#### GET /api/rest/5000 - Wellbore Data

**Purpose:** Retrieve wellbore drilling information including status, depths, and completion details
**Parameters:**
- `npdidWellbore` (optional): Specific wellbore ID
- `npdidBlock` (optional): Filter by block ID
- `wellboreStatus` (optional): Filter by status (DRILLING, COMPLETED, ABANDONED)
**Response:** JSON array of wellbore objects with properties:
- `npdidWellbore`: Unique wellbore identifier
- `wellboreName`: Wellbore name
- `wellboreType`: Type (EXPLORATION, DEVELOPMENT, etc.)
- `drillingOperator`: Operating company
- `spudDate`: Drilling start date
- `totalDepth`: Total depth in meters
- `waterDepth`: Water depth in meters
- `nsDeg`, `ewDeg`: Coordinates in decimal degrees
**Errors:**
- 400: Invalid wellbore ID or status
- 404: Wellbore not found
- 429: Rate limit exceeded

#### GET /api/rest/7100 - Field Data

**Purpose:** Retrieve field information including discovery dates, operators, and resource estimates
**Parameters:**
- `npdidField` (optional): Specific field ID
- `operator` (optional): Filter by operator company
- `fieldStatus` (optional): Filter by development status
**Response:** JSON array of field objects with properties:
- `npdidField`: Unique field identifier
- `fieldName`: Field name
- `fieldOperator`: Current operator
- `discoveryDate`: Date of discovery
- `fieldStatus`: Development status
- `recoverableOil`: Recoverable oil in million Sm³
- `recoverableGas`: Recoverable gas in billion Sm³
**Errors:**
- 400: Invalid field ID or operator
- 404: Field not found
- 429: Rate limit exceeded

#### GET /api/rest/7000 - Discovery Data

**Purpose:** Retrieve discovery information including geological formations and reserve classifications
**Parameters:**
- `npdidDiscovery` (optional): Specific discovery ID
- `discoveryYear` (optional): Filter by discovery year
**Response:** JSON array of discovery objects with properties:
- `npdidDiscovery`: Unique discovery identifier
- `discoveryName`: Discovery name
- `discoveryYear`: Discovery year
- `mainArea`: Main geological area
- `hydrocarbon`: Primary hydrocarbon type (OIL, GAS, OIL/GAS)
- `resourceClass`: Resource classification
**Errors:**
- 400: Invalid discovery ID or year
- 404: Discovery not found
- 429: Rate limit exceeded

#### GET /api/rest/4000 - Survey Data

**Purpose:** Retrieve survey information including seismic surveys and geological studies
**Parameters:**
- `surveyType` (optional): Type of survey (2D_SEISMIC, 3D_SEISMIC, etc.)
- `acquisitionYear` (optional): Filter by acquisition year
**Response:** JSON array of survey objects with properties:
- `npdidSurvey`: Unique survey identifier
- `surveyName`: Survey name
- `surveyType`: Type of survey
- `acquisitionYear`: Year of acquisition
- `surveyCompany`: Company conducting survey
- `surveyArea`: Survey area coverage
**Errors:**
- 400: Invalid survey type or year
- 404: Survey not found
- 429: Rate limit exceeded

## Internal API Design

### Client Class (sodir/data/api/client.py)

#### SodirAPIClient

**Purpose:** Centralized HTTP client for all SODIR API interactions with rate limiting and caching

```python
class SodirAPIClient:
    def __init__(self, base_url: str, rate_limit: int = 10)
    def get(self, endpoint: str, params: dict = None) -> dict
    def get_blocks(self, **kwargs) -> List[dict]
    def get_wellbores(self, **kwargs) -> List[dict]
    def get_fields(self, **kwargs) -> List[dict]
    def get_discoveries(self, **kwargs) -> List[dict]
    def get_surveys(self, **kwargs) -> List[dict]
```

**Rate Limiting:** Token bucket implementation with 10 tokens/second refill rate
**Error Handling:** Automatic retry with exponential backoff for 429, 500, 502, 503 responses
**Caching:** Filesystem cache with 24-hour default TTL

### Data Processing Classes

#### BlockProcessor (sodir/data/processors/blocks.py)

**Purpose:** Process raw block data from SODIR API into standardized format

```python
class BlockProcessor:
    def __init__(self, config: dict)
    def process_raw_data(self, raw_blocks: List[dict]) -> pd.DataFrame
    def validate_geometry(self, wkt_string: str) -> bool
    def convert_coordinates(self, geometry: str) -> dict
```

**Key Methods:**
- `process_raw_data`: Convert JSON to DataFrame with data type enforcement
- `validate_geometry`: Ensure WKT geometry strings are valid
- `convert_coordinates`: Transform UTM coordinates to WGS84 decimal degrees

#### WellboreProcessor (sodir/data/processors/wellbores.py)

**Purpose:** Process wellbore data with unit conversions and status normalization

```python
class WellboreProcessor:
    def __init__(self, config: dict)
    def process_raw_data(self, raw_wellbores: List[dict]) -> pd.DataFrame
    def convert_units(self, df: pd.DataFrame) -> pd.DataFrame
    def normalize_status(self, status: str) -> str
```

## Router Integration

### Main Router (sodir/sodir.py)

**Purpose:** Main entry point following BSEE architecture pattern

```python
class sodir:
    def __init__(self)
    def router(self, cfg: dict) -> dict
```

**Integration Pattern:**
1. Initialize data collection classes
2. Process configuration parameters
3. Route to appropriate data processors
4. Return updated configuration with results

### Data Router (sodir/data/sodir_data.py)

**Purpose:** Orchestrate data collection from multiple SODIR endpoints

```python
class SodirData:
    def __init__(self)
    def router(self, cfg: dict) -> Tuple[dict, dict]
```

**Workflow:**
1. Parse configuration for requested data types
2. Initialize API client with rate limiting
3. Collect data from specified endpoints
4. Process and validate collected data
5. Return configuration and collected datasets

## Error Handling Strategy

### HTTP Errors
- **400 Bad Request:** Log error and skip invalid requests
- **401/403 Unauthorized/Forbidden:** Retry once, then fail with authentication error
- **404 Not Found:** Return empty dataset with warning
- **429 Rate Limited:** Exponential backoff retry (1s, 2s, 4s, 8s, 16s)
- **500/502/503 Server Errors:** Retry with exponential backoff, max 5 attempts

### Data Validation Errors
- **Invalid Geometry:** Log warning and exclude invalid records
- **Missing Required Fields:** Log error and exclude incomplete records
- **Date Parsing Errors:** Attempt multiple formats, exclude if all fail
- **Coordinate Conversion Errors:** Log error and use original coordinates with warning

### Configuration Errors
- **Invalid Dataset IDs:** Raise ConfigurationError with available options
- **Missing API Configuration:** Use defaults with warning
- **Invalid Date Ranges:** Raise ValueError with format requirements