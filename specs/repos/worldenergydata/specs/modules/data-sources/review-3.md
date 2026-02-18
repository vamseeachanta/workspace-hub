# Review Iteration 3

**Reviewer**: DevOps & Maintainability Specialist
**Date**: 2026-01-26

## Summary

The implementation plan for multi-regional oil & gas well data integration is **well-structured** and demonstrates good alignment with existing codebase patterns. The phased approach is sound, particularly the "quick win" strategy of promoting the existing SODIR module first. However, there are several areas requiring attention around CI/CD impact, test organization, error handling consistency, and maintainability concerns that should be addressed before implementation proceeds.

**Overall Assessment**: Approved with mandatory revisions (see Critical Issues)

---

## Critical Issues

### 1. CI/CD Pipeline Impact Not Addressed

**Location**: Section 5 (Testing Strategy), Section 6 (Verification Plan)

**Issue**: The plan does not address how new modules will integrate with the existing CI/CD pipeline defined in `.github/workflows/ci.yml`. Specifically:

- The current CI runs `uv run pytest tests/` which will include all new module tests
- Selenium tests for Mexico CNH require Chrome/Chromium drivers not available in standard CI runners
- Landman API tests require credentials that should not be committed

**Required Actions**:
1. Add a dedicated `slow` or `integration` pytest marker for Selenium tests
2. Update CI workflow to exclude slow tests by default: `pytest --ignore=tests/modules/mexico_cnh/`
3. Create a separate nightly workflow for slow/integration tests
4. Document credential management via GitHub Secrets for Landman tests

**Suggested CI Configuration Addition**:
```yaml
# In .github/workflows/ci.yml, modify test step:
- name: Run tests with coverage
  run: |
    uv run pytest tests/ \
      --ignore=tests/modules/mexico_cnh/test_selenium*.py \
      -m "not slow and not integration" \
      -v --tb=short --cov=src
```

### 2. Error Hierarchy Inconsistency

**Location**: Section 4 (Configuration Changes - New Exception Classes)

**Issue**: The plan proposes adding `TexasRRCError`, `CanadaAERError`, etc. to `src/worldenergydata/common/exceptions.py`, but the existing SODIR module in `tests/modules/sodir-integration/sodir_module/errors.py` defines its own separate error hierarchy that is NOT integrated with `common/exceptions.py`.

**Current Exception Structure**:
```python
# common/exceptions.py
WorldEnergyDataError (base)
|-- ModuleError
    |-- BSEEError
    |-- SODIRError  # Exists but not used by SODIR test module
    |-- EIAError

# tests/modules/sodir-integration/sodir_module/errors.py (SEPARATE)
SodirError (standalone, not inheriting from ModuleError)
|-- SodirAPIError
|-- SodirConfigurationError
|-- SodirDataError
|-- SodirValidationError
|-- SodirRateLimitError
```

**Required Actions**:
1. During Phase 1 (SODIR Promotion), refactor SODIR errors to inherit from `ModuleError`
2. Create a standardized error template that all new modules follow
3. Ensure all module errors implement the `to_dict()` method from `WorldEnergyDataError`

**Suggested Error Template**:
```python
# src/worldenergydata/modules/<module>/errors.py
from worldenergydata.common.exceptions import ModuleError, DataError, APIError

class TexasRRCError(ModuleError):
    default_code = "TEXAS_RRC_ERROR"

class TexasRRCAPIError(TexasRRCError, APIError):
    default_code = "TEXAS_RRC_API_ERROR"

class TexasRRCValidationError(TexasRRCError, DataError):
    default_code = "TEXAS_RRC_VALIDATION_ERROR"
```

### 3. Test Directory Structure Inconsistency

**Location**: Section 5 (Testing Strategy), Section 6 (Verification Plan)

**Issue**: The verification commands reference `tests/modules/sodir/`, `tests/modules/texas_rrc/`, etc., but the existing test structure uses:
- `tests/unit/<module>/` for unit tests
- `tests/integration/` for integration tests
- `tests/modules/sodir-integration/` (non-standard location for SODIR)

