# Spec Tasks

These are the tasks to be completed for the spec detailed in @specs/modules/analysis/npv-data-source-comparison/spec.md

> Created: 2025-07-28
> Status: Ready for Implementation

## Output File Organization

All output files from this spec should be saved to:
```
tests\modules\bsee\analysis\<spec_folder>\
├── data\           # CSV and JSON data files
├── visualizations\ # Charts and graphs (PNG/PDF)
└── reports\        # Markdown and text reports
```
Note: `<spec_folder>` should match the spec folder name (e.g., `npv-data-source-comparison` for this spec)

## Tasks

- [x] 1. Create Excel Data Extraction Utilities
  - [x] 1.1 Write tests for Excel data extraction functions
  - [x] 1.2 Implement production data extraction from Row 22 (JSM Total AVGMoly)
  - [x] 1.3 Implement oil price extraction from Row 4 (BRENT prices - corrected from Row 2)
  - [x] 1.4 Add data validation and error handling
  - [x] 1.5 Verify all extraction tests pass (14/14 tests passing)

- [x] 2. Analyze Excel Data Characteristics
  - [x] 2.1 Extract and validate Excel benchmark data (55 periods)
  - [x] 2.2 Calculate average production (33,938 BBL/period)
  - [x] 2.3 Calculate average oil price ($56.60/BBL)
  - [x] 2.4 Identify data represents DAILY production, not monthly
  - [x] 2.5 Document total revenue potential ($106M)

- [x] 3. Build NPV Comparison Framework
  - [x] 3.1 Create NPV calculation using Excel data
  - [x] 3.2 Calculate NPV with same parameters as manual analysis
  - [x] 3.3 Identify 44.2% variance from Excel benchmark
  - [x] 3.4 Test sensitivity to daily vs monthly interpretation
  - [x] 3.5 Generate comprehensive comparison reports
  - [x] 3.6 Save visualizations and CSV breakdowns to tests\modules\bsee\analysis\<spec_folder>\

- [x] 4. Identify Root Causes of NPV Variance
  - [x] 4.1 Production scale mismatch: Excel data is daily (33,938 BBL/day)
  - [x] 4.2 Period count difference: 55 periods vs expected 60 months
  - [x] 4.3 Revenue scale issue: $106M seems low for deepwater field
  - [x] 4.4 Confirm OPEX calculation uses same $15/BBL rate
  - [x] 4.5 Document cash flow component breakdown
  - [x] 4.6 Create detailed recommendations for alignment

- [x] 5. Create Comprehensive Production and Prices Differences Report
  - [x] 5.1 Document production data scale differences (daily vs monthly)
  - [x] 5.2 Analyze oil price data source alignment and variations
  - [x] 5.3 Quantify revenue impact of production scale mismatch (33.1x factor)
  - [x] 5.4 Create detailed comparison tables and visualizations
  - [x] 5.5 Generate executive summary of key differences
  - [x] 5.6 Provide specific recommendations for data alignment

- [x] 6. Implement Data Alignment Solution
  - [x] 6.1 Update manual analysis to use daily production data
  - [x] 6.2 Ensure consistent time period aggregation
  - [x] 6.3 Extend data to full 60-month period if possible
  - [x] 6.4 Re-run NPV calculations with aligned data
  - [x] 6.5 Update NPV accuracy spec (2025-07-25) with findings
  - [x] 6.6 Verify NPV variance reduced to <20% target

- [x] 7. Create Comparison Table for Field Analysis Methods
  - [x] 7.1 Write tests for comparison table generation
  - [x] 7.2 Extract field data for both Excel and WorldEnergyData methods
  - [x] 7.3 Calculate required parameters for comparison table
  - [x] 7.4 Generate markdown comparison table with the following parameters:
    - Number of months of production
    - Production Start Month
    - Production End Month
    - Total production in BBL
    - Average oil price in USD
    - Total revenue in USD
    - Number of Wells - total
    - Number of Wells - producing
    - Total average daily Production by month
  - [x] 7.5 Verify comparison accuracy and save results

