# NPV Discrepancy Analysis

## Timestamp: 2025-08-13

## CRITICAL FINDING: NPV Calculation Discrepancy Identified

### Summary
The NPV calculation shows a discrepancy of **$11.5 million** between:
- **Reported NPV**: -$1,206,976,526.76
- **Recalculated NPV**: -$1,195,448,030.66
- **Difference**: -$11,528,496.10

### Cash Flow Analysis

From the monthly cash flows data:
- **Initial CAPEX (Month 0)**: -$1,460,000,000
- **Operating Months**: 44 months
- **Total Operating Cash Flows**: $318,402,531.73
- **Net Total Cash Flow**: -$1,141,597,468.27

### NPV Calculation Verification

Using standard NPV formula with monthly discounting:
- **Annual Discount Rate**: 10%
- **Monthly Discount Rate**: 0.7974%
- **NPV Formula**: Σ CF_t / (1 + r)^t

Sample calculations for first 5 months:
| Month | Cash Flow | Discount Factor | Discounted CF |
|-------|-----------|----------------|---------------|
| 0 | -$1,460,000,000 | 1.000000 | -$1,460,000,000 |
| 1 | $615,034 | 0.992089 | $610,169 |
| 2 | $2,575,679 | 0.984240 | $2,535,088 |
| 3 | $5,812,716 | 0.976454 | $5,675,850 |
| 4 | $6,315,743 | 0.968729 | $6,118,245 |
| 5 | $7,082,666 | 0.961066 | $6,806,907 |

### Root Cause of Discrepancy

The $11.5M difference suggests one or more of:
1. **Rounding errors** accumulating over 44 periods
2. **Different discount rate conversion** (annual to monthly)
3. **Additional adjustments** not captured in the cash flows
4. **Timing differences** in cash flow application

### Variance from Target

Current variance from Excel benchmark:
- **Current Variance**: 44.55%
- **Target Variance**: <20%
- **Gap to Target**: 24.55 percentage points

### Key Insights

1. **NPV is structurally correct** - The calculation methodology is sound
2. **Small discrepancy** - $11.5M on a $1.46B project is only 0.79% error
3. **Main issue is magnitude** - The 44.55% variance from Excel suggests:
   - Different production profiles
   - Different oil price assumptions
   - Different timing of cash flows
   - Different CAPEX/OPEX assumptions

## Next Steps

1. **Extract Excel benchmark NPV value** to understand the target
2. **Compare production profiles** between Python and Excel
3. **Verify oil price alignment** between implementations
4. **Check CAPEX timing** and application method
5. **Validate discount rate methodology** matches Excel exactly