**Required Actions**:
1. Standardize test locations:
   - `tests/unit/modules/<module>/` - Unit tests
   - `tests/integration/modules/<module>/` - Integration tests (API, Selenium)
   - Move SODIR tests from `tests/modules/sodir-integration/` to standard location during promotion
2. Update `conftest.py` to register pytest markers for `slow`, `integration`, `requires_credentials`

---

## Recommendations

### 1. Engine.py Routing Pattern Needs Update

**Location**: `src/worldenergydata/engine.py`

**Finding**: The current engine routing is simplistic with only `bsee` and `dwnld_from_zipurl` basenames. Adding 5 new modules will require either:
- A registry pattern for dynamic module discovery
- A configuration-driven approach

**Recommendation**: Implement a module registry pattern before Phase 2:
```python
MODULE_REGISTRY = {
    "bsee": ("worldenergydata.bsee.bsee", "bsee"),
    "sodir": ("worldenergydata.sodir.sodir", "Sodir"),
    "texas_rrc": ("worldenergydata.texas_rrc.texas_rrc", "TexasRRC"),
    # etc.
}

def engine(inputfile: str = None, cfg: dict = None, config_flag: bool = True) -> dict:
    # ... existing validation ...

    if basename in MODULE_REGISTRY:
        module_path, class_name = MODULE_REGISTRY[basename]
        module = importlib.import_module(module_path)
        instance = getattr(module, class_name)()
        cfg_base = instance.router(cfg_base)
    else:
        raise Exception(f"Analysis for basename: {basename} not found. ... FAIL")
```

### 2. CLI Command Pattern Standardization

**Location**: `src/worldenergydata/cli/commands/`

**Finding**: The existing CLI follows a Typer sub-application pattern. New modules should follow the same structure.

**Recommendation**: Create a CLI template in documentation:
```python
# src/worldenergydata/cli/commands/sodir.py (template)
app = typer.Typer(
    name="sodir",
    help="SODIR (Norwegian Offshore Directorate) data operations",
    no_args_is_help=True,
)

@app.command()
def collect(
    data_types: List[str] = typer.Option(["wellbores"], "--types", "-t"),
    output: Path = typer.Option(Path("./data/sodir"), "--output", "-o"),
):
    """Collect data from SODIR API."""
    pass

@app.command()
def stats():
    """Display SODIR data statistics."""
    pass
```

### 3. Configuration Management Enhancement

**Finding**: The plan places config files in `config/<module>.yml`, but the SODIR config in `tests/modules/sodir-integration/configs/sodir.yml` is comprehensive (248 lines). This level of detail is excellent.

**Recommendations**:
1. Create a `config/schemas/` directory with JSON Schema definitions for config validation
2. Add configuration validation to the module initialization
3. Consider environment-specific configs: `config/sodir.yml`, `config/sodir.dev.yml`, `config/sodir.ci.yml`

### 4. Dependency Management for Selenium

**Location**: Section 7 (Dependencies)

**Finding**: `selenium` and `webdriver-manager` are listed as "To Add" but the current `pyproject.toml` already includes `selenium>=4.15.0`.

**Recommendations**:
1. Verify `webdriver-manager` is actually needed (modern selenium has built-in driver management)
2. Add `selenium` to `[project.optional-dependencies]` as `scraping` group:
```toml
[project.optional-dependencies]
scraping = [
    "selenium>=4.15.0",
    # webdriver-manager not needed for selenium 4.6+
]
```
3. Document that Mexico CNH module requires `uv sync --extra scraping`

### 5. Documentation Gaps

**Location**: Throughout plan

**Recommendations**:
1. Add module-specific README.md to each module directory
2. Create data dictionary documentation for each region's identifier formats
3. Add architecture decision records (ADRs) for key design choices

---

## Approved Items

