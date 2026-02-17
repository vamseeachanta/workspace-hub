# Review Iteration 1

**Reviewer**: Architecture Specialist
**Date**: 2026-01-26

---

## Summary

The plan demonstrates solid research and a clear understanding of the target data sources. The phased approach with SODIR promotion first is pragmatic. However, there are several architectural inconsistencies, security gaps, and missing details that need to be addressed before implementation.

**Overall Assessment**: Needs revision before proceeding. Critical issues must be resolved.

---

## Critical Issues

### 1. Architecture Pattern Inconsistency (High Priority)

**Problem**: The proposed module structures do not consistently follow the established BSEE pattern.

**Evidence from existing codebase**:
- BSEE uses `bsee.py` with a `bsee` class containing `router(cfg)` method
- Data/Analysis components are separate classes (`BSEEData`, `BSEEAnalysis`)
- Configuration flows through the router: `cfg, data = bsee_data.router(cfg)`

**Issues in plan**:
- Texas RRC proposes `texas_rrc.py` as "Main router" but structure shows `api_client.py` separately - this is correct
- Mexico CNH proposes `api_client.py` for "Selenium-based client" which is a misnomer (Selenium is not an API)
- Landman `auth/api_key_manager.py` is proposed but no consistent auth pattern exists in BSEE

**Required Fix**:
```
# Each module MUST follow this pattern:
src/worldenergydata/modules/<module_name>/
├── __init__.py
├── <module_name>.py        # Main class with router() method
├── data/
│   └── <module>_data.py    # Data class with router() method
├── analysis/
│   └── <module>_analysis.py
├── errors.py               # NOT exceptions.py - follow SODIR pattern
└── validators.py
```

### 2. Engine.py Registration Pattern Not Documented (High Priority)

**Problem**: The plan mentions "Add routing in `engine.py`" but does not show the actual pattern.

**Current engine.py pattern**:
```python
if basename in ["bsee"]:
    bsee_app = bsee()
    cfg_base = bsee_app.router(cfg_base)
elif basename in ["dwnld_from_zipurl"]:
    # ...
```

**Required Addition**:
```python
elif basename in ["sodir"]:
    from worldenergydata.sodir.sodir import Sodir
    sodir_app = Sodir()
    cfg_base = sodir_app.router(cfg_base)
elif basename in ["texas_rrc"]:
    from worldenergydata.texas_rrc.texas_rrc import TexasRRC
    texas_app = TexasRRC()
    cfg_base = texas_app.router(cfg_base)
# ... etc for each module
```

### 3. Missing Exception Class Implementation Details (Medium-High Priority)

**Problem**: Plan says "Add to `src/worldenergydata/common/exceptions.py`" but doesn't show proper implementation.

**Required Pattern** (from existing `exceptions.py`):
```python
class TexasRRCError(ModuleError):
    """Texas RRC module-specific errors."""
    default_code = "TEXAS_RRC_ERROR"
    module_name = "texas_rrc"

class CanadaAERError(ModuleError):
    """AER module-specific errors."""
    default_code = "CANADA_AER_ERROR"
    module_name = "canada_aer"

# Note: Plan proposes CanadaBCERError - but should this be a separate
# module error or subclass of CanadaAERError? Architecture decision needed.
```

### 4. Selenium Dependency is Heavyweight and Risky (High Priority)

**Problem**: Adding `selenium` and `webdriver-manager` for Mexico CNH introduces:
- Large dependency footprint (Selenium alone is ~10MB)
- Browser driver version management complexity
- CI/CD complexity (Chrome/Chromium in containers)
- Potential for flaky tests due to browser automation

**Alternative Consideration**:
Before committing to Selenium, investigate:
1. Does CNH have undocumented API endpoints? (Check network tab in browser)
2. Can `requests-html` or `playwright` provide lighter alternatives?
3. Is the data available through third-party aggregators?

**If Selenium is required**, document:
- Docker configuration for CI
- Browser version pinning strategy
- Fallback behavior when scraping fails

---

## Recommendations

### 1. Add Protocol Implementation Requirements

Each new data source class should implement `DataSourceProtocol` from `types.py`:

```python
@runtime_checkable
class DataSourceProtocol(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def is_available(self) -> bool: ...
    def fetch(self, query: Dict[str, Any], **kwargs) -> DataFrameLike: ...
    def validate_query(self, query: Dict[str, Any]) -> bool: ...
```

**Action**: Add explicit protocol implementation to each module's data class.

### 2. Configuration File Location Clarification

Plan mentions `config/sodir.yml` but Glob shows no existing config files in that location. Clarify:
- Where do YAML configs actually go?
- Should they be in `src/worldenergydata/config/` or project root `config/`?
- Are configs loaded via environment or file path?

**Investigation needed**: Check how BSEE currently loads its configuration.

### 3. Credential Security for Landman Module

