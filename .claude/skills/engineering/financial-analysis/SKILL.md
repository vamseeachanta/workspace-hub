---
name: financial-analysis
version: "1.0.0"
category: engineering
description: "Financial markets, investment analysis, energy economics and ESG"
capabilities: []
requires: []
see_also: []
---
# Financial Analysis Expert

> Domain expertise for financial markets, investment analysis, corporate finance, risk management, and energy finance. Use this skill when working on financial modeling, valuation, portfolio analysis, energy economics, or ESG analysis in the worldenergydata context.

## Domain Knowledge

### Financial Markets and Instruments
- **Equity Markets**: Stock valuation, market analysis, sector rotation
- **Fixed Income**: Bond pricing, yield curves, duration, credit analysis
- **Derivatives**: Options, futures, swaps, structured products
- **Commodities**: Energy markets, precious metals, agricultural products
- **Foreign Exchange**: Currency pairs, carry trades, hedging strategies
- **Alternative Investments**: Private equity, hedge funds, real assets

### Investment Analysis
- **Fundamental Analysis**: Financial statement analysis, ratio analysis, DCF modeling
- **Technical Analysis**: Chart patterns, indicators, momentum strategies
- **Quantitative Analysis**: Factor models, statistical arbitrage, algorithmic trading
- **Portfolio Management**: Asset allocation, risk management, performance attribution
- **Risk Assessment**: VaR, CVaR, stress testing, scenario analysis
- **ESG Investing**: Sustainable finance, impact investing, green bonds

### Corporate Finance
- **Capital Structure**: Optimal leverage, cost of capital, capital budgeting
- **Valuation Methods**: DCF, comparables, precedent transactions, LBO analysis
- **M&A Analysis**: Synergies, accretion/dilution, deal structuring
- **Financial Planning**: Budgeting, forecasting, variance analysis
- **Working Capital**: Cash management, receivables, inventory optimization
- **Dividend Policy**: Payout ratios, share buybacks, capital allocation

### Risk Management
- **Market Risk**: Beta, volatility, correlation, hedging strategies
- **Credit Risk**: Default probability, credit spreads, rating models
- **Operational Risk**: Process risks, fraud detection, internal controls
- **Liquidity Risk**: Funding risk, market liquidity, cash flow management
- **Regulatory Risk**: Compliance, capital requirements, stress testing
- **Systemic Risk**: Contagion effects, macroeconomic factors

### Energy Finance
- **Oil and Gas Economics**: Price forecasting, project finance, reserve valuation
- **Power Markets**: Electricity pricing, renewable energy finance, PPAs
- **Carbon Markets**: Emissions trading, carbon credits, offset projects
- **Energy Derivatives**: Commodity futures, options, basis swaps
- **Project Finance**: Infrastructure funding, risk allocation, cash flow modeling
- **Energy Transition**: Clean energy investments, stranded assets, transition risks

### Financial Modeling
- **DCF Models**: Free cash flow, WACC, terminal value calculations
- **LBO Models**: Debt schedules, returns analysis, exit strategies
- **Merger Models**: Pro forma statements, synergy modeling, integration costs
- **Project Finance Models**: Construction phase, operations, debt service
- **Monte Carlo Simulation**: Probabilistic modeling, sensitivity analysis
- **Option Pricing Models**: Black-Scholes, binomial trees, real options

## Energy Markets Context

### Oil Markets
- **WTI**: US benchmark crude oil
- **Brent Crude**: International benchmark
- **Dubai/Oman**: Middle East benchmark
- **OPEC Basket**: Average of OPEC member crudes

### Natural Gas Markets
- **Henry Hub**: US benchmark
- **NBP**: UK National Balancing Point
- **TTF**: European benchmark
- **JKM**: Asia Japan Korea Marker

### Electricity Markets
- **Day-Ahead Markets**: Next-day delivery
- **Real-Time Markets**: Immediate balancing
- **Capacity Markets**: Future reliability
- **Ancillary Services**: Grid stability

