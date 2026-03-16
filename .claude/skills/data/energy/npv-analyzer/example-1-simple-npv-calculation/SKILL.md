---
name: npv-analyzer-example-1-simple-npv-calculation
description: 'Sub-skill of npv-analyzer: Example 1: Simple NPV Calculation (+2).'
version: 1.0.0
category: data/energy
type: reference
scripts_exempt: true
---

# Example 1: Simple NPV Calculation (+2)

## Example 1: Simple NPV Calculation


```python
from npv_analyzer import (
    NPVCalculator, ProductionForecast, PriceAssumptions,
    FiscalTerms, CapexSchedule, OpexAssumptions
)

# Define production forecast
production = [
    ProductionForecast(year=2027, oil_mbbls=3000, gas_mmcf=2000),
    ProductionForecast(year=2028, oil_mbbls=8000, gas_mmcf=5000),
    ProductionForecast(year=2029, oil_mbbls=10000, gas_mmcf=6500),
    ProductionForecast(year=2030, oil_mbbls=9000, gas_mmcf=6000),
    ProductionForecast(year=2031, oil_mbbls=7500, gas_mmcf=5000),
]

# Define economics
prices = PriceAssumptions(oil_price_usd_bbl=70, gas_price_usd_mmbtu=3.50)
fiscal = FiscalTerms(working_interest=0.50, net_revenue_interest=0.875)
capex = CapexSchedule(schedule={2024: 200, 2025: 600, 2026: 360})
opex = OpexAssumptions(fixed_opex_usd_year=25e6, variable_opex_usd_boe=8.0)

# Calculate NPV
calc = NPVCalculator(production, prices, fiscal, capex, opex, discount_rate=0.10)

print(f"NPV @ 10%: ${calc.npv()/1e6:.1f}MM")
print(f"IRR: {calc.irr()*100:.1f}%")
print(f"Payback: {calc.payback_period():.1f} years")
```


## Example 2: Scenario Analysis


```python
from npv_analyzer import ScenarioAnalyzer, NPVReportGenerator

# Create analyzer
analyzer = ScenarioAnalyzer(production, fiscal, capex, opex)

# Run price scenarios
scenarios = analyzer.run_price_scenarios()
print("\nPrice Scenario Results:")
print(scenarios[['scenario', 'npv_mm', 'irr_pct', 'payback_years']])

# Generate tornado chart data
tornado = analyzer.tornado_chart_data(prices)
print("\nSensitivity Ranking:")
print(tornado[['variable', 'range']])

# Generate report
reporter = NPVReportGenerator(calc, analyzer)
reporter.generate_report(
    Path("reports/npv_report.html"),
    project_name="Lower Tertiary Development"
)
```


## Example 3: Monte Carlo Simulation


```python
from npv_analyzer import (
    MonteCarloSimulator, MonteCarloConfig, DistributionParams,
    DistributionType, NPVReportGenerator
)

# Create Monte Carlo simulator
mc_sim = MonteCarloSimulator(
    production=production,
    base_prices=prices,
    fiscal=fiscal,
    capex=capex,
    opex=opex,
    base_discount_rate=0.10
)

# Quick simulation with default triangular distributions
result = mc_sim.quick_simulation(
    oil_range_pct=0.30,  # ±30% oil price variation
    cost_range_pct=0.20,  # ±20% cost variation
    prod_range_pct=0.15,  # ±15% production variation
    n_iterations=5000
)

# Print P10/P50/P90 results
print(f"\nMonte Carlo Results ({len(result.npv_values):,} iterations):")
print(f"P10 NPV: ${result.p10_npv/1e6:.1f}MM (pessimistic)")
print(f"P50 NPV: ${result.p50_npv/1e6:.1f}MM (median)")
print(f"P90 NPV: ${result.p90_npv/1e6:.1f}MM (optimistic)")
print(f"Probability of positive NPV: {result.prob_positive_npv*100:.1f}%")

# Custom distribution configuration
custom_config = MonteCarloConfig(
    n_iterations=10000,
    random_seed=42,  # For reproducibility
    oil_price=DistributionParams(
        distribution=DistributionType.TRIANGULAR,
        min_value=50, mode_value=70, max_value=100
    ),
    capex_multiplier=DistributionParams(
        distribution=DistributionType.PERT,
        min_value=0.95, mode_value=1.0, max_value=1.30
    ),
    production_multiplier=DistributionParams(
        distribution=DistributionType.LOGNORMAL,
        min_value=0.6, max_value=1.15, mean=1.0, std_dev=0.15
    )
)

result = mc_sim.run_simulation(custom_config)

# Calculate Value at Risk
var_95 = mc_sim.value_at_risk(result, confidence=0.95)
cvar_95 = mc_sim.conditional_value_at_risk(result, confidence=0.95)
print(f"\nRisk Metrics:")
print(f"VaR (95%): ${var_95/1e6:.1f}MM")
print(f"CVaR (95%): ${cvar_95/1e6:.1f}MM")

# Generate report with Monte Carlo visualization
reporter = NPVReportGenerator(calc, analyzer, monte_carlo_result=result)
reporter.generate_report(
    Path("reports/npv_montecarlo_report.html"),
    project_name="Lower Tertiary Development - Risk Analysis"
)
```