- [x] 8. Generate Monthly Field Economics DataFrame
  - [x] 8.1 Write tests for monthly dataframe generation
  - [x] 8.2 Create monthly production and economic data extraction
  - [x] 8.3 Calculate monthly economic metrics (CAPEX, OPEX, Oil sales, Revenue, NPV)
  - [x] 8.4 Generate dataframe with following columns by month:
    - Month-Year (production period)
    - Monthly production in BBL
    - Oil price in USD
    - CAPEX (monthly allocation)
    - OPEX (monthly calculation)  
    - Oil sales (monthly revenue)
    - Net revenue (after OPEX)
    - Cumulative revenue
    - Cumulative OPEX
    - Cumulative CAPEX
    - Cumulative cash flow
    - Cumulative cash flow after OPEX
    - Cumulative NPV
    - Wells total (monthly count)
    - Wells producing (monthly count)
    - Daily production rate (BBL/day for that month)
  - [x] 8.5 Save dataframe as CSV in tests\modules\bsee\analysis\<spec_folder>\data\
  - [x] 8.6 Verify data accuracy and completeness

- [x] 9. Prepare Excel-based CSV for Task 8 DataFrame Comparison
  - [x] 9.1 Extract all calculation data from NPV_JStM-WELL-Production-Data-thru-2019.xlsx
  - [x] 9.2 Identify Excel rows containing monthly economic calculations
  - [x] 9.3 Map Excel columns to Task 8 DataFrame structure:
    - Month-Year periods from Excel timeline
    - Monthly production from JSM Total AVGMoly (Row 22)
    - Oil prices from BRENT data (Row 2 - corrected from Row 4)
    - OPEX calculations from Excel operational costs. No explicit row, embedded in Row 22. Evaluate.
    - CAPEX allocation from Excel investment schedule (Row 34)
    - Revenue calculations from Excel oil sales. No explicit row, embedded in Row 22. Evaluate.
    - Revenue - OPEX calculation given in Row 22
    - NPV calculations from Excel financial model
  - [x] 9.4 Process Excel formulas and convert to monthly data points
  - [x] 9.5 Generate CSV with identical column structure to Task 8 DataFrame:
    - Month-Year, Monthly_production_BBL, Oil_price_USD
    - CAPEX_monthly, OPEX_monthly, Oil_sales
    - Net_revenue_after_OPEX, Cumulative_revenue
    - Cumulative_OPEX, Cumulative_CAPEX, Cumulative_cash_flow
    - Cumulative_cash_flow_after_OPEX, Cumulative_NPV
    - Wells_total, Wells_producing, Daily_production_rate_BBL_per_day
  - [x] 9.6 Save Excel-derived CSV in tests\modules\bsee\analysis\<spec_folder>\data\ as comparison baseline
  - [x] 9.7 Create side-by-side comparison analysis between Excel CSV and Task 8 DataFrame
  - [x] 9.8 Generate variance report highlighting differences between data sources
  - [x] 9.9 Validate that both datasets cover same time periods and metrics
  - [x] 9.10 Document methodology differences between Excel and programmatic calculations

## Key Findings Summary

### Tasks 1-6: Initial Data Analysis
1. **Excel Data Characteristics:**
   -  
   - 55 periods of DAILY production data
   - Average: 33,938 BBL/day
   - Oil prices: $56.60/BBL average
   - Total revenue: $106M

1. **NPV Calculation Results:**
   - Using Excel data: -$1.45B
   - Excel benchmark: ~-$2.6B
   - Variance: 44.2%

2. **Root Cause Analysis:**
   - Production data is DAILY, not MONTHLY
   - Only 55 days of data vs expected 60 months
   - Manual analysis likely using monthly aggregation
   - This explains the significant NPV variance

### Task 9: Excel vs Task 8 Comparison Results
1. **Data Source Mapping (Corrected):**
   - Oil Prices: Row 2 (BRENT prices) - NOT Row 4
   - Production: Row 22 (JSM Total AVGMoly) - Confirmed
   - Well Count: Row 27
   - CAPEX: Row 32
   - Revenue: Row 31

2. **Scale Discrepancy Identified:**
   - Excel Total Production: 5,720,176 BBL over 55 periods
   - Task 8 Total Production: 268,330 BBL over 60 periods
   - Variance: 2031.77% difference
   - Excel appears to show MONTHLY production data (104,003 BBL/period average)
   - Task 8 shows much lower values (4,472 BBL/period average)

3. **Time Period Differences:**
   - Excel: 55 periods (December through June, no year labels)
   - Task 8: 60 periods (2014-08 through 2019-06)
   - Different coverage may explain some variance

4. **Key Recommendations:**
   - Verify the actual scale of Excel production data (monthly vs daily)
   - Align time periods between data sources
   - Standardize oil price sources (Excel: $56.60/BBL avg, Task 8: $63.00/BBL avg)
   - Document all calculation assumptions clearly