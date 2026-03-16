---
name: risk-assessment
version: 1.0.0
category: engineering
description: Perform probabilistic risk assessment with Monte Carlo simulations for
  offshore marine operations
see_also:
- risk-assessment-1-sample-size-selection
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

## Complete Examples

### Example 1: Complete Mooring System Risk Assessment

```python
import numpy as np
from pathlib import Path

def complete_mooring_risk_assessment(
    design_parameters: dict,
    environmental_parameters: dict,
    n_simulations: int = 10000
) -> dict:
    """

*See sub-skills for full details.*

## Well Planning Risk Context

### The Actionability Gap

Standard 5x5 risk matrices capture **what** the risk is and **how severe** it is, but not **who has the authority to mitigate it**. In well planning, this creates a systematic bias:

- Engineers write risks they can act on (operational: mud weight, BOP procedures, casing design)
- Engineers omit risks they understand but cannot control (strategic: downhole tool contracts, rig selection, fleet capacity)
- The risk register becomes operationally complete but strategically incomplete
### Risk Authority Tiers

When building risk registers for well planning, classify every risk into one of three tiers:

| Tier | Authority | Decision Sits With | Example Risks |
|------|-----------|-------------------|---------------|
| **Operational** | Project team | Drilling engineer / superintendent | Lost circulation, wellbore instability, swelling clay, mud contamination |
| **Tactical** | Cross-functional | Project manager + discipline leads | Casing design changes, BOP stack configuration, completion sequence |
| **Strategic** | Outside project | Procurement / fleet / corporate | Downhole tool availability, rig hook load capacity, contract terms, regulatory changes |
### Structured Escalation for Strategic Risks

When a risk falls outside project authority, convert it from a vague register entry into a structured escalation:

```
Risk: [Formation X] requires [capability Y] that current [tool/rig/contract] does not provide.
Impact if unaddressed: [specific consequence — NPT days, sidetrack probability, well objective at risk]
Mitigation lever: [what needs to change — new tool contract, different rig class, regulatory exemption]
Decision owner: [organizational function — procurement, fleet management, regulatory affairs]
Decision timeline: [when the decision must be made relative to spud date]
```

This reframes "we need a better downhole tool" into an actionable request with a clear owner, deadline, and consequence.
### Risk Influence Map

Categorize the project's relationship to each risk:

- **Controls**: Project team can directly mitigate (operational risks)
- **Influences**: Project team provides input but doesn't decide (tactical risks)
- **Observes**: Project team identifies and escalates but has no lever (strategic risks)

A well planning risk register should have risks in all three categories. If the register contains only operational risks, the strategic dimension is being suppressed — not because those risks don't exist, but because the project lacks empowerment to address them.
### Integration with Quantitative Assessment

The Monte Carlo and reliability tools in this skill quantify operational risks effectively. For strategic risks, the quantitative output serves a different purpose — it provides the **business case for escalation**:

```python
# Example: Quantify cost impact of rig capability gap
# This output goes into the escalation template, not the project risk register
rig_gap_risk = assess_hazards([
    Hazard(
        id='STR-001',
        description='Rig hookload insufficient for 9-5/8" casing at TD',
        severity=Severity.MAJOR,          # sidetrack or redesign required

*See sub-skills for full details.*

## Resources

### Textbooks

- Ang, A.H-S., Tang, W.H. (2007). *Probability Concepts in Engineering*
- Melchers, R.E., Beck, A.T. (2018). *Structural Reliability Analysis and Prediction*
- DNV (2021). *DNVGL-RP-C205: Environmental Conditions and Environmental Loads*
### Standards

- **DNV-RP-C205**: Environmental conditions and environmental loads
- **DNV-RP-C206**: Fatigue methodology of offshore ships
- **ISO 2394**: General principles on reliability for structures
- **API RP 2A**: Planning, designing and constructing fixed offshore platforms
### Software

- **@RISK**: Monte Carlo simulation add-in for Excel
- **Crystal Ball**: Oracle's risk analysis software
- **OpenTURNS**: Open source library for uncertainty quantification
- **scipy.stats**: Python statistical distributions

---

**Use this skill for:** Expert probabilistic risk assessment and reliability analysis for marine and offshore systems with comprehensive uncertainty quantification.

## Sub-Skills

- [1. Sample Size Selection (+1)](1-sample-size-selection/SKILL.md)
