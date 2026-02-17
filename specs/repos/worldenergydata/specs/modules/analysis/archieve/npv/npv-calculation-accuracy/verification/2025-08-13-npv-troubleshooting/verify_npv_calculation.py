#!/usr/bin/env python
"""
Verify NPV Calculation from Monthly Cash Flows
Created: 2025-08-13
Purpose: Recalculate NPV from the monthly cash flows to verify calculation
"""

import pandas as pd
import numpy as np

def verify_npv_from_cashflows():
    """
    Load monthly cash flows and recalculate NPV
    """
    
    print("=" * 80)
    print("NPV VERIFICATION FROM MONTHLY CASH FLOWS")
    print("=" * 80)
    
    # Load the monthly cash flows
    cashflow_file = "/mnt/github/github/worldenergydata/tests/modules/bsee/analysis/results/monthly_cashflows.csv"
    df = pd.read_csv(cashflow_file)
    
    print(f"\nLoaded {len(df)} months of cash flow data")
    print(f"First 5 entries:")
    print(df.head())
    
    # Extract cash flows
    cash_flows = df['Cash_Flow_USD'].values
    months = df['Month'].values
    
    # Calculate summary statistics
    capex = cash_flows[0]
    operating_cashflows = cash_flows[1:]
    total_operating_cf = operating_cashflows.sum()
    
    print(f"\n" + "=" * 80)
    print("CASH FLOW SUMMARY:")
    print("=" * 80)
    print(f"Initial CAPEX (Month 0): ${capex:,.2f}")
    print(f"Number of Operating Months: {len(operating_cashflows)}")
    print(f"Total Operating Cash Flows: ${total_operating_cf:,.2f}")
    print(f"Net Total Cash Flow: ${capex + total_operating_cf:,.2f}")
    
    # Calculate NPV with 10% annual discount rate
    annual_rate = 0.10
    monthly_rate = (1 + annual_rate) ** (1/12) - 1  # Convert to monthly
    
    print(f"\n" + "=" * 80)
    print("NPV CALCULATION:")
    print("=" * 80)
    print(f"Annual Discount Rate: {annual_rate:.1%}")
    print(f"Monthly Discount Rate: {monthly_rate:.4%}")
    
    # Method 1: Standard NPV calculation
    npv_standard = 0
    for t, cf in enumerate(cash_flows):
        discount_factor = 1 / (1 + monthly_rate) ** t
        discounted_cf = cf * discount_factor
        npv_standard += discounted_cf
        if t <= 5:  # Show first few calculations
            print(f"Month {t}: CF=${cf:,.2f}, DF={discount_factor:.6f}, DCF=${discounted_cf:,.2f}")
    
    print(f"\nNPV (Standard Method): ${npv_standard:,.2f}")
    
    # Method 2: Using numpy-financial's NPV function
    try:
        import numpy_financial as npf
        npv_numpy = npf.npv(monthly_rate, cash_flows)
        print(f"NPV (NumPy-Financial Method): ${npv_numpy:,.2f}")
    except ImportError:
        npv_numpy = npv_standard
        print(f"NPV (NumPy-Financial not available, using standard): ${npv_numpy:,.2f}")
    
    # Method 3: Alternative annual discounting (if months represent years)
    print(f"\n" + "=" * 80)
    print("ALTERNATIVE: IF PERIODS ARE YEARS (NOT MONTHS):")
    print("=" * 80)
    npv_annual = 0
    for t, cf in enumerate(cash_flows):
        discount_factor = 1 / (1 + annual_rate) ** t
        discounted_cf = cf * discount_factor
        npv_annual += discounted_cf
        if t <= 5:
            print(f"Year {t}: CF=${cf:,.2f}, DF={discount_factor:.6f}, DCF=${discounted_cf:,.2f}")
    
    print(f"\nNPV (Annual Discounting): ${npv_annual:,.2f}")
    
    # Compare with reported NPV
    reported_npv = -1206976526.76
    print(f"\n" + "=" * 80)
    print("COMPARISON WITH REPORTED NPV:")
    print("=" * 80)
    print(f"Reported NPV: ${reported_npv:,.2f}")
    print(f"Calculated NPV (Monthly): ${npv_standard:,.2f}")
    print(f"Difference: ${reported_npv - npv_standard:,.2f}")
    
    # Save results
    results_df = pd.DataFrame({
        'Method': ['Reported', 'Calculated_Monthly', 'Calculated_Annual', 'NumPy_Monthly'],
        'NPV_USD': [reported_npv, npv_standard, npv_annual, npv_numpy],
        'Discount_Rate': ['10% Annual', f'{monthly_rate:.4%} Monthly', '10% Annual', f'{monthly_rate:.4%} Monthly']
    })
    
    output_file = 'npv_verification_results.csv'
    results_df.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")
    
    return results_df

if __name__ == "__main__":
    verify_npv_from_cashflows()