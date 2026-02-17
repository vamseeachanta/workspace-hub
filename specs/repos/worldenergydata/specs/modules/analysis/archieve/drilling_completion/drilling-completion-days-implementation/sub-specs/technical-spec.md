# Technical Specification

This is the technical specification for the spec detailed in @specs/modules/analysis/drilling-completion-days-implementation/spec.md

> Created: 2025-07-30
> Version: 1.0.0

## Technical Requirements

- **Custom Router Integration**: Modify `src\worldenergydata\modules\bsee\custom_router.py` to include routing logic for drilling and completion days analysis
- **Binary File Processing**: Update file paths in the existing class to use pickle binary files from `data\modules\bsee\bin\war\` directory
- **Configuration Management**: Create YAML configuration that integrates with the engine's "bsee_custom" basename routing
- **Excel Output Generation**: Ensure the existing Excel output functionality works without errors in the integrated framework
- **Lease Data Processing**: Maintain compatibility with the existing `tests\modules\bsee\analysis\leases.csv` input file
- **Framework Compliance**: Follow established patterns for logging, error handling, and configuration management

## Approach Options

**Option A:** Move the existing class to a new location and modify the custom router
- Pros: Minimal code changes, preserves existing tested logic, clear separation of concerns
- Cons: Creates duplicate code temporarily, requires careful import management

**Option B:** Create a new wrapper class that inherits from the existing class (Selected)
- Pros: Preserves existing functionality, enables framework integration, maintains backward compatibility, follows DRY principles
- Cons: Slightly more complex inheritance structure

**Option C:** Completely rewrite the class for the framework
- Pros: Clean integration, optimized for framework patterns
- Cons: High risk of introducing bugs, extensive testing required, time-intensive

**Rationale:** Option B provides the best balance of reliability and integration. The existing class already contains complex business logic that has been tested and validated. Creating a wrapper allows us to leverage this proven functionality while adding the necessary framework integration points.

## External Dependencies

- **No new dependencies required** - All functionality uses existing framework components
- **Existing dependencies used:**
  - pandas for data processing
  - loguru for logging
  - assetutilities for configuration management
  - openpyxl for Excel output (already in tech stack)

## Implementation Details

### File Structure Changes

```
src/worldenergydata/modules/bsee/
├── analysis/
│   └── drilling_completion_days.py  # New wrapper class
└── custom_router.py                 # Modified to include new routing

tests/modules/bsee/analysis/
├── drilling_completion_days_config.yml    # New configuration file
├── drilling_completion_days_test.py       # New test file
└── leases.csv                             # Existing file (no changes)
```

### Configuration File Paths

The YAML configuration will specify pickle binary file paths:
```yaml
filepath:
  leases: "tests/modules/bsee/analysis/leases.csv"
  war_files:
    main: "data/modules/bsee/bin/war/mv_war_main.bin"
    prop: "data/modules/bsee/bin/war/mv_war_main_prop.bin"
    remarks: "data/modules/bsee/bin/war/mv_war_main_prop_remark.bin"
    boreholes: "data/modules/bsee/bin/war/mv_war_boreholes_view.bin"
```

### Custom Router Integration

The custom router will be enhanced with:
```python
def router(self, cfg):
    if 'drilling_n_completion_days' in cfg and cfg['drilling_n_completion_days']['flag']:
        from worldenergydata.bsee.analysis.drilling_completion_days import DrillingCompletionDaysFramework
        drilling_analysis = DrillingCompletionDaysFramework()
        drilling_analysis.router(cfg)
    # ... existing routing logic
```

### Wrapper Class Design

The new wrapper class will:
1. Import and instantiate the existing `ExtractDrillingAndCompletionDays` class
2. Implement the standard `router(cfg)` method expected by the framework
3. Handle file path configuration from the YAML structure
4. Provide appropriate logging using the framework's logger
5. Delegate core processing to the existing proven implementation