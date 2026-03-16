---
name: sodir-data-extractor
description: Extract and process Norwegian Petroleum Directorate field and production
  data from SODIR
capabilities: []
requires: []
see_also:
- sodir-data-extractor-best-practices
tags: []
category: data
version: 1.0.0
---

# Sodir Data Extractor

## When to Use This Skill

Use this skill when you need to:
- Extract Norwegian continental shelf field data
- Query SODIR production statistics
- Compare Norwegian fields with GOM fields
- Build cross-basin analysis datasets
- Access historical NCS field performance

## Core Pattern

```python
"""
ABOUTME: Norwegian Petroleum Directorate (SODIR) data extraction
ABOUTME: Provides field and production data from the Norwegian Continental Shelf
"""

from dataclasses import dataclass
from typing import List, Optional
import requests
import pandas as pd


@dataclass
class SODIRField:
    """Norwegian field information."""
    field_name: str
    discovery_year: int
    status: str  # PRODUCING, SHUT DOWN, etc.
    operator: str
    area_name: str  # Quadrant/block area
    water_depth_m: float
    recoverable_oil_mmbbl: float
    recoverable_gas_bcm: float



*See sub-skills for full details.*

## YAML Configuration Template

```yaml
# config/input/sodir-extraction.yaml

metadata:
  feature_name: "sodir-extraction"
  created: "2025-01-15"

data_source:
  type: "sodir"
  cache_enabled: true
  cache_ttl_days: 7

query:
  fields:
    - "JOHAN SVERDRUP"
    - "TROLL"
    - "EKOFISK"
  status_filter: "PRODUCING"
  start_year: 2015
  end_year: null

output:
  format: "csv"
  path: "data/sodir/"
  include_metadata: true
```

## CLI Usage

```bash
# Extract field list
python -m worldenergydata.sodir \
    --action list-fields \
    --status PRODUCING \
    --output data/sodir/fields.csv

# Get production data
python -m worldenergydata.sodir \
    --action production \
    --field "JOHAN SVERDRUP" \
    --start-year 2019 \
    --output data/sodir/johan_sverdrup.csv
```

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)
