# Initial NPV Troubleshooting Findings

## Timestamp: 2025-08-13

## Key Discovery

From the NPV summary data, we can derive:

### Implied Production and Pricing
- **Total Production**: 7,800,613 BBL (calculated from Total OPEX / OPEX per BBL)
- **Implied Average Oil Price**: $111.64/BBL (calculated from Total Revenue / Total Production)
- **OPEX per BBL**: $15.00

### Financial Metrics
- **Total Revenue**: $870,823,453.46
- **Total OPEX**: $117,009,195.00
- **Total CAPEX**: $1,460,000,000.00
- **Net Operating Cash Flow**: $753,814,258.46 (Revenue - OPEX)
- **Net Cash Flow (after CAPEX)**: $318,402,531.73

### NPV Result
- **Calculated NPV**: -$1,206,976,526.76
- **Discount Rate**: 10% annual

## Critical Issue Identified

The NPV is highly negative (-$1.2B) despite:
1. Positive net operating cash flows of $753.8M
2. Net cash flow after CAPEX of $318.4M

This suggests a fundamental issue with either:
1. The discounting methodology
2. The timing of cash flows
3. The NPV formula implementation

## Single Well Verification

Created a test case for one well producing 50,000 BBL in one month:
- Oil Price: $65/BBL
- Revenue: $3,250,000
- OPEX: $750,000
- Net Cash Flow: $2,500,000
- Discounted CF (Month 1): $2,479,339

The single well calculation appears correct.

## Next Steps

1. Extract actual production profile from test data
2. Verify monthly cash flow calculations
3. Check NPV discounting formula implementation
4. Compare with Excel benchmark values

## Questions to Investigate

1. Why is the implied oil price $111.64/BBL so high?
2. Is the CAPEX being applied correctly in the NPV calculation?
3. Are the cash flows being discounted from the correct time periods?
4. Is there a sign error in the NPV calculation?