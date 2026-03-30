---
name: financial-analysis-net-present-value
description: 'Sub-skill of financial-analysis: Net Present Value (+5).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Net Present Value (+5)

## Net Present Value


```python
def calculate_npv(cash_flows, discount_rate, initial_investment=0):
    """Calculate Net Present Value."""
    pv = sum([cf / (1 + discount_rate)**i
              for i, cf in enumerate(cash_flows, 1)])
    return pv - initial_investment
```

## WACC Calculation


```python
def calculate_wacc(equity_weight, debt_weight, cost_of_equity,
                   cost_of_debt, tax_rate):
    """Calculate Weighted Average Cost of Capital."""
    return (equity_weight * cost_of_equity +
            debt_weight * cost_of_debt * (1 - tax_rate))
```

## Sharpe Ratio


```python
import numpy as np

def sharpe_ratio(returns, risk_free_rate, periods_per_year=252):
    """Calculate Sharpe Ratio."""
    excess_returns = returns - risk_free_rate / periods_per_year
    return np.sqrt(periods_per_year) * (excess_returns.mean() /
                                        excess_returns.std())
```

## Black-Scholes Option Pricing


```python
from scipy.stats import norm
import numpy as np

def black_scholes(S, K, T, r, sigma, option_type='call'):
    """Black-Scholes option pricing."""
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
```

## Portfolio Metrics


```python
import pandas as pd
import numpy as np
from typing import Dict

def calculate_portfolio_metrics(
    returns: pd.Series,
    weights: np.ndarray,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252

*See sub-skills for full details.*

## Data Validation


```python
import pandas as pd

def validate_financial_data(data: pd.DataFrame) -> None:
    """Validate financial data quality and completeness."""
    if data.isnull().any().any():
        missing_cols = data.columns[data.isnull().any()].tolist()
        raise ValueError(f"Missing values in columns: {missing_cols}")
    price_cols = [col for col in data.columns if 'price' in col.lower()]
    for col in price_cols:
        if (data[col] < 0).any():
            raise ValueError(f"Negative values in price column: {col}")
    if 'volume' in data.columns and (data['volume'] < 0).any():
        raise ValueError("Negative volume detected")
```
