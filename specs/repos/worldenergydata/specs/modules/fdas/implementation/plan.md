# FDAS Implementation Plan
**Author:** Analysis Team
**Date:** 2025-10-03
**Source:** `/home/vamsee/Downloads/FDAS_V30`
**Target:** WorldEnergyData Repository

## Executive Summary

Roy's latest FDAS code represents a complete financial analysis system for deepwater field development. This plan outlines integration into the WorldEnergyData repository with proper alignment to BSEE data structures.

## Source Code Analysis

### Core Files Identified

1. **`generate_financial_summary.py`** (474 lines)
   - Main financial calculation engine
   - NPV/MIRR calculations using Excel-like methodology
   - Development system-specific assumptions (dry-tree, subsea15, subsea20)
   - Host CAPEX, D&C costs, OPEX, revenue modeling

2. **`build_multi_year_lease_matrix1.py`** (548 lines)
   - OGORA production data processing
   - WAR mapping integration
   - Multi-year monthly pivot tables
   - Water production tracking
   - Supports headerless OGORA txt files and zipped data

3. **`ogora_to_chronological.py`** (346 lines)
   - Chronological lease analysis builder
   - Reads raw OGORA zip files
   - Monthly production long-form output
   - D&C and WTI integration

4. **`extract_drilling_completion_days.py`** (381 lines)
   - Drilling and completion days extraction
   - WAR data integration
   - Completion activity detection from remarks
   - Gap-adjusted drilling calculations

### Key Dependencies

```python
# Core dependencies found in FDAS
- pandas >= 1.5.0
- numpy >= 1.20.0
- openpyxl >= 3.0.0
- xlsxwriter >= 3.0.0
```

### Input File Requirements

**Required Files:**
1. `leases.xlsx` - Lease mapping (LEASE_NAME, DEV_NAME, DEV_SYSTEM)
2. `lease_assumptions.xlsx` - Development system assumptions
3. `chronological_lease_analysis.xlsx` - Monthly production by API
4. `drilling_and_completion_days.xlsx` - D&C timeline data
5. `wti_monthly.xlsx` - WTI price deck

**OGORA Files (Optional for production):**
- `ogora20??delimit.zip` - Historical OGORA production data
- WAR files: `mv_war_main*.txt`, `mv_war_boreholes_view*.txt`

## Integration Architecture

### Phase 1: Core Module Structure

```
src/worldenergydata/modules/fdas/
├── __init__.py
├── config.py                      # Configuration management
├── assumptions.py                 # Load lease_assumptions.xlsx
├── production.py                  # Production data processing
├── drilling.py                    # D&C calculations
├── pricing.py                     # WTI and price deck handling
├── financial.py                   # NPV/MIRR core engine
├── cashflow.py                    # Monthly cashflow modeling
└── reports.py                     # Excel workbook generation
```

### Phase 2: BSEE Data Mapping

**Current BSEE Structure → FDAS Requirements:**

| BSEE File | FDAS Equivalent | Mapping Notes |
|-----------|-----------------|---------------|
| `well_data.csv` | `mv_war_main.txt` | API_WELL_NUMBER, lease mapping |
| `well_activity_summary.csv` | `mv_war_boreholes_view.txt` | Spud dates, TD dates |
| `well_activity_remarks.csv` | `mv_war_main_prop_remark.txt` | Completion activity detection |
| `production.csv` | `chronological_lease_analysis.xlsx` | Monthly oil/water volumes |

**Key Translation Logic:**

```python
# BSEE → FDAS Lease Mapping
bsee_lease_map = {
    'LEASE_NUMBER': 'SURF_LEASE_NUM',  # e.g., G09868
    'COMPLEX_ID_NUMBER': 'DEV_NAME',    # Field/development name
    'API_WELL_NUMBER': 'API_WELL_NUMBER',  # Direct mapping
}

# Development System Classification
def classify_dev_system(water_depth, complex_name):
    """
    Classify development system for assumptions lookup
    Returns: 'dry', 'subsea15', or 'subsea20'
    """
    if water_depth is None:
        return 'unknown'
    if water_depth < 500:
        return 'dry'
    elif water_depth < 6000:
        return 'subsea15'
    else:
        return 'subsea20'
```

### Phase 3: Financial Assumptions Adapter

**Create BSEE-compatible assumptions structure:**

