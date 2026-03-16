---
name: field-analyzer
description: Deepwater field-specific analysis for major Gulf of Mexico developments
  and production aggregation
capabilities: []
requires: []
see_also:
- field-analyzer-best-practices
tags: []
category: data
version: 1.0.0
---

# Field Analyzer

## When to Use This Skill

Use this skill when you need to:
- Analyze specific deepwater fields (Anchor, Julia, Jack, St. Malo)
- Aggregate production by field across multiple wells/leases
- Compare field performance and economics
- Build field-level type curves
- Track development history and milestones

## Core Pattern

```python
"""
ABOUTME: Field-level analysis for major GOM deepwater developments
ABOUTME: Aggregates wells by field and provides field-specific analytics
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import pandas as pd


@dataclass
class FieldDefinition:
    """Definition of a GOM field."""
    name: str
    operator: str
    development_type: str  # FPSO, TLP, SPAR, SUBSEA
    water_depth_ft: float
    first_production: str  # YYYY-MM
    api_numbers: List[str] = field(default_factory=list)
    lease_numbers: List[str] = field(default_factory=list)
    blocks: List[str] = field(default_factory=list)


# Known Lower Tertiary fields

*See sub-skills for full details.*

## YAML Configuration Template

```yaml
# config/input/field-analysis.yaml

metadata:
  feature_name: "field-analysis"
  created: "2025-01-15"

# Fields to analyze
fields:
  - name: "ANCHOR"
    include_forecast: true
  - name: "JACK"
    include_forecast: true
  - name: "ST_MALO"
    include_forecast: true

# Analysis options
analysis:
  aggregate_by: "month"
  calculate_type_curve: true
  compare_vs_plan: false

# Custom field definitions (optional)
custom_fields:
  - name: "MY_FIELD"

*See sub-skills for full details.*

## CLI Usage

```bash
# Analyze single field
python -m worldenergydata.field_analyzer \
    --field ANCHOR \
    --output reports/anchor_analysis.html

# Compare multiple fields
python -m worldenergydata.field_analyzer \
    --compare JACK ST_MALO JULIA \
    --metric oil_bbl \
    --output reports/lt_comparison.html
```

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)
