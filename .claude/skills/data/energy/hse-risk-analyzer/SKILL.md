---
name: hse-risk-analyzer
description: Analyze BSEE HSE (Health, Safety, Environment) incident data for risk
  assessment. Use for operator safety scoring, incident trend analysis, compliance
  tracking, and ESG-integrated economic evaluation.
capabilities: []
requires: []
see_also:
- hse-risk-analyzer-basic-operator-safety-assessment
tags: []
category: data
version: 1.0.0
---

# Hse Risk Analyzer

## When to Use

- Assessing operator safety performance before investment decisions
- Analyzing incident trends for specific fields, facilities, or operators
- Calculating risk-adjusted economic metrics (NPV with safety factors)
- Supporting ESG (Environmental, Social, Governance) compliance requirements
- Benchmarking operator safety records across similar assets
- Identifying high-risk operators or facilities for due diligence
- Generating safety-integrated investment analysis reports

## Core Pattern

```
Query Parameters → HSE Database → Aggregate → Score → Integrate with Economics → Report
```

## Implementation

### Data Models

```python
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
import pandas as pd
import numpy as np

class IncidentType(Enum):
    """HSE incident classification types."""

*See sub-skills for full details.*
### HSE Risk Analyzer

```python
from pathlib import Path
from typing import Optional, List, Dict, Generator
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class HSERiskAnalyzer:

*See sub-skills for full details.*
### HSE Report Generator

```python
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime

class HSEReportGenerator:
    """
    Generate interactive HTML reports for HSE risk analysis.

*See sub-skills for full details.*

## YAML Configuration

```yaml
hse_analysis:
  data_source: "data/modules/hse"

  operator_analysis:
    operator: "Chevron"
    years: 5
    include_subsidiaries: true

  field_analysis:
    fields:
      - "Thunder Horse"
      - "Mars"
      - "Atlantis"
    years: 5

  risk_adjustment:
    include_penalty_exposure: true
    include_insurance_adjustment: true
    custom_discount_factors:
      LOW: 0.0
      MODERATE: 0.05
      ELEVATED: 0.10
      HIGH: 0.20


*See sub-skills for full details.*

## Integration with NPV Analysis

```python
from worldenergydata.hse import HSERiskAnalyzer
from worldenergydata.economics import NPVCalculator

# Initialize components
hse_analyzer = HSERiskAnalyzer()
npv_calc = NPVCalculator()

# Calculate base NPV
base_result = npv_calc.calculate(
    production_profile=production_df,
    price_assumptions=prices,
    fiscal_terms=terms,
    discount_rate=0.10
)

# Apply HSE risk adjustment
risk_metrics = hse_analyzer.calculate_risk_adjusted_npv(
    base_npv=base_result.npv,
    operator="Shell"
)

print(f"Base NPV: ${base_result.npv:,.0f}")
print(f"Risk-Adjusted NPV: ${risk_metrics.risk_adjusted_npv:,.0f}")
print(f"Safety Risk Category: {risk_metrics.risk_category}")
```

## ESG Compliance Output

```python
# Generate ESG-compliant safety summary
def generate_esg_summary(analyzer: HSERiskAnalyzer, operator: str) -> Dict[str, Any]:
    """Generate ESG-compliant safety summary for reporting."""
    profile = analyzer.get_operator_profile(operator)

    return {
        "operator": operator,
        "reporting_period_years": profile.years_analyzed,
        "safety_metrics": {
            "total_recordable_incident_rate": profile.trir,
            "fatalities": profile.fatalities,
            "lost_time_incidents": profile.lost_time_incidents,
            "recordable_incidents": profile.recordable_incidents,
            "safety_score": profile.safety_score,
            "risk_classification": profile.risk_category
        },
        "environmental_metrics": {
            "total_spill_volume_bbls": profile.total_spill_volume,
            "regulatory_penalties_usd": profile.total_penalties
        },
        "governance_metrics": {
            "compliance_status": "COMPLIANT" if profile.safety_score >= 70 else "REVIEW_REQUIRED"
        }
    }
```

## Notes

- Requires HSE incident data in CSV format or database connection
- Safety scores are normalized 0-100 (higher = safer)
- Risk discount factors are configurable for organization-specific policies
- Integrates with existing NPV and economic analysis modules
- Supports ESG reporting requirements for institutional investors
- TRIR calculations require exposure hours data for accuracy

## Sub-Skills

- [Basic Operator Safety Assessment (+4)](basic-operator-safety-assessment/SKILL.md)
