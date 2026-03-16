---
name: economic-sensitivity-analyzer-sensitivityparameter
description: 'Sub-skill of economic-sensitivity-analyzer: SensitivityParameter (+6).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# SensitivityParameter (+6)

## SensitivityParameter


```python
# ABOUTME: Defines a parameter for sensitivity analysis with range and display settings
# ABOUTME: Supports linear and percentage-based parameter variations

from dataclasses import dataclass, field
from typing import List, Optional, Callable
from enum import Enum
import numpy as np



*See sub-skills for full details.*

## SpiderDiagramAnalyzer


```python
# ABOUTME: Creates spider (radar) diagrams showing multi-parameter sensitivity
# ABOUTME: Normalizes NPV changes to percentage basis for fair comparison

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Callable
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


*See sub-skills for full details.*

## SensitivitySurfaceAnalyzer


```python
# ABOUTME: Creates 2D sensitivity surfaces (contour/heatmaps) for two-variable analysis
# ABOUTME: Shows NPV as function of two parameters simultaneously

@dataclass
class SurfaceResult:
    """Results from 2D surface analysis."""
    param1_name: str
    param1_values: np.ndarray
    param2_name: str

*See sub-skills for full details.*

## BreakevenAnalyzer


```python
# ABOUTME: Calculates and visualizes breakeven prices for oil, gas, and costs
# ABOUTME: Supports multi-commodity breakeven analysis and sensitivity to other parameters

@dataclass
class BreakevenResult:
    """Results from breakeven analysis."""
    parameter_name: str
    breakeven_value: Optional[float]
    unit: str

*See sub-skills for full details.*

## ScenarioMatrixAnalyzer


```python
# ABOUTME: Creates scenario comparison matrices for management presentations
# ABOUTME: Supports low/mid/high scenarios with customizable probability weighting

@dataclass
class ScenarioDefinition:
    """Definition of a single scenario."""
    name: str
    parameters: Dict[str, float]
    probability: float = 0.0  # For expected value calculation

*See sub-skills for full details.*

## DecisionTreeAnalyzer


```python
# ABOUTME: Creates decision tree analysis for staged investments
# ABOUTME: Calculates expected value considering probabilities and decision points

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
import plotly.graph_objects as go


@dataclass

*See sub-skills for full details.*

## SensitivityDashboard


```python
# ABOUTME: Combines all sensitivity analyses into comprehensive dashboard
# ABOUTME: Creates executive-ready reports with multiple visualization types

from typing import Dict, List, Optional, Callable
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class SensitivityDashboard:

*See sub-skills for full details.*
