---
name: economic-sensitivity-analyzer-cli-usage
description: 'Sub-skill of economic-sensitivity-analyzer: CLI Usage.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# CLI Usage

## CLI Usage


```bash
# Run spider diagram analysis
uv run python -c "
from worldenergydata.economics.sensitivity import SpiderDiagramAnalyzer
# ... analysis code
"

# Generate sensitivity dashboard
uv run python -m worldenergydata.cli sensitivity-dashboard \
    --config config/sensitivity_config.yaml \
    --output reports/sensitivity_dashboard.html

# Quick breakeven analysis
uv run python -c "
from worldenergydata.economics.sensitivity import BreakevenAnalyzer
analyzer = BreakevenAnalyzer(npv_calc)
result = analyzer.find_breakeven('oil_price', 70, range_pct=0.5, unit='\$/bbl')
print(f'Breakeven oil price: \${result.breakeven_value:.2f}/bbl')
"
```
