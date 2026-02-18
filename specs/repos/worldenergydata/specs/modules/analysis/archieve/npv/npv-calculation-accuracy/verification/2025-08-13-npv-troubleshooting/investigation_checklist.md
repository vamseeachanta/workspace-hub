# NPV Troubleshooting Investigation Checklist

> Session: 2025-08-13
> Current NPV: -$1,206,976,526.76 (44.55% variance)
> Target: <20% variance from Excel

## Phase 1: Data Validation

### 1.1 Excel Benchmark Analysis
- [ ] Extract exact Excel NPV value from benchmark file
- [ ] Document Excel NPV methodology and assumptions
- [ ] Identify Excel cash flow structure and timing
- [ ] Calculate expected variance based on Excel benchmark

### 1.2 Current Implementation Analysis  
- [ ] Review Python NPV calculation code in production_api12.py
- [ ] Trace cash flow construction methodology
- [ ] Validate discount rate application approach
- [ ] Check period timing assumptions (Period 0 vs Period 1+)

### 1.3 Data Input Verification
- [ ] Verify oil price extraction from Excel Row 2 (BRENT)
- [ ] Validate production data extraction from Excel Row 22 (JSM Total AVGMoly)  
- [ ] Confirm CAPEX amount and timing ($1.46B at Period 0)
- [ ] Check OPEX calculation ($15/BBL application)

## Phase 2: Component-Level Analysis

### 2.1 Cash Flow Components
- [ ] **Revenue Validation**
  - Compare monthly production × oil price calculations
  - Verify production data scaling factors
  - Check oil price timeline alignment
- [ ] **OPEX Validation** 
  - Verify $15/BBL application to production volumes
  - Check monthly OPEX calculation methodology
- [ ] **CAPEX Validation**
  - Confirm $1.46B amount matches Excel
  - Verify timing at Period 0 (undiscounted)

### 2.2 NPV Formula Analysis
- [ ] **Formula Verification**
  - Test with simple 3-period cash flow example
  - Compare numpy-financial vs custom implementation
  - Validate against Excel NPV function directly
- [ ] **Discount Rate Application**
  - Verify 10% annual rate application
  - Check for monthly vs annual conversion issues
  - Confirm period timing methodology

### 2.3 Data Quality Assessment
- [ ] **Production Data Quality**
  - Check for missing or zero production months
  - Validate production timeline and duration
  - Assess calibration factor accuracy
- [ ] **Price Data Quality**
  - Verify BRENT price extraction accuracy
  - Check for missing or interpolated prices
  - Validate price currency and units

## Phase 3: Root Cause Identification

### 3.1 Variance Source Analysis
Based on investigation findings, rank variance sources by impact:

- [ ] **Primary Cause** (>50% of variance): ________________
- [ ] **Secondary Cause** (20-50% of variance): ________________
- [ ] **Tertiary Causes** (<20% of variance): ________________

### 3.2 Technical Issues Identified
- [ ] Production scaling calibration problems
- [ ] NPV formula timing methodology errors
- [ ] Data extraction or alignment issues
- [ ] Cash flow construction methodology flaws
- [ ] Discount rate application errors

## Phase 4: Solution Implementation

### 4.1 High-Impact Fixes
Based on root cause analysis, implement fixes for:

- [ ] **Fix #1**: ________________ (Expected variance reduction: __%)
- [ ] **Fix #2**: ________________ (Expected variance reduction: __%)
- [ ] **Fix #3**: ________________ (Expected variance reduction: __%)

### 4.2 Validation Testing
- [ ] Run corrected NPV calculation
- [ ] Compare against Excel benchmark
- [ ] Calculate variance improvement percentage
- [ ] Validate across multiple discount rates (8%, 10%, 12%)

## Current Status Summary

### Key Findings
- **Current NPV**: -$1,206,976,526.76
- **Revenue**: $870,823,453.46 (may be too low for $1.46B CAPEX)
- **OPEX**: $117,009,195.00 (reasonable for production levels)
- **Net Operating Cash Flow**: $753,814,258.46 over project life
- **Issue**: Negative NPV despite positive net cash flows suggests timing/discounting problems

### Critical Questions to Answer
1. **What is the exact Excel NPV benchmark value?**
2. **Why is the NPV negative despite positive net cash flows?**
3. **Is the production data properly scaled to match Excel assumptions?**
4. **Are cash flows properly timed and discounted?**
5. **What is the primary source of the 44.55% variance?**

### Next Priority Actions
1. Extract and document exact Excel NPV benchmark
2. Analyze cash flow timing and discount methodology  
3. Validate production data scaling and calibration
4. Test NPV formula with simplified scenarios
5. Implement targeted fixes based on findings

## Investigation Log

### Session Notes
- **Started**: 2025-08-13
- **Files Analyzed**: 
  - spec.md, tasks.md, technical-spec.md, tests.md
  - production_api12.py (NPV methods)
  - query_field_jack_stmalo_npv_test.py
  - NPV results: npv_summary_goa_jack_stmalo.csv
  - Configuration: query_field_jack_stmalo_npv.yml

### Key Observations
- All tasks marked complete but variance target not achieved
- NPV highly negative (-$1.2B) despite positive operations cash flows
- Revenue seems low relative to CAPEX for a major field development
- Need to investigate Excel benchmark and cash flow methodology

---
*This checklist will be updated as investigation progresses*