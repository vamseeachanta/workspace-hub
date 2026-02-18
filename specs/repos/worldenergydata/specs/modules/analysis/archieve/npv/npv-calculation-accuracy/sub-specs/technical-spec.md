# Technical Specification

This is the technical specification for the spec detailed in @specs/modules/analysis/npv-calculation-accuracy/spec.md

> Created: 2025-07-25
> Version: 1.0.0

## Technical Requirements

- **NPV Function Alignment**: Replace numpy-financial NPV with custom implementation that exactly mirrors Excel's NPV function behavior
- **Cash Flow Timing**: Implement proper period alignment where Period 0 = initial investment, Period 1+ = operating cash flows
- **Discount Rate Application**: Use Excel's NPV formula: `NPV = ∑(CFt / (1 + r)^t)` where t starts from 1 for operating cash flows
- **Data Source Consistency**: Ensure oil prices, production volumes, and cost parameters exactly match Excel analysis inputs
- **Precision Requirements**: Achieve NPV results within 10-20% variance from Excel calculations
- **Backward Compatibility**: Maintain existing API while improving calculation accuracy

## Approach Options

**Option A: Custom NPV Implementation** (Selected)
- Pros: Full control over calculation methodology, exact Excel alignment possible, transparent logic
- Cons: More development effort, need to implement and test financial mathematics

**Option B: numpy-financial Parameter Adjustment**
- Pros: Minimal code changes, leverages tested library
- Cons: Limited control over timing assumptions, may not achieve exact Excel alignment

**Option C: Excel Integration via openpyxl**
- Pros: Guaranteed Excel compatibility
- Cons: Performance overhead, external Excel dependency, deployment complexity

**Rationale:** Option A provides the best balance of accuracy, control, and maintainability. By implementing the exact Excel NPV formula, we can ensure identical results while maintaining code transparency and avoiding external dependencies.

## Key Implementation Details

### Current Issue Analysis
Based on code review, the main discrepancy sources are:
1. **Period Timing**: Current code may not handle Period 0 (CAPEX) vs Period 1+ (operating cash flows) correctly
2. **Discount Rate Application**: Monthly vs annual discount rate conversion inconsistencies
3. **Cash Flow Construction**: Possible differences in how revenue, OPEX, and CAPEX are combined
4. **Data Alignment**: Oil prices and production volumes may not exactly match Excel inputs

### Solution Architecture
1. **NPV Engine Refactoring**: Replace existing `perform_npv_calculation` method with Excel-aligned implementation
2. **Cash Flow Validation**: Add comprehensive logging and validation of all cash flow components
3. **Input Data Verification**: Implement data comparison utilities to verify Excel input alignment
4. **Test Framework**: Create benchmark tests using known Excel results

## External Dependencies

No new external dependencies required. Will use existing libraries:
- **pandas** - For data manipulation and alignment
- **numpy** - For mathematical operations (replacing numpy-financial NPV)
- **python built-ins** - For financial calculations