```python
# Template: lease_assumptions.xlsx structure
DEFAULT_ASSUMPTIONS = {
    'DEV_SYSTEM': ['dry', 'subsea15', 'subsea20'],
    'HOST_CAPEX_MM': [0, 300, 450],  # Million USD
    'SURF_PER_WELL_MM': [0, 8, 12],
    'MODU_LOADED_DAYRATE_MM': [0.6, 0.8, 1.0],
    'DRY_TREE_RIG_RATE_MM': [0.5, 0.5, 0.5],
    'ROYALTY_RATE': [0.125, 0.188, 0.188],
    'VARIABLE_OPEX_$/BBL': [8, 12, 15],
    'FIXED_OPEX_MM_PER_YEAR': [10, 25, 40],
    'DISCOUNT_RATE_ANNUAL': [0.10, 0.10, 0.10],
    'WTI_BASE_$/BBL': [75, 75, 75],
}
```

## Implementation Tasks

### Task 1: Create FDAS Module Foundation
**Priority:** High
**Effort:** 3 days

- Create module directory structure
- Port `assumptions.py` from `load_assumptions_fixed()`
- Port `financial.py` core NPV/MIRR functions
- Add comprehensive unit tests

**Deliverables:**
- `src/worldenergydata/modules/fdas/` with core files
- `tests/modules/fdas/test_financial.py`
- Configuration schema validation

### Task 2: BSEE Data Adapter
**Priority:** High
**Effort:** 5 days

- Create BSEE → FDAS data transformation layer
- Build production aggregation pipeline
- Implement D&C extraction from BSEE activities
- Water depth classification for dev systems

**Deliverables:**
- `src/worldenergydata/modules/fdas/adapters/bsee_adapter.py`
- Conversion utilities in `common/converters/`
- Integration tests with real BSEE data

### Task 3: Production Data Processing
**Priority:** High
**Effort:** 4 days

- Port monthly aggregation logic
- Integrate with existing BSEE production pipeline
- Add first oil detection
- Producer/injector well counting

**Deliverables:**
- `src/worldenergydata/modules/fdas/production.py`
- Production summary generators
- Monthly pivot functionality

### Task 4: Drilling & Completion Timeline
**Priority:** Medium
**Effort:** 4 days

- Port D&C days calculation
- Integrate completion activity detection
- Gap-adjusted drilling timeline
- Month-by-month allocation logic

**Deliverables:**
- `src/worldenergydata/modules/fdas/drilling.py`
- Activity classification from remarks
- Timeline visualization tools

### Task 5: Cashflow Engine
**Priority:** High
**Effort:** 5 days

- Port monthly cashflow calculation
- CAPEX timing (host, facilities, D&C)
- OPEX (fixed and variable)
- Revenue and royalty calculations
- NPV/MIRR with Excel-compatible formulas

**Deliverables:**
- `src/worldenergydata/modules/fdas/cashflow.py`
- Financial summary generation
- Development-specific assumption lookup

### Task 6: Report Generation
**Priority:** Medium
**Effort:** 3 days

- Excel workbook generation with openpyxl
- Project summary sheet formatting
- Per-development detail sheets
- Number formatting and column widths

**Deliverables:**
- `src/worldenergydata/modules/fdas/reports.py`
- Template-based report builders
- Export to multiple formats (Excel, CSV, JSON)

### Task 7: Integration Testing
**Priority:** High
**Effort:** 3 days

- End-to-end pipeline tests
- Golden baseline validation (compare against FDAS reference)
- Performance benchmarking
- Edge case handling

**Deliverables:**
- `tests/integration/fdas/test_end_to_end.py`
- Golden reference comparison utilities
- Performance regression tests

### Task 8: Documentation
**Priority:** Medium
**Effort:** 2 days

- User guide for FDAS module
- API documentation
- Configuration examples
- Financial methodology documentation

**Deliverables:**
- `docs/modules/fdas/user-guide.md`
- `docs/modules/fdas/financial-methodology.md`
- API reference with docstrings

## BSEE Input File Changes Required

### 1. Add Development System Classification

**New Column: `well_data.csv`**
```csv
API_WELL_NUMBER,COMPLEX_ID_NUMBER,WATER_DEPTH,DEV_SYSTEM
...
608054011700,Anchor,7500,subsea20
608054012100,Julia,7000,subsea15
```

