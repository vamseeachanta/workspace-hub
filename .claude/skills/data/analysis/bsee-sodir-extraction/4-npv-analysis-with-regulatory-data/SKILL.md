---
name: bsee-sodir-extraction-4-npv-analysis-with-regulatory-data
description: 'Sub-skill of bsee-sodir-extraction: 4. NPV Analysis with Regulatory
  Data.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 4. NPV Analysis with Regulatory Data

## 4. NPV Analysis with Regulatory Data


```python
import numpy as np
import numpy_financial as npf
import pandas as pd
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class EconomicAssumptions:
    """Economic assumptions for NPV calculation."""
    oil_price: float = 75.0      # $/bbl
    gas_price: float = 3.0       # $/mcf
    opex_per_boe: float = 15.0   # $/BOE
    capex_remaining: float = 0   # $ millions (for ongoing development)
    discount_rate: float = 0.10  # 10%
    royalty_rate: float = 0.125  # 12.5% federal royalty
    tax_rate: float = 0.21       # Corporate tax rate


def calculate_field_npv(
    production_df: pd.DataFrame,
    assumptions: EconomicAssumptions,
    forecast_years: int = 10
) -> Tuple[float, pd.DataFrame]:
    """
    Calculate NPV for a field based on BSEE production data.

    Args:
        production_df: Historical production data
        assumptions: Economic assumptions
        forecast_years: Years to forecast

    Returns:
        Tuple of (NPV, detailed cashflow DataFrame)
    """
    # Get latest year's production as baseline
    latest_year = production_df["PRODUCTION_YEAR"].max()
    baseline = production_df[production_df["PRODUCTION_YEAR"] == latest_year]

    annual_oil = baseline["OIL_BBL"].sum()
    annual_gas = baseline["GAS_MCF"].sum()

    # Simple decline curve (exponential decline)
    decline_rate = 0.10  # 10% annual decline

    cashflows = []

    for year in range(1, forecast_years + 1):
        # Decline production
        oil_prod = annual_oil * ((1 - decline_rate) ** year)
        gas_prod = annual_gas * ((1 - decline_rate) ** year)

        # Revenue
        oil_revenue = oil_prod * assumptions.oil_price
        gas_revenue = gas_prod * assumptions.gas_price
        gross_revenue = oil_revenue + gas_revenue

        # Royalties
        royalties = gross_revenue * assumptions.royalty_rate
        net_revenue = gross_revenue - royalties

        # Operating costs
        boe_produced = oil_prod + gas_prod / 6000
        opex = boe_produced * assumptions.opex_per_boe

        # EBITDA
        ebitda = net_revenue - opex

        # CapEx (if any)
        capex = assumptions.capex_remaining / forecast_years if year <= 3 else 0

        # Pre-tax income
        pretax_income = ebitda - capex

        # Taxes
        taxes = max(0, pretax_income * assumptions.tax_rate)

        # Net cash flow
        ncf = pretax_income - taxes

        cashflows.append({
            "Year": year,
            "Oil_BBL": oil_prod,
            "Gas_MCF": gas_prod,
            "Gross_Revenue_MM": gross_revenue / 1e6,
            "Royalties_MM": royalties / 1e6,
            "OPEX_MM": opex / 1e6,
            "CAPEX_MM": capex / 1e6,
            "Pre_Tax_MM": pretax_income / 1e6,
            "Taxes_MM": taxes / 1e6,
            "NCF_MM": ncf / 1e6
        })

    cashflow_df = pd.DataFrame(cashflows)

    # Calculate NPV
    ncf_series = [-assumptions.capex_remaining] + cashflow_df["NCF_MM"].tolist()
    npv = npf.npv(assumptions.discount_rate, ncf_series)

    return npv, cashflow_df


# Example: Calculate NPV for a GOM field
production = fetch_bsee_production_data(
    year=2024,
    output_dir=Path("data/raw/bsee")
)

# Filter to specific field
thunder_horse = production[
    production["FIELD_NAME"].str.contains("THUNDER HORSE", case=False, na=False)
]

assumptions = EconomicAssumptions(
    oil_price=75.0,
    gas_price=3.5,
    opex_per_boe=18.0,
    discount_rate=0.10
)

npv, cashflows = calculate_field_npv(thunder_horse, assumptions)

print(f"Thunder Horse NPV (10 year): ${npv:.1f} MM")
print("\nCashflow Summary:")
print(cashflows.to_string(index=False))
```
