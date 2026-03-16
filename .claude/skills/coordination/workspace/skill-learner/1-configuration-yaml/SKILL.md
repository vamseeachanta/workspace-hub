---
name: skill-learner-1-configuration-yaml
description: 'Sub-skill of skill-learner: 1. Configuration (YAML) (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. Configuration (YAML) (+3)

## 1. Configuration (YAML)


```yaml
calculation:
  type: npv
  discount_rates: [0.05, 0.08, 0.10, 0.12]
  cash_flows: data/cash_flows.csv
  scenarios:
    - base
    - optimistic
    - pessimistic
```

## 2. Calculator Module (Python)


```python
class NPVCalculator:
    def calculate(self, cash_flows, discount_rate):
        return np.npv(discount_rate, cash_flows)

    def multi_scenario(self, scenarios, rates):
        results = {}
        for scenario in scenarios:
            for rate in rates:
                npv = self.calculate(scenario.cash_flows, rate)
                results[(scenario.name, rate)] = npv
        return results
```

## 3. Visualization (Plotly)


Interactive multi-scenario comparison with hover tooltips.

## 4. Execution (Bash)


```bash
./scripts/run_npv_analysis.sh config/npv.yaml
```