**Logic:**
```python
def add_dev_system_to_well_data():
    """Add DEV_SYSTEM classification based on water depth"""
    well_data = pd.read_csv('data/modules/bsee/current/wells/well_data.csv')
    well_data['DEV_SYSTEM'] = well_data['WATER_DEPTH'].apply(
        lambda d: 'subsea20' if d > 6000 else 'subsea15' if d > 500 else 'dry'
    )
    well_data.to_csv('data/modules/bsee/current/wells/well_data.csv', index=False)
```

### 2. Create Lease Mapping File

**New File: `data/modules/bsee/current/leases/lease_mapping.csv`**
```csv
LEASE_NUMBER,LEASE_NAME,DEV_NAME,DEV_SYSTEM,WATER_DEPTH
G09868,Mississippi Canyon 941,Anchor,subsea20,7500
G09964,Green Canyon 19,Julia,subsea15,7000
G32306,Walker Ridge 758,Jack,subsea15,7000
G32635,Walker Ridge 678,St. Malo,subsea15,6800
```

### 3. Enhance Production Data

**Modification: `production.csv`**
- Add `DEV_NAME` column from complex ID lookup
- Add `LEASE_NAME` from lease mapping
- Ensure `MONTHLY_OIL_VOLUME` and `MONTHLY_WATER_VOLUME` present

### 4. Completion Activity Enhancement

**Modification: `well_activity_remarks.csv`**
- Parse remarks for completion keywords (existing in extract_drilling_completion_days.py)
- Extract mud weight from remarks text
- Classify activity type (drilling, completion, testing)

### 5. Create Assumptions Configuration

**New File: `data/modules/fdas/config/default_assumptions.xlsx`**
- Port structure from FDAS `lease_assumptions.xlsx`
- Include all development system parameters
- Document assumption sources and rationale

## Migration Path

### Option A: Parallel Systems (Recommended)
**Timeline:** 4-6 weeks

1. Build FDAS module alongside existing BSEE code
2. Create BSEE adapter for data translation
3. Validate against golden baseline
4. Gradual migration of analyses

**Pros:**
- No disruption to existing code
- Comprehensive testing before cutover
- Can compare outputs side-by-side

**Cons:**
- Temporary code duplication
- Requires more storage/compute

### Option B: In-Place Refactor
**Timeline:** 6-8 weeks

1. Refactor existing BSEE code to match FDAS structure
2. Update all downstream consumers
3. Migrate tests

**Pros:**
- Single codebase
- Forces cleanup of legacy code

**Cons:**
- Higher risk of breaking changes
- Longer testing cycle

## Validation Strategy

### Golden Baseline Comparison

Use FDAS reference workbook: `V30_Golden_Baseline_Reference_Full_With_AfterTax.docx`

**Comparison Metrics:**
1. NPV values (±1% tolerance due to floating point)
2. MIRR annual/monthly values (±0.1% tolerance)
3. Total cashflow sums
4. D&C cost totals
5. Facilities CAPEX totals

**Test Case:**
```python
def test_anchor_field_matches_golden_baseline():
    """Compare Anchor field results against V30 golden baseline"""
    fdas_result = run_fdas_analysis(
        lease_name='Mississippi Canyon 941',
        dev_name='Anchor'
    )

    golden = load_golden_baseline('V30_Golden_Baseline_Reference')
    anchor_baseline = golden[golden['Project Name'] == 'Anchor']

    assert_allclose(fdas_result['NPV_USD'],
                   anchor_baseline['NPV_USD'],
                   rtol=0.01)  # 1% tolerance
    assert_allclose(fdas_result['MIRR_annual'],
                   anchor_baseline['MIRR_annual'],
                   rtol=0.001)  # 0.1% tolerance
```

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| BSEE data structure incompatibility | High | Medium | Comprehensive adapter layer, extensive testing |
| NPV calculation differences | High | Low | Use exact Excel formulas from V30, validate with golden baseline |
| Performance degradation | Medium | Low | Profile code, optimize hot paths, use vectorized operations |
| Missing production data | Medium | Medium | Implement graceful degradation, data quality checks |
| Completion activity detection failures | Medium | Medium | Keyword library expansion, manual review process |

## Success Criteria

