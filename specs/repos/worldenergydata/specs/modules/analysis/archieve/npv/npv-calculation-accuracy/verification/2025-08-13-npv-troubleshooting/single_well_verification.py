#!/usr/bin/env python
"""
Single Well Production and Oil Price Verification
Created: 2025-08-13
Purpose: Verify production calculations for a single well for one month
"""

import pandas as pd
import numpy as np
from datetime import datetime

def verify_single_well_month():
    """
    Verify production and oil price calculation for one well for one month
    """
    
    print("=" * 80)
    print("SINGLE WELL PRODUCTION VERIFICATION")
    print("=" * 80)
    
    # Test data for one well, one month
    test_well = {
        'API12': '608174046300',
        'COMPLETION_NAME': 'WELL_A',
        'PRODUCTION_MONTH': '2019-01',
        'MON_O_PROD_VOL': 50000,  # 50,000 BBL for the month
        'DAYS_ON_PROD': 30,
        'OIL_PRICE_BRENT': 65.0,  # $65/BBL
        'OPEX_PER_BBL': 15.0      # $15/BBL operating cost
    }
    
    print(f"\nTest Well Configuration:")
    print(f"  API12: {test_well['API12']}")
    print(f"  Completion: {test_well['COMPLETION_NAME']}")
    print(f"  Month: {test_well['PRODUCTION_MONTH']}")
    print(f"  Production Volume: {test_well['MON_O_PROD_VOL']:,} BBL")
    print(f"  Days on Production: {test_well['DAYS_ON_PROD']}")
    print(f"  Oil Price (BRENT): ${test_well['OIL_PRICE_BRENT']:.2f}/BBL")
    print(f"  OPEX: ${test_well['OPEX_PER_BBL']:.2f}/BBL")
    
    # Calculate production rate
    prod_rate_bopd = test_well['MON_O_PROD_VOL'] / test_well['DAYS_ON_PROD']
    print(f"\nProduction Rate: {prod_rate_bopd:,.0f} BOPD")
    
    # Calculate revenue
    revenue = test_well['MON_O_PROD_VOL'] * test_well['OIL_PRICE_BRENT']
    print(f"\nRevenue Calculation:")
    print(f"  Production × Oil Price = Revenue")
    print(f"  {test_well['MON_O_PROD_VOL']:,} BBL × ${test_well['OIL_PRICE_BRENT']:.2f}/BBL = ${revenue:,.2f}")
    
    # Calculate OPEX
    opex = test_well['MON_O_PROD_VOL'] * test_well['OPEX_PER_BBL']
    print(f"\nOPEX Calculation:")
    print(f"  Production × OPEX Rate = Total OPEX")
    print(f"  {test_well['MON_O_PROD_VOL']:,} BBL × ${test_well['OPEX_PER_BBL']:.2f}/BBL = ${opex:,.2f}")
    
    # Calculate net cash flow
    net_cash_flow = revenue - opex
    print(f"\nNet Cash Flow (before CAPEX):")
    print(f"  Revenue - OPEX = Net Cash Flow")
    print(f"  ${revenue:,.2f} - ${opex:,.2f} = ${net_cash_flow:,.2f}")
    
    # NPV calculation for single month (no discounting for month 1)
    discount_rate_monthly = 0.1 / 12  # 10% annual to monthly
    discount_factor = 1 / (1 + discount_rate_monthly) ** 1
    discounted_cash_flow = net_cash_flow * discount_factor
    
    print(f"\nNPV Calculation (single month):")
    print(f"  Annual Discount Rate: 10%")
    print(f"  Monthly Discount Rate: {discount_rate_monthly:.4%}")
    print(f"  Discount Factor (Month 1): {discount_factor:.6f}")
    print(f"  Discounted Cash Flow: ${discounted_cash_flow:,.2f}")
    
    # Create summary dataframe
    summary_df = pd.DataFrame([{
        'API12': test_well['API12'],
        'Month': test_well['PRODUCTION_MONTH'],
        'Production_BBL': test_well['MON_O_PROD_VOL'],
        'Oil_Price_USD': test_well['OIL_PRICE_BRENT'],
        'Revenue_USD': revenue,
        'OPEX_USD': opex,
        'Net_Cash_Flow_USD': net_cash_flow,
        'Discounted_CF_USD': discounted_cash_flow
    }])
    
    print("\n" + "=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print(summary_df.to_string(index=False))
    
    # Save results
    output_file = 'single_well_verification_results.csv'
    summary_df.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")
    
    return summary_df

if __name__ == "__main__":
    verify_single_well_month()