### Renewable Energy Economics
- **LCOE Trends**: Solar, wind, storage cost trajectories
- **PPAs**: Power Purchase Agreements
- **RECs**: Renewable Energy Certificates
- **Grid Parity**: Competitiveness analysis

### Carbon Markets
- **EU ETS**: European emissions trading
- **RGGI**: US Northeast carbon market
- **Voluntary Markets**: Carbon credits and offsets

### Key Energy Finance Metrics
- **LCOE**: Levelized Cost of Energy
- **IRR**: Internal Rate of Return
- **NPV**: Net Present Value
- **Spark/Dark Spreads**: Generation margins
- **Crack Spreads**: Refining margins

## Industry Standards and Regulations

### Accounting Standards
- **US GAAP**: Generally Accepted Accounting Principles
- **IFRS**: International Financial Reporting Standards
- **FASB**: Financial Accounting Standards Board guidelines
- **SEC Reporting**: 10-K, 10-Q, 8-K requirements
- **Audit Standards**: PCAOB, internal controls, SOX compliance

### Financial Regulations
- **Basel III/IV**: Capital requirements, liquidity ratios
- **Dodd-Frank**: Volcker rule, stress testing, derivatives regulation
- **MiFID II**: Market structure, transparency, investor protection
- **Solvency II**: Insurance capital requirements
- **GDPR**: Data protection in financial services

### Market Standards
- **GIPS**: Global Investment Performance Standards
- **CFA Standards**: Code of Ethics and Standards of Professional Conduct
- **ISDA**: Derivatives documentation and standards
- **FIX Protocol**: Electronic trading communications
- **XBRL**: Financial reporting taxonomy

### Sustainability Standards
- **TCFD**: Task Force on Climate-related Financial Disclosures
- **GRI Standards**: Global Reporting Initiative
- **ISO 50001**: Energy management systems

## Key Analysis Methods

### Valuation Techniques
- **Discounted Cash Flow (DCF)**: FCFF, FCFE, DDM, APV
- **Relative Valuation**: P/E, EV/EBITDA, P/B, PEG, EV/Sales, industry multiples
- **Asset-Based Valuation**: Book value, liquidation value, replacement cost, sum-of-parts

### Risk Metrics
- **Portfolio Risk**: Standard deviation, Sharpe ratio, Information ratio, Sortino ratio, maximum drawdown, Calmar ratio
- **Value at Risk (VaR)**: Historical simulation, variance-covariance, Monte Carlo simulation
- **Credit Metrics**: Probability of default (PD), Loss given default (LGD), Expected loss (EL), Credit value adjustment (CVA)

### Performance Analysis
- **Return Metrics**: TWR (time-weighted return), MWR (money-weighted return), IRR, XIRR
- **Risk-Adjusted Returns**: Sharpe ratio, Treynor ratio, Jensen's alpha, Information ratio, M-squared, Omega ratio

## Common Calculations

### Net Present Value
```python
def calculate_npv(cash_flows, discount_rate, initial_investment=0):
    """Calculate Net Present Value."""
    pv = sum([cf / (1 + discount_rate)**i
              for i, cf in enumerate(cash_flows, 1)])
    return pv - initial_investment
```

### WACC Calculation
```python
def calculate_wacc(equity_weight, debt_weight, cost_of_equity,
                   cost_of_debt, tax_rate):
    """Calculate Weighted Average Cost of Capital."""
    return (equity_weight * cost_of_equity +
            debt_weight * cost_of_debt * (1 - tax_rate))
```

### Sharpe Ratio
```python
import numpy as np

def sharpe_ratio(returns, risk_free_rate, periods_per_year=252):
    """Calculate Sharpe Ratio."""
    excess_returns = returns - risk_free_rate / periods_per_year
    return np.sqrt(periods_per_year) * (excess_returns.mean() /
                                        excess_returns.std())
```

### Black-Scholes Option Pricing
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

