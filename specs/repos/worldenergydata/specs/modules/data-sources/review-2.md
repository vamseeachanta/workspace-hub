# Review Iteration 2

**Reviewer**: Data Engineering Specialist
**Date**: 2026-01-26
**Focus Areas**: Data model consistency, API integration patterns, rate limiting, data quality, cross-regional normalization

---

## Summary

The plan provides a comprehensive strategy for multi-regional oil and gas data integration. The modular architecture aligns well with existing codebase patterns (protocol-based interfaces, router patterns). However, several critical data engineering concerns require attention before implementation, particularly around identifier validation, retry/backoff strategies, and cross-regional data normalization.

**Overall Assessment**: **Conditionally Approved** - Address critical issues before Phase 2 begins.

---

## Critical Issues

### 1. API Number Format Specification is Incomplete

**Location**: Section 2.2 (Texas RRC Data Model)

**Problem**: The plan specifies API numbers as `42-XXX-XXXXX-XX-XX` but does not define:
- The full 14-digit format breakdown: `SS-CCC-WWWWW-SS-DD` (State-County-Well-Sidetrack-Directional)
- Validation regex pattern
- How to handle 10-digit vs 12-digit vs 14-digit API numbers
- Mapping between Texas RRC's format and BSEE's API10/API12 system

**Evidence**: The existing codebase in `src/worldenergydata/common/types.py` defines:
```python
APINumber = str  # API well number (10, 12, or 14 digits)
```

But there's no validation logic or format specification. The `production_api12.py` module uses API12 strings directly without parsing.

**Recommendation**:
```python
# Add to plan - API Number validation patterns
API_NUMBER_PATTERNS = {
    'api10': r'^\d{10}$',                           # SSCCWWWWWW
    'api12': r'^\d{12}$',                           # SSCCWWWWWWSS
    'api14': r'^\d{14}$',                           # SSCCWWWWWWSSDD
    'api_formatted': r'^\d{2}-\d{3}-\d{5}(-\d{2}){0,2}$'  # With dashes
}

# Texas state code must be 42
TEXAS_STATE_CODE = '42'
```

### 2. Canada UWI Format is Oversimplified

**Location**: Section 3A (Canada Integration)

**Problem**: The UWI format `AA/BB-CC-DDD-EEFFGG/W` is not correct. The actual Canadian Unique Well Identifier follows CAPP/PPDM standards:

- Full format: `LE/SS-LSD-MER-TWP-RGE-M`
- Example: `100/06-35-054-23W4/0` (Legal Subdivision location)
- Alternative BC format differs from Alberta format

**Recommendation**:
Add a dedicated `uwi_parser.py` as planned, but with complete format specification:
```python
# Alberta UWI (14+ characters)
# Format: LSD/SEC-TWP-RGE-MER/EV
# Example: 102/06-35-054-23W4/00

# BC UWI (NTS-based)
# Format: A-XXX-X/09X-X-XX
# Different from Alberta system
```

### 3. Mexico Identifier (Clave del Pozo) Lacks Specification

**Location**: Section 4 (Mexico CNH)

**Problem**: The plan mentions "Clave del Pozo" but provides no format specification. Mexican well identifiers follow PEMEX/CNH conventions that differ significantly from API numbers.

**Recommendation**:
Research and document the Mexican well identifier format:
```python
# Mexican Well Key (Clave del Pozo)
# Typical format: XXXX-NNNN or field-based naming
# Need to verify with actual CNH data samples
```

---

## Recommendations

### 1. Enhance Rate Limiting and Resilience Strategy

**Current State**: Plan mentions "conservative limits, exponential backoff" but lacks specifics.

**Existing Pattern** (from `bsee_web.py`):
```python
MAX_RETRIES = 5
RETRY_DELAY = 10  # Fixed delay
# Adaptive timeout increases by 50% per retry
adaptive_timeout = timeout * (1 + attempt * 0.5)
```

**Recommended Enhancement**:
```python
# Per-source rate limiting configuration
RATE_LIMITS = {
    'texas_rrc': {'requests_per_second': 2, 'burst': 5},
    'aer': {'requests_per_second': 5, 'burst': 10},
    'bcer': {'requests_per_second': 10, 'burst': 20},
    'cnh': {'requests_per_second': 1, 'burst': 2},  # Dashboard scraping - be conservative
}

# Exponential backoff with jitter (industry standard)
def calculate_backoff(attempt: int, base_delay: float = 1.0) -> float:
    return base_delay * (2 ** attempt) + random.uniform(0, 1)
```

**Rationale**: The SODIR implementation in `tests/modules/sodir-integration/sodir_module/api_client.py` already implements rate limiting with `min_interval`. This pattern should be standardized across all data sources.

### 2. Add Data Validation Pipeline

**Gap**: Plan lacks detailed data validation strategy post-collection.

**Existing Pattern** (from SODIR validators):
```python
class DataValidator:
    def validate_schema(self, data, schema) -> Tuple[bool, List[str]]
    def validate_types(self, data, type_schema) -> bool
    def validate_norwegian_coordinates(self, lat, lon) -> bool
```

**Recommendation**: Add region-specific validators to the plan:
```python
# Per-region validators
class TexasRRCValidator(DataValidator):
    TEXAS_LAT_MIN, TEXAS_LAT_MAX = 25.8, 36.5
    TEXAS_LON_MIN, TEXAS_LON_MAX = -106.6, -93.5

    def validate_api_number(self, api: str) -> bool
    def validate_district(self, district: str) -> bool  # 01-12, 7B, 7C, 8, 8A

class CanadaValidator(DataValidator):
    def validate_uwi(self, uwi: str) -> bool
    def validate_nad83_coordinates(self, lat, lon) -> bool
```

