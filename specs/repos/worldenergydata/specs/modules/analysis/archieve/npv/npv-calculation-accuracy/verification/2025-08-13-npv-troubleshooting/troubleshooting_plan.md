# NPV Calculation Troubleshooting Plan

> Verification Date: 2025-08-13
> Current NPV Result: -$1,206,976,526.76 (44.55% variance from Excel)
> Target: <20% variance from Excel benchmark

## Current Status Analysis

### Key Financial Metrics from Latest Run
- **NPV**: -$1,206,976,526.76 (negative)
- **Total Revenue**: $870,823,453.46
- **Total OPEX**: $117,009,195.00
- **Total CAPEX**: $1,460,000,000 (Excel-aligned)
- **Net Cash Flow**: $318,402,531.73
- **Discount Rate**: 10% annual

### Critical Observation
The NPV result is **highly negative** (-$1.2B), which suggests potential issues with:
1. **Cash flow timing** - CAPEX may be overwhelming operational cash flows
2. **Production scaling** - Revenue may be too low relative to CAPEX
3. **Period alignment** - Cash flows may not be properly discounted

## Troubleshooting Methodology

### Phase 1: Immediate Data Validation

#### 1.1 Excel Benchmark Extraction
**Objective**: Get the exact Excel NPV value for comparison

**Actions**:
- [ ] Open `/docs/modules/bsee/data/NPV_JStM-WELL-Production-Data-thru-2019.xlsx`
- [ ] Locate the NPV calculation cell(s) in the "NPV w Mo'ly data chart" sheet
- [ ] Extract the exact Excel NPV value at 10% discount rate
- [ ] Document the Excel NPV methodology (formula, timing, assumptions)

#### 1.2 Cash Flow Component Analysis
**Objective**: Validate each component of the cash flow calculation

**Actions**:
- [ ] Compare monthly production volumes with Excel Row 22 (JSM Total AVGMoly)
- [ ] Validate oil price extraction from Excel Row 2 (BRENT prices)
- [ ] Verify revenue calculation: production × oil price per month
- [ ] Check OPEX calculation: production × $15/BBL
- [ ] Confirm CAPEX timing and amount ($1.46B at Period 0)

#### 1.3 NPV Formula Verification
**Objective**: Ensure NPV calculation method matches Excel exactly

**Actions**:
- [ ] Test NPV formula with simple 3-period cash flow example
- [ ] Compare numpy-financial NPV vs custom implementation vs Excel
- [ ] Verify discount rate application (annual 10% vs monthly equivalent)
- [ ] Check period timing assumptions (mid-period vs end-period)

### Phase 2: Detailed Variance Analysis

#### 2.1 Production Data Scaling Investigation
**Current Issue**: Revenue of $870M seems low for a $1.46B CAPEX project

**Investigation Points**:
- [ ] Verify production data extraction methodology
- [ ] Check calibration factors applied to production volumes
- [ ] Compare total production volumes with Excel expectations
- [ ] Validate production timeline (start date, duration, decline)

#### 2.2 Cash Flow Timing Analysis
**Current Issue**: NPV is highly negative despite positive net cash flow

**Investigation Points**:
- [ ] Verify CAPEX is placed at Period 0 (not discounted)
- [ ] Ensure operational cash flows start at Period 1 and are properly discounted
- [ ] Check monthly vs annual period conversion
- [ ] Validate discount factor calculation for each period

#### 2.3 Oil Price and Market Assumptions
**Investigation Points**:
- [ ] Compare extracted BRENT prices with Excel values month-by-month
- [ ] Verify price timeline alignment with production periods
- [ ] Check for any price escalation or real vs nominal price issues
- [ ] Validate currency assumptions (all USD)

### Phase 3: Targeted Corrections

Based on Phase 1-2 findings, implement specific fixes:

#### 3.1 High-Impact Corrections
- [ ] **Production Scaling Fix** (if production volumes are incorrect)
- [ ] **NPV Formula Correction** (if timing/formula methodology is wrong)
- [ ] **Cash Flow Timing Fix** (if period alignment is causing issues)

#### 3.2 Validation Testing
- [ ] Run corrected NPV calculation with detailed logging
- [ ] Compare result with Excel benchmark
- [ ] Calculate variance percentage improvement
- [ ] Document remaining variance sources

## Specific Technical Investigation Areas

### 1. Excel NPV Function Replication
```python
# Test simple NPV calculation to validate methodology
import numpy_financial as npf

# Simple test case
cash_flows = [-1000, 300, 400, 500]  # CAPEX at t=0, positive flows t=1,2,3
discount_rate = 0.10

# Compare implementations
npv_numpy = npf.npv(discount_rate, cash_flows)
npv_excel = sum(cf / (1 + discount_rate)**i for i, cf in enumerate(cash_flows))
npv_custom = -cash_flows[0] + sum(cf / (1 + discount_rate)**i for i, cf in enumerate(cash_flows[1:], 1))

print(f"NumPy NPV: {npv_numpy}")
print(f"Excel NPV: {npv_excel}")  
print(f"Custom NPV: {npv_custom}")
```

### 2. Production Data Extraction Verification
```python
# Verify Excel data extraction
import pandas as pd

excel_file = "docs/modules/bsee/data/NPV_JStM-WELL-Production-Data-thru-2019.xlsx"
df_excel = pd.read_excel(excel_file, sheet_name="NPV w Mo'ly data chart")

# Extract Row 2 (oil prices) and Row 22 (production data)
oil_prices = df_excel.iloc[1, 1:].values  # Row 2, starting from column B
production_data = df_excel.iloc[21, 1:].values  # Row 22, starting from column B

print(f"Oil Prices (first 12 months): {oil_prices[:12]}")
print(f"Production Data (first 12 months): {production_data[:12]}")
```

### 3. Cash Flow Timeline Reconstruction
```python
# Reconstruct monthly cash flows step by step
months = range(1, len(production_data) + 1)
monthly_revenue = production_data * oil_prices
monthly_opex = production_data * 15.0  # $15/BBL
monthly_net_cf = monthly_revenue - monthly_opex

# Add CAPEX at Period 0
cash_flows = [-1460000000] + monthly_net_cf.tolist()

# Calculate NPV
npv_result = npf.npv(0.10, cash_flows)
print(f"Reconstructed NPV: ${npv_result:,.2f}")
```

## Expected Deliverables

### 1. Root Cause Analysis Report
- Exact variance amount and percentage
- Primary contributing factors ranked by impact
- Technical explanation of discrepancies

### 2. Corrected NPV Implementation
- Updated NPV calculation method
- Comprehensive test validation
- Performance comparison with previous version

### 3. Validation Results
- Before/after NPV comparison
- Variance reduction achieved
- Remaining variance explanation

## Success Criteria

### Immediate Goals (Phase 1)
- [ ] Identify exact Excel NPV benchmark value
- [ ] Isolate top 3 variance contributing factors
- [ ] Understand why current NPV is highly negative

### Medium-term Goals (Phase 2-3)
- [ ] Reduce NPV variance to <30% (significant improvement)
- [ ] Achieve NPV variance <20% (target achievement)
- [ ] Create robust validation framework for future testing

### Documentation Goals
- [ ] Clear explanation of methodology changes
- [ ] Comprehensive variance analysis report
- [ ] Updated test suite with improved validation

This systematic approach will identify and resolve the root causes preventing achievement of the <20% NPV variance target.