---
name: economic-sensitivity-analyzer-yaml-configuration
description: 'Sub-skill of economic-sensitivity-analyzer: YAML Configuration.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# YAML Configuration

## YAML Configuration


```yaml
# sensitivity_config.yaml
meta:
  mode: sensitivity_analysis
  output_format: html_dashboard

analysis:
  base_case:
    oil_price: 70.0          # $/bbl
    gas_price: 3.50          # $/mcf
    capex: 500.0             # MM$
    opex_per_boe: 15.0       # $/boe
    discount_rate: 0.10      # 10%
    working_interest: 0.80   # 80%

  spider_diagram:
    enabled: true
    parameters:
      - name: oil_price
        display_name: "Oil Price"
        variations: [-30, -20, -10, 0, 10, 20, 30]
      - name: gas_price
        display_name: "Gas Price"
        variations: [-30, -20, -10, 0, 10, 20, 30]
      - name: capex

*See sub-skills for full details.*
