---
name: field-analyzer
description: Field Analyzer (user)
capabilities: []
requires: []
see_also: []
---

# Field Analyzer Skill

> Deepwater field-specific analysis for major GOM developments

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
LOWER_TERTIARY_FIELDS = {
    "ANCHOR": FieldDefinition(
        name="Anchor",
        operator="Chevron",
        development_type="FPSO",
        water_depth_ft=5200,
        first_production="2024-08",
        blocks=["GC 807", "GC 808"]
    ),
    "JACK": FieldDefinition(
        name="Jack",
        operator="Chevron",
        development_type="SPAR",
        water_depth_ft=7000,
        first_production="2014-12",
        blocks=["WR 759"]
    ),
    "ST_MALO": FieldDefinition(
        name="St. Malo",
        operator="Chevron",
        development_type="SPAR",
        water_depth_ft=7000,
        first_production="2014-11",
        blocks=["WR 678"]
    ),
    "JULIA": FieldDefinition(
        name="Julia",
        operator="ExxonMobil",
        development_type="SUBSEA",
        water_depth_ft=7000,
        first_production="2016-10",
        blocks=["WR 627"]
    ),
    "KASKIDA": FieldDefinition(
        name="Kaskida",
        operator="BP",
        development_type="TBD",
        water_depth_ft=5800,
        first_production="TBD",
        blocks=["KC 292"]
    )
}


class FieldAnalyzer:
    """
    Analyze GOM fields by aggregating well-level data.

    Supports predefined fields and custom field definitions.
    """

    def __init__(self):
        self.field_definitions = LOWER_TERTIARY_FIELDS.copy()

    def add_field(self, definition: FieldDefinition) -> None:
        """Add custom field definition."""
        self.field_definitions[definition.name.upper()] = definition

    def get_field_wells(self, field_name: str) -> List[str]:
        """Get API numbers for wells in a field."""
        field_def = self.field_definitions.get(field_name.upper())
        if not field_def:
            raise ValueError(f"Unknown field: {field_name}")

        # Query BSEE for wells in field blocks
        from worldenergydata.bsee.data import query_wells_by_block

        all_apis = []
        for block in field_def.blocks:
            apis = query_wells_by_block(block)
            all_apis.extend(apis)

        return list(set(all_apis))

    def aggregate_field_production(
        self,
        field_name: str,
        start_date: str = None,
        end_date: str = None
    ) -> pd.DataFrame:
        """
        Aggregate production across all wells in a field.

        Returns monthly field-level production totals.
        """
        from worldenergydata.bsee.data import get_production_data

        field_def = self.field_definitions.get(field_name.upper())
        if not field_def:
            raise ValueError(f"Unknown field: {field_name}")

        # Get production for each well
        well_dfs = []
        for api in self.get_field_wells(field_name):
            try:
                df = get_production_data(api_number=api)
                df["api_number"] = api
                well_dfs.append(df)
            except Exception:
                continue

        if not well_dfs:
            return pd.DataFrame()

        # Combine and aggregate
        combined = pd.concat(well_dfs, ignore_index=True)

        # Group by month
        combined["year_month"] = combined["date"].dt.to_period("M")

        field_production = combined.groupby("year_month").agg({
            "oil_bbl": "sum",
            "gas_mcf": "sum",
            "water_bbl": "sum",
            "api_number": "nunique"
        }).rename(columns={"api_number": "active_wells"})

        field_production["field_name"] = field_name
        field_production = field_production.reset_index()
        field_production["date"] = field_production["year_month"].dt.to_timestamp()

        return field_production

    def compare_fields(
        self,
        field_names: List[str],
        metric: str = "oil_bbl"
    ) -> pd.DataFrame:
        """
        Compare production across multiple fields.

        Aligns by months on production for fair comparison.
        """
        field_dfs = []

        for name in field_names:
            df = self.aggregate_field_production(name)
            if not df.empty:
                # Add months on production
                df = df.sort_values("date")
                df["months_on_prod"] = range(len(df))
                df = df[["months_on_prod", metric, "field_name"]]
                field_dfs.append(df)

        if not field_dfs:
            return pd.DataFrame()

        # Pivot for comparison
        combined = pd.concat(field_dfs)
        comparison = combined.pivot(
            index="months_on_prod",
            columns="field_name",
            values=metric
        )

        return comparison

    def field_economics_summary(self, field_name: str) -> Dict:
        """
        Generate economics summary for a field.

        Returns key metrics and KPIs.
        """
        field_def = self.field_definitions.get(field_name.upper())
        production = self.aggregate_field_production(field_name)

        if production.empty:
            return {}

        total_oil = production["oil_bbl"].sum()
        total_gas = production["gas_mcf"].sum()
        peak_oil = production["oil_bbl"].max()
        months_producing = len(production)

        return {
            "field_name": field_name,
            "operator": field_def.operator,
            "development_type": field_def.development_type,
            "water_depth_ft": field_def.water_depth_ft,
            "first_production": field_def.first_production,
            "cumulative_oil_mmbbl": total_oil / 1_000_000,
            "cumulative_gas_bcf": total_gas / 1_000_000,
            "peak_oil_bopd": peak_oil / 30,
            "months_producing": months_producing,
            "active_wells": production["active_wells"].iloc[-1] if len(production) > 0 else 0
        }
```

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
    operator: "Operator Name"
    development_type: "SUBSEA"
    water_depth_ft: 6000
    blocks: ["GC 100", "GC 101"]

output:
  format: "html"
  path: "reports/fields/"
  include_comparison_chart: true
```

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

## Best Practices

1. Use official BSEE block designations for field definitions
2. Validate well assignments periodically as new wells come online
3. Exclude wells with anomalous data (testing, workovers)
4. Align comparison by months on production, not calendar date
