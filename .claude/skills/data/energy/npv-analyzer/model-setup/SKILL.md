---
name: npv-analyzer-model-setup
description: 'Sub-skill of npv-analyzer: Model Setup (+3).'
version: 1.0.0
category: data/energy
type: reference
scripts_exempt: true
---

# Model Setup (+3)

## Model Setup

- Use consistent units throughout (USD, bbls, MCF)
- Validate production forecasts against reservoir studies
- Document all assumptions in YAML configs
- Version control economic parameters


## Sensitivity Analysis

- Always run multiple price scenarios
- Include cost and schedule sensitivities
- Identify breakeven prices for investment decisions
- Document uncertainty ranges


## Reporting

- Include summary metrics prominently
- Show cash flow timing clearly
- Compare against investment criteria (hurdle rate, payback limits)
- Archive analysis with assumptions


## Monte Carlo Analysis

- Use 5,000-10,000 iterations for stable P10/P50/P90
- Choose appropriate distributions (PERT for expert estimates, triangular for simple ranges)
- CAPEX typically skewed toward overruns (use asymmetric distributions)
- Production typically skewed toward underperformance
- Set random seed for reproducible results
- Calculate VaR and CVaR for risk management
- Report probability of positive NPV for investment decisions