**Current plan states**: "API keys from environment variables only" - This is correct but incomplete.

**Required security additions**:
```python
# In auth/api_key_manager.py:
import os
from worldenergydata.common.exceptions import ConfigError

def get_api_key(provider: str) -> str:
    """
    Retrieve API key from environment.

    Raises:
        ConfigError: If key is not set or is empty
    """
    env_var = f"LANDMAN_{provider.upper()}_API_KEY"
    key = os.environ.get(env_var)
    if not key:
        raise ConfigError.missing_setting(env_var)
    return key
```

**Additional requirements**:
- Document all required environment variables in `.env.example`
- Add validation for key format where possible
- Consider supporting a secrets manager pattern for production

### 4. Add Rate Limiting Configuration Table

The comparison matrix shows rate limits but doesn't specify implementation:

| Source | Proposed Rate Limit | Backoff Strategy |
|--------|---------------------|------------------|
| Texas RRC | 5 req/sec | Exponential (2^n seconds) |
| Canada AER | 10 req/sec | Linear (n seconds) |
| Canada BCER | 10 req/sec | Linear |
| Mexico CNH | 1 req/sec* | Exponential + circuit breaker |
| Landman | Provider-specific | Per provider docs |

*CNH needs aggressive limiting due to dashboard fragility

### 5. Add Data Model Type Definitions

Extend `types.py` with regional identifier types:

```python
# Regional well identifiers
APINumber = str      # Existing: 10/12/14 digit US API
UWI = str           # Canadian: AA/BB-CC-DDD-EEFFGG/W
ClaveDelPozo = str  # Mexican: Well key identifier
NPDWellId = str     # Norwegian: SODIR well ID

# Unit conversion types
ImperialUnits = Literal["feet", "barrels", "mcf"]
MetricUnits = Literal["meters", "cubic_meters", "mscf"]
```

### 6. Cross-Regional Analysis Framework Needs More Detail

The proposed `cross_regional.py` is too vague:

```python
# Current proposal (insufficient):
compare_drilling_metrics()
benchmark_production()
normalize_identifiers()
convert_units()

# Required detail:
class CrossRegionalAnalysis:
    def compare_drilling_metrics(
        self,
        regions: List[str],
        metrics: List[str] = ["depth", "duration", "cost"],
        date_range: Optional[DateRange] = None,
        normalize_units: bool = True,
    ) -> DataFrame: ...

    def normalize_identifiers(
        self,
        identifier: str,
        source_format: str,  # "api", "uwi", "clave"
        target_format: str,
    ) -> str: ...
```

### 7. CLI Command Pattern Missing

Plan does not address CLI integration. Based on `bsee.py` CLI pattern:

```python
# Required: src/worldenergydata/cli/commands/sodir.py
# Required: src/worldenergydata/cli/commands/texas_rrc.py
# etc.

# Each should follow the BSEE pattern with Typer:
app = typer.Typer(name="sodir", help="SODIR data operations", no_args_is_help=True)

@app.command()
def collect(data_types: List[str] = ["wellbores"], ...): ...

@app.command()
def analyze(...): ...
```

---

## Approved Items

### 1. Phased Implementation Approach
Starting with SODIR promotion is correct - validates the pattern before new development.

### 2. SODIR Module Already Implements Correct Pattern
The existing `tests/modules/sodir-integration/sodir_module/` follows BSEE patterns well:
- `sodir.py` has `Sodir` class with `router()` method
- Separate `data.py`, `analysis.py` components
- Proper error classes in `errors.py`
- Validators separate from data logic

### 3. Data Source Comparison Matrix
Well-researched with appropriate auth, format, and complexity assessments.

### 4. Risk Matrix
Comprehensive coverage of key risks. Mitigations are appropriate.

### 5. UWI Parser for Canada
Good recognition that Canadian well identifiers need specialized parsing.

### 6. Testing Strategy Structure
Unit/Integration/Slow test separation is appropriate.

---

## Action Items Before Implementation

1. **[CRITICAL]** Update module structure diagrams to match BSEE pattern exactly
2. **[CRITICAL]** Document engine.py registration code for each module
3. **[CRITICAL]** Research CNH alternatives to Selenium before committing
4. **[HIGH]** Add exception class implementations to plan
5. **[HIGH]** Define CLI command structure for each module
6. **[MEDIUM]** Add protocol implementation requirements
7. **[MEDIUM]** Clarify configuration file locations and loading patterns
8. **[MEDIUM]** Expand cross-regional analysis API specification
9. **[LOW]** Add type definitions for regional identifiers

---

## Next Steps

After addressing critical issues:
1. Review iteration 2 should validate Selenium decision
2. Security review should focus on Landman credential handling
3. Performance review should assess memory for large Texas RRC datasets

---

**Review Status**: Requires revision
**Recommended**: Address Critical and High priority items, then request Review Iteration 2