The following aspects of the plan are well-designed and approved without modification:

### 1. Phased Implementation Order
The sequence (SODIR -> Texas RRC -> Canada -> Mexico CNH -> Landman) is optimal because:
- SODIR promotion provides immediate value with minimal risk
- Texas RRC offers highest ROI (public data, large market)
- Canada integration builds on established REST/CSV patterns
- Mexico CNH (highest complexity) comes after team has experience
- Landman correctly scoped to free public records only

### 2. Module Structure Pattern
The proposed directory structure mirrors the existing BSEE pattern:
```
modules/<module>/
|-- __init__.py
|-- <module>.py           # Main router
|-- api_client.py         # HTTP/scraping client
|-- data/loaders/         # Data type-specific loaders
|-- processors/           # Data processors
|-- validators.py
|-- errors.py
```
This promotes consistency and reduces cognitive load.

### 3. Cross-Regional Analysis Framework
The `cross_regional.py` proposal with `normalize_identifiers()` and `convert_units()` is essential for multi-source data integration and addresses a real business need.

### 4. Risks & Mitigation Table
The risk assessment is comprehensive with appropriate mitigations:
- Rate limiting: Conservative limits, exponential backoff
- Dashboard changes: Page object pattern, version detection
- API key exposure: Environment variables only, audit logging

### 5. SODIR Configuration Quality
The existing SODIR configuration (`tests/modules/sodir-integration/configs/sodir.yml`) is production-ready with:
- Comprehensive API configuration
- Unit conversion specifications
- Error handling and retry logic
- Performance tuning options

---

## Implementation Checklist for Phase 1 (SODIR Promotion)

Before proceeding to Phase 2, ensure the following are completed:

1. [ ] Refactor SODIR errors to inherit from `ModuleError`
2. [ ] Move SODIR module from `tests/modules/sodir-integration/sodir_module/` to `src/worldenergydata/modules/sodir/`
3. [ ] Move tests to `tests/unit/modules/sodir/` and `tests/integration/modules/sodir/`
4. [ ] Update `src/worldenergydata/engine.py` with SODIR routing
5. [ ] Create CLI commands in `src/worldenergydata/cli/commands/sodir.py`
6. [ ] Register CLI in `src/worldenergydata/cli/main.py`
7. [ ] Move config to `config/sodir.yml`
8. [ ] Add pytest markers configuration to `pyproject.toml` or `pytest.ini`
9. [ ] Update CI workflow to handle slow tests
10. [ ] Verify all existing tests pass: `uv run pytest tests/modules/sodir-integration/ -v`

---

## Version Control Notes

Recommended branch strategy for this implementation:
```
feature/data-sources-integration (main feature branch)
|-- feature/sodir-promotion (Phase 1)
|-- feature/texas-rrc-integration (Phase 2)
|-- feature/canada-integration (Phase 3)
|-- feature/mexico-cnh-integration (Phase 4)
|-- feature/landman-integration (Phase 5)
```

Each phase should be a separate PR to allow incremental review and rollback if needed.

---

## Sign-off

**Reviewed Sections**:
- [x] Implementation order and phasing
- [x] Maintainability patterns
- [x] Documentation completeness
- [x] CI/CD integration impact
- [x] Error handling hierarchy
- [x] Test organization
- [x] Security considerations (Landman API keys)
- [x] Dependency management

**Disposition**: **Conditionally Approved**

The plan may proceed to implementation once Critical Issues 1-3 are addressed in the plan document. Recommendations should be incorporated as the implementation progresses.

---

**Next Steps**:
1. Update plan.md to address critical issues
2. Schedule Review Iteration 4 (Final approval)
3. Begin Phase 1 implementation

**Reviewer Notes**:
This plan reflects good understanding of the existing codebase architecture and demonstrates appropriate risk awareness. The main gaps are around operational concerns (CI/CD, test organization) rather than technical design, which is a positive indicator of implementation readiness.
