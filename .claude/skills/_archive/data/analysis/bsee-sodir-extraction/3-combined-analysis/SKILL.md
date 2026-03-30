---
name: bsee-sodir-extraction-3-combined-analysis
description: 'Sub-skill of bsee-sodir-extraction: 3. Combined Analysis.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 3. Combined Analysis

## 3. Combined Analysis


**Cross-Basin Comparison:**
```python
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


def compare_gom_norway_production(
    gom_data: pd.DataFrame,
    norway_data: pd.DataFrame,
    output_dir: Path = Path("reports")
) -> None:
    """
    Create comparative analysis of GOM vs Norway production.

    Args:
        gom_data: BSEE production data
        norway_data: SODIR production data
        output_dir: Report output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Aggregate by year
    gom_annual = gom_data.groupby("PRODUCTION_YEAR").agg({
        "OIL_BBL": "sum",
        "GAS_MCF": "sum"
    }).reset_index()
    gom_annual["REGION"] = "Gulf of Mexico"
    gom_annual["OIL_MM_BBL"] = gom_annual["OIL_BBL"] / 1e6
    gom_annual["GAS_BCF"] = gom_annual["GAS_MCF"] / 1e6

    norway_annual = norway_data.groupby("year").agg({
        "oilProduction": "sum",
        "gasProduction": "sum"
    }).reset_index()
    norway_annual.columns = ["PRODUCTION_YEAR", "OIL_MM_BBL", "GAS_BCF"]
    norway_annual["REGION"] = "Norway"

    # Create comparison chart
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Oil Production (MM BBL)", "Gas Production (BCF)"]
    )

    # Oil production
    fig.add_trace(
        go.Bar(
            x=gom_annual["PRODUCTION_YEAR"],
            y=gom_annual["OIL_MM_BBL"],
            name="GOM Oil",
            marker_color="blue"
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            x=norway_annual["PRODUCTION_YEAR"],
            y=norway_annual["OIL_MM_BBL"],
            name="Norway Oil",
            marker_color="red"
        ),
        row=1, col=1
    )

    # Gas production
    fig.add_trace(
        go.Bar(
            x=gom_annual["PRODUCTION_YEAR"],
            y=gom_annual["GAS_BCF"],
            name="GOM Gas",
            marker_color="lightblue"
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(
            x=norway_annual["PRODUCTION_YEAR"],
            y=norway_annual["GAS_BCF"],
            name="Norway Gas",
            marker_color="pink"
        ),
        row=1, col=2
    )

    fig.update_layout(
        title="Gulf of Mexico vs Norway: Offshore Production Comparison",
        barmode="group",
        height=500
    )

    fig.write_html(output_dir / "gom_norway_comparison.html")
    print(f"Report saved to {output_dir / 'gom_norway_comparison.html'}")
```