1. **Functional:**
   - FDAS module processes all BSEE data without errors
   - NPV/MIRR values match golden baseline within 1%
   - All major fields (Anchor, Julia, Jack, St. Malo) produce valid results

2. **Performance:**
   - Full analysis completes in < 5 minutes for single field
   - Memory usage < 2GB for typical dataset
   - Can process 10+ years of production data

3. **Code Quality:**
   - 90%+ test coverage
   - Type hints on all public APIs
   - Documentation for all modules
   - Passes mypy strict mode

4. **Integration:**
   - Works with existing BSEE pipeline
   - No breaking changes to existing consumers
   - Clear migration path for legacy code

## Timeline Summary

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| 1. Core Module | 3 days | None |
| 2. BSEE Adapter | 5 days | Phase 1 |
| 3. Production Processing | 4 days | Phase 2 |
| 4. D&C Timeline | 4 days | Phase 2 |
| 5. Cashflow Engine | 5 days | Phase 1, 3, 4 |
| 6. Reports | 3 days | Phase 5 |
| 7. Integration Testing | 3 days | All above |
| 8. Documentation | 2 days | Phase 7 |
| **Total** | **29 days** (~6 weeks with parallel work) |

## Recommendations

### Immediate Actions (Week 1)
1. Create FDAS module skeleton
2. Port core NPV/MIRR functions with unit tests
3. Set up BSEE adapter framework
4. Document BSEE → FDAS data mapping

### Short-term (Weeks 2-4)
1. Implement production data processing
2. Build D&C timeline extraction
3. Create cashflow engine
4. Validate against golden baseline

### Medium-term (Weeks 5-6)
1. Complete report generation
2. Integration testing
3. Documentation
4. Performance optimization

### Future Enhancements
1. After-tax financial modeling (from V30 docx reference)
2. Sensitivity analysis and tornado charts
3. Monte Carlo simulation
4. API endpoints for web dashboard
5. Real-time data refresh integration

## Appendix A: Key Code Snippets

### NPV Calculation (Excel-compatible)
```python
def excel_like_mirr(cf: np.ndarray, r_ann: float) -> float:
    """
    Modified Internal Rate of Return using Excel methodology
    Trims to first/last non-zero cashflow before calculation
    """
    nz = np.where(np.abs(cf) > 1e-6)[0]
    if nz.size == 0:
        return np.nan

    cf = cf[nz[0]:nz[-1]+1]
    if not (np.any(cf > 0) and np.any(cf < 0)):
        return np.nan

    n = cf.size - 1
    r = (1.0 + r_ann)**(1/12) - 1.0

    fv_pos = sum(cf[t] * ((1.0 + r) ** (n - t))
                 for t in range(cf.size) if cf[t] > 0)
    pv_neg = sum(cf[t] / ((1.0 + r) ** t)
                 for t in range(cf.size) if cf[t] < 0)

    if pv_neg >= 0 or fv_pos <= 0:
        return np.nan

    return (fv_pos / -pv_neg) ** (1.0 / n) - 1.0
```

### Development System Classification
```python
def norm_dev_system(s):
    """Normalize development system name"""
    if pd.isna(s):
        return 'unknown'
    return str(s).strip().lower().replace(' ', '')

# Usage in assumptions lookup
def Aget(assumptions_df, sys_name, key, default=0.0):
    """Get assumption value for development system"""
    sysn = norm_dev_system(sys_name)
    keyU = key.upper()

    if keyU in assumptions_df.columns:
        mask = (assumptions_df['DEV_SYSTEM'] == sysn)
        if not mask.any():
            mask = (assumptions_df['DEV_SYSTEM'] == 'default')

        if mask.any():
            val = assumptions_df.loc[mask, keyU].iloc[0]
            return float(val) if pd.notna(val) else default

    return default
```

## Appendix B: BSEE Field Mapping Reference

| Field Name | Complex ID | Lease Numbers | Water Depth | Dev System |
|------------|-----------|---------------|-------------|------------|
| Anchor | 603214001 | G09868 | 7,500 ft | subsea20 |
| Julia | 603214011 | G09964 | 7,000 ft | subsea15 |
| Jack | 603214096 | G32306 | 7,000 ft | subsea15 |
| St. Malo | 603214097 | G32635 | 6,800 ft | subsea15 |

---

**End of Implementation Plan**