### Portfolio Metrics
```python
import pandas as pd
import numpy as np
from typing import Dict

def calculate_portfolio_metrics(
    returns: pd.Series,
    weights: np.ndarray,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> Dict[str, float]:
    """Calculate comprehensive portfolio performance metrics."""
    portfolio_returns = (returns * weights).sum(axis=1)
    annual_return = portfolio_returns.mean() * periods_per_year
    annual_volatility = portfolio_returns.std() * np.sqrt(periods_per_year)
    sharpe = (annual_return - risk_free_rate) / annual_volatility
    cumulative = (1 + portfolio_returns).cumprod()
    running_max = cumulative.expanding().max()
    max_drawdown = ((cumulative - running_max) / running_max).min()
    return {
        'annual_return': annual_return,
        'annual_volatility': annual_volatility,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_drawdown,
    }
```

### Data Validation
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

## Best Practices

### Financial Analysis Workflow
1. Data Collection: gather reliable, timely data
2. Data Validation: check for errors, outliers, missing values
3. Analysis Framework: apply appropriate models and methods
4. Sensitivity Analysis: test key assumptions and variables
5. Documentation: clear assumptions, methodology, limitations
6. Review Process: peer review, model validation

### Model Development
1. Simplicity First: start with simple models, add complexity as needed
2. Transparency: clear logic, documented assumptions
3. Flexibility: parameterized inputs, scenario capability
4. Validation: backtesting, out-of-sample testing
5. Version Control: track changes, maintain audit trail

### Risk Management
1. Diversification: across assets, sectors, geographies
2. Limits: position limits, concentration limits, VaR limits
3. Stress Testing: historical scenarios, hypothetical scenarios
4. Monitoring: real-time risk metrics, early warning systems
5. Governance: clear policies, regular reviews

### Response Standards When Providing Financial Analysis
1. Start with context: explain market conditions and relevant factors
2. Use precise terminology: apply correct financial terms with clarity
3. Show calculations: provide formulas and step-by-step computations
4. Reference standards: cite GAAP, IFRS, or regulatory requirements
5. Include disclaimers: note assumptions, limitations, and risks
6. Never guarantee returns or outcomes without uncertainty ranges

## Integration with WorldEnergyData

### Energy Market Analysis
- Oil, gas, and power market dynamics
- Energy project economics evaluation
- Commodity price scenario modeling
- Energy transition investment assessment
- Carbon market impact calculations

### ESG Integration
- Climate-related financial risk evaluation
- Sustainability metrics analysis
- Transition scenario modeling
- Stranded asset risk assessment
- Green investment return calculations

### Sector Analysis
- Energy sector valuation models
- Utility financial analysis
- Infrastructure investment evaluation
- Clean tech opportunity assessment
- Traditional vs renewable economics

### External Data Sources
- EIA (US Energy Information Administration): https://www.eia.gov/
- IEA (International Energy Agency): https://www.iea.org/
- OPEC: https://www.opec.org/
- World Bank Energy: https://www.worldbank.org/en/topic/energy

## References

1. CFA Institute Materials — comprehensive investment knowledge
2. Options, Futures, and Other Derivatives — John Hull
3. Investment Valuation — Aswath Damodaran
4. Risk Management and Financial Institutions — John Hull
5. Energy Finance and Economics — Betty Simkins and Russell Simkins
6. Python for Finance — Yves Hilpisch
7. Quantitative Portfolio Management — Grinold and Kahn

## Usage

Invoke this skill when:
- Building or reviewing DCF, LBO, or merger financial models
- Performing energy project economics analysis (NPV, IRR, LCOE)
- Calculating portfolio risk metrics (VaR, Sharpe ratio, drawdown)
- Analyzing oil, gas, power, or carbon market dynamics
- Evaluating renewable energy project finance or PPA structures
- Assessing ESG and climate-related financial risks
- Performing option pricing or derivatives valuation
- Generating Python code for quantitative financial analysis
- Benchmarking financial performance against GIPS or CFA standards
- Modeling commodity price scenarios or hedging strategies
