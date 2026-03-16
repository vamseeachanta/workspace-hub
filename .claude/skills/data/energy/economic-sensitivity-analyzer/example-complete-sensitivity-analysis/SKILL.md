---
name: economic-sensitivity-analyzer-example-complete-sensitivity-analysis
description: 'Sub-skill of economic-sensitivity-analyzer: Example: Complete Sensitivity
  Analysis.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Example: Complete Sensitivity Analysis

## Example: Complete Sensitivity Analysis


```python
# ABOUTME: Complete example of multi-dimensional sensitivity analysis
# ABOUTME: Shows spider diagram, surface, breakeven, and scenario comparison

from worldenergydata.economics.sensitivity import (
    SensitivityParameter,
    SpiderDiagramAnalyzer,
    SensitivitySurfaceAnalyzer,
    BreakevenAnalyzer,
    ScenarioMatrixAnalyzer,
    ScenarioDefinition,
    SensitivityDashboard,
    ParameterType
)
import numpy as np

# Define NPV calculator (simplified example)
def calculate_npv(params: dict) -> float:
    """Simple NPV calculator for demonstration."""
    oil_price = params.get('oil_price', 70)
    gas_price = params.get('gas_price', 3.5)
    capex = params.get('capex', 500)
    opex_per_boe = params.get('opex_per_boe', 15)
    discount_rate = params.get('discount_rate', 0.10)


*See sub-skills for full details.*