### 3. Cross-Regional Normalization Needs More Detail

**Location**: Section 3 (Cross-Regional Analysis Framework)

**Current**:
```python
├── normalize_identifiers()       # API, UWI, Clave del Pozo mapping
└── convert_units()               # Imperial/Metric standardization
```

**Recommendation**: Expand with explicit unit conversion functions:
```python
class UnitConverter:
    """Standardize units to SI (metric) or API standard."""

    # Depth conversions
    @staticmethod
    def feet_to_meters(feet: float) -> float:
        return feet * 0.3048

    # Volume conversions
    @staticmethod
    def barrels_to_cubic_meters(bbls: float) -> float:
        return bbls * 0.158987

    @staticmethod
    def mcf_to_cubic_meters(mcf: float) -> float:
        return mcf * 28.3168

    # Coordinate system transformations
    @staticmethod
    def utm_to_wgs84(easting, northing, zone, hemisphere='N') -> Tuple[float, float]:
        # Use pyproj for coordinate transformations
        pass
```

**Additional**: Plan should specify target coordinate reference system (recommend WGS84/EPSG:4326 for cross-regional compatibility).

### 4. Selenium Strategy for CNH Needs Hardening

**Location**: Section 4 (Mexico CNH)

**Concerns**:
- Selenium is fragile for production systems
- No headless browser configuration mentioned
- No page object pattern details
- Missing anti-detection measures

**Recommendation**:
```python
# config/mexico_cnh.yml
selenium:
  browser: chrome
  headless: true
  user_agent_rotation: true
  page_load_timeout: 60
  implicit_wait: 10
  explicit_wait: 30
  screenshot_on_failure: true
  retry_on_stale_element: 3

# Use page object pattern
class SIHDashboardPage:
    """Page object for CNH SIH dashboard."""
    def __init__(self, driver):
        self.driver = driver

    def navigate_to_well_search(self) -> None
    def search_by_clave(self, clave: str) -> None
    def export_to_excel(self) -> Path
```

### 5. Add Circuit Breaker Pattern for External APIs

**Gap**: No fault tolerance pattern for external service failures.

**Recommendation**:
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def fetch_aer_data(endpoint: str, params: Dict) -> Dict:
    """Fetch data with circuit breaker protection."""
    pass
```

---

## Approved Items

### 1. Module Structure

The proposed module structure aligns perfectly with existing BSEE patterns:
```
src/worldenergydata/modules/<region>/
├── __init__.py
├── <region>.py           # Main router
├── api_client.py         # HTTP client
├── data/loaders/
├── processors/
├── validators.py
└── errors.py
```

This matches the established pattern in `src/worldenergydata/modules/bsee/data/` and will ensure consistency.

### 2. Protocol-Based Design

The plan correctly identifies and commits to implementing:
- `DataSourceProtocol`
- `ProcessorProtocol`
- `ValidatorProtocol`

These protocols from `src/worldenergydata/common/types.py` provide a solid interface contract.

### 3. SODIR Promotion Strategy

The Phase 1 approach to promote existing SODIR code from `tests/modules/sodir-integration/` is correct. The implementation is mature with:
- Proper API client with rate limiting
- Comprehensive validators
- Coordinate system handling
- Caching infrastructure

### 4. Configuration-Driven Architecture

YAML configuration approach (`config/<module>.yml`) follows established patterns:
```yaml
module: texas_rrc
api:
  base_url: https://www.rrc.texas.gov
  rate_limit: 5
  cache_ttl: 86400
```

### 5. Testing Strategy

The three-tier testing approach (unit, integration, slow/optional) is appropriate:
- Unit tests for parsing and validation
- Integration tests with mocked responses
- Slow tests for actual Selenium/API interactions

### 6. Security Approach for Landman

API key management via environment variables with audit logging is the correct approach:
```python
├── auth/
    └── api_key_manager.py
```

---

## Action Items for Plan Update

| Priority | Item | Section to Update |
|----------|------|-------------------|
| **P0** | Add complete API number validation specification | Section 2.2 |
| **P0** | Correct and detail UWI format for Alberta/BC | Section 3A |
| **P0** | Research and document Clave del Pozo format | Section 4 |
| **P1** | Add per-source rate limiting configuration table | Section 2-5 |
| **P1** | Add data validation pipeline section | New Section |
| **P1** | Expand unit conversion specifications | Section 3 |
| **P2** | Add Selenium hardening configuration | Section 4 |
| **P2** | Document target CRS (WGS84 recommended) | Section 3 |
| **P3** | Consider circuit breaker pattern | Section 8 (Risks) |

---

## Questions for Plan Author

1. **Identifier Cross-Reference**: How will we handle wells that appear in multiple data sources? (e.g., a well near the Texas-Mexico border)

2. **Data Freshness Strategy**: What is the target data freshness for each source? SODIR offers daily updates but Texas RRC is monthly.

3. **Historical Data Scope**: How far back should we collect historical data? This impacts storage and initial load time significantly.

4. **Error Aggregation**: Should validation errors prevent record insertion or should we store data with quality flags?

---

## Next Steps

1. Address P0 critical issues before Phase 2 (Texas RRC) begins
2. Create identifier validation module during Phase 1 (SODIR promotion) as a shared utility
3. Document actual data samples from each source to validate format assumptions
4. Review updated plan in Iteration 3

---

**Reviewer Signature**: Data Engineering Specialist
**Review Status**: Conditionally Approved (Pending P0 Resolution)
