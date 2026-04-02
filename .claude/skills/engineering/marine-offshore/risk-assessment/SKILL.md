---
name: risk-assessment
version: 1.0.0
category: engineering
description: Perform probabilistic risk assessment with Monte Carlo simulations for
  offshore marine operations
type: reference
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Risk Assessment

## When to Use This Skill

Use this skill when you need to:
- Perform Monte Carlo simulations for uncertainty quantification
- Calculate system reliability and failure probabilities
- Conduct sensitivity analysis to identify critical parameters
- Create risk matrices for hazard assessment
- Perform probabilistic design and analysis
- Quantify uncertainties in marine operations
- Make decisions under uncertainty with risk metrics
- Validate designs against reliability targets

## Core Knowledge Areas

### 1. Monte Carlo Simulation

Basic Monte Carlo framework:

```python
import numpy as np
from scipy import stats
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Optional
import pandas as pd

@dataclass

*See sub-skills for full details.*
### 2. Reliability Analysis

Calculate reliability and failure probability:

```python
def calculate_reliability(
    response_data: np.ndarray,
    limit_state: float,
    mode: str = 'less_than'
) -> dict:
    """
    Calculate reliability from Monte Carlo results.

*See sub-skills for full details.*
### 3. Sensitivity Analysis

Identify critical parameters:

```python
def sensitivity_analysis_correlation(
    inputs: Dict[str, np.ndarray],
    output: np.ndarray
) -> pd.DataFrame:
    """
    Sensitivity analysis using correlation coefficients.


*See sub-skills for full details.*
### 4. Risk Matrices and Hazard Assessment

```python
from enum import Enum

class Severity(Enum):
    """Consequence severity levels."""
    NEGLIGIBLE = 1
    MINOR = 2
    MODERATE = 3
    MAJOR = 4
    CATASTROPHIC = 5

*See sub-skills for full details.*
### 5. Extreme Value Analysis

```python
from scipy.stats import genextreme

def fit_extreme_value_distribution(
    data: np.ndarray,
    method: str = 'gev'
) -> dict:
    """
    Fit extreme value distribution to data.


*See sub-skills for full details.*

## Complete Examples & Well Planning Context

See [references/examples.md](references/examples.md) for complete mooring system risk assessment examples and well planning risk context (actionability gap, risk authority tiers, structured escalation, risk influence maps).

## Resources

See [references/resources.md](references/resources.md) for textbooks, standards, and software references.

---

**Use this skill for:** Expert probabilistic risk assessment and reliability analysis for marine and offshore systems with comprehensive uncertainty quantification.

## Sub-Skills

- [1. Sample Size Selection (+1)](1-sample-size-selection/SKILL.md)
