#!/usr/bin/env python
"""
Extract and Verify Actual Well Production Data
Created: 2025-08-13
Purpose: Extract actual production data from the system for verification
"""

import pandas as pd
import os

def extract_actual_well_data():
    """
    Extract actual production data from a real well
    """
    
    print("=" * 80)
    print("EXTRACTING ACTUAL WELL PRODUCTION DATA")
    print("=" * 80)
    
    # Look for test data files
    test_data_path = "/mnt/github/github/worldenergydata/tests/modules/bsee/analysis/results"
    
    # Check for CSV files with production data
    csv_files = []
    if os.path.exists(test_data_path):
        for file in os.listdir(test_data_path):
            if file.endswith('.csv'):
                csv_files.append(os.path.join(test_data_path, file))
                print(f"Found CSV: {file}")
    
    # Check the NPV summary data
    npv_summary_file = os.path.join(test_data_path, "npv_summary_goa_jack_stmalo.csv")
    if os.path.exists(npv_summary_file):
        print(f"\nNPV Summary Data:")
        npv_data = pd.read_csv(npv_summary_file)
        print(npv_data.to_string())
        
        # Extract key metrics
        if not npv_data.empty:
            row = npv_data.iloc[0]
            print(f"\n" + "=" * 80)
            print("EXTRACTED METRICS FROM NPV ANALYSIS:")
            print("=" * 80)
            print(f"Field Name: {row['Field_Name']}")
            print(f"NPV: ${row['NPV_rate']:,.2f}")
            print(f"Total CAPEX: ${row['Total_CAPEX_USD']:,.2f}")
            print(f"Total Revenue: ${row['Total_Revenue_USD']:,.2f}")
            print(f"Total OPEX: ${row['Total_OPEX_USD']:,.2f}")
            print(f"Total Net Cash Flow: ${row['Total_Net_Cash_Flow_USD']:,.2f}")
            print(f"OPEX per BBL: ${row['OPEX_per_BBL_USD']:.2f}")
            print(f"Discount Rate: {row['Discount_Rate_Annual']*100:.0f}%")
            
            # Calculate implied production
            if row['OPEX_per_BBL_USD'] > 0:
                implied_production = row['Total_OPEX_USD'] / row['OPEX_per_BBL_USD']
                print(f"\nIMPLIED TOTAL PRODUCTION:")
                print(f"  Total OPEX / OPEX per BBL = Total Production")
                print(f"  ${row['Total_OPEX_USD']:,.2f} / ${row['OPEX_per_BBL_USD']:.2f} = {implied_production:,.0f} BBL")
                
                # Calculate implied oil price
                if implied_production > 0:
                    implied_oil_price = row['Total_Revenue_USD'] / implied_production
                    print(f"\nIMPLIED AVERAGE OIL PRICE:")
                    print(f"  Total Revenue / Total Production = Average Oil Price")
                    print(f"  ${row['Total_Revenue_USD']:,.2f} / {implied_production:,.0f} BBL = ${implied_oil_price:.2f}/BBL")
    
    # Look for actual production data files
    prod_data_path = "/mnt/github/github/worldenergydata/data/modules/bsee/production/processed"
    if os.path.exists(prod_data_path):
        print(f"\n" + "=" * 80)
        print("CHECKING FOR PROCESSED PRODUCTION DATA:")
        print("=" * 80)
        for root, dirs, files in os.walk(prod_data_path):
            for file in files:
                if 'jack' in file.lower() or 'stmalo' in file.lower():
                    print(f"Found: {file}")
                    file_path = os.path.join(root, file)
                    if file.endswith('.csv'):
                        df = pd.read_csv(file_path, nrows=5)
                        print(f"  Columns: {list(df.columns)[:5]}...")
                        if 'MON_O_PROD_VOL' in df.columns:
                            print(f"  Sample production: {df['MON_O_PROD_VOL'].head().tolist()}")

if __name__ == "__main__":
    extract_actual_well_data()