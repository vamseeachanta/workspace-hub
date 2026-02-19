---
name: energy-data-visualizer
description: Energy Data Visualizer (user)
capabilities: []
requires: []
see_also: []
---

# Energy Data Visualizer Skill

> Interactive visualization for oil & gas data analysis using Plotly

## When to Use This Skill

Use this skill when you need to:
- Create production time series charts
- Visualize decline curves and forecasts
- Build economic scenario comparison charts
- Generate field/block comparison visualizations
- Create interactive HTML dashboards

## Core Pattern

```python
"""
ABOUTME: Interactive visualization toolkit for energy data analysis
ABOUTME: Provides chart templates for production, economics, and mapping
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


class ProductionChartBuilder:
    """Build interactive production charts."""

    def production_time_series(
        self,
        df: pd.DataFrame,
        date_col: str = "date",
        rate_cols: list = ["oil_bopd", "gas_mcfd"]
    ) -> go.Figure:
        """Create production rate vs time chart."""
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

        colors = {"oil_bopd": "#2E7D32", "gas_mcfd": "#D32F2F"}

        for col in rate_cols:
            if col in df.columns:
                fig.add_trace(
                    go.Scatter(x=df[date_col], y=df[col], name=col),
                    row=1, col=1
                )

        fig.update_layout(title="Production History", hovermode="x unified")
        return fig

    def decline_curve_plot(
        self,
        actual_df: pd.DataFrame,
        forecast_df: pd.DataFrame = None,
        log_scale: bool = True
    ) -> go.Figure:
        """Create decline curve with forecast overlay."""
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=actual_df["months"],
            y=actual_df["rate"],
            mode="markers",
            name="Actual"
        ))

        if forecast_df is not None:
            fig.add_trace(go.Scatter(
                x=forecast_df["months"],
                y=forecast_df["p50"],
                mode="lines",
                name="P50 Forecast"
            ))

        if log_scale:
            fig.update_yaxes(type="log")

        return fig


class EconomicsChartBuilder:
    """Build economic analysis charts."""

    def cash_flow_waterfall(self, components: dict) -> go.Figure:
        """Create waterfall chart for cash flow breakdown."""
        names = list(components.keys()) + ["Net"]
        values = list(components.values())
        values.append(sum(values))

        fig = go.Figure(go.Waterfall(
            x=names,
            y=values,
            measure=["relative"] * (len(values)-1) + ["total"]
        ))

        fig.update_layout(title="Cash Flow Waterfall")
        return fig

    def npv_sensitivity_tornado(
        self,
        sensitivities: dict,
        base_npv: float
    ) -> go.Figure:
        """Create tornado chart for NPV sensitivity."""
        params = list(sensitivities.keys())
        lows = [s["low"] - base_npv for s in sensitivities.values()]
        highs = [s["high"] - base_npv for s in sensitivities.values()]

        fig = go.Figure()
        fig.add_trace(go.Bar(y=params, x=lows, orientation="h", name="Low"))
        fig.add_trace(go.Bar(y=params, x=highs, orientation="h", name="High"))

        fig.update_layout(barmode="overlay", title="NPV Sensitivity")
        return fig
```

## Usage Example

```python
from worldenergydata.visualize import ProductionChartBuilder
import pandas as pd

# Load data
df = pd.read_csv("production.csv", parse_dates=["date"])

# Create chart
builder = ProductionChartBuilder()
fig = builder.production_time_series(df)
fig.write_html("reports/production.html")
```

## Best Practices

1. Use interactive Plotly charts, not static matplotlib
2. Include hover tooltips with relevant data
3. Export as standalone HTML files
4. Use consistent color schemes
