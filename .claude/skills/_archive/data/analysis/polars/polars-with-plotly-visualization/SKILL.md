---
name: polars-polars-with-plotly-visualization
description: 'Sub-skill of polars: Polars with Plotly Visualization (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Polars with Plotly Visualization (+1)

## Polars with Plotly Visualization


```python
import polars as pl
import plotly.express as px
import plotly.graph_objects as go

def create_dashboard_data(df: pl.DataFrame) -> dict:
    """Prepare data for Plotly dashboard."""

    # Time series for line chart
    daily_trend = (
        df
        .group_by("date")
        .agg([
            pl.col("revenue").sum().alias("revenue"),
            pl.col("orders").sum().alias("orders")
        ])
        .sort("date")
        .to_pandas()  # Convert for Plotly
    )

    # Category breakdown for pie chart
    category_breakdown = (
        df
        .group_by("category")
        .agg(pl.col("revenue").sum())
        .sort("revenue", descending=True)
        .to_pandas()
    )

    # Regional comparison for bar chart
    regional = (
        df
        .group_by("region")
        .agg([
            pl.col("revenue").sum(),
            pl.col("orders").count()
        ])
        .to_pandas()
    )

    return {
        "daily_trend": daily_trend,
        "category_breakdown": category_breakdown,
        "regional": regional
    }

def plot_time_series(df_pandas, x_col, y_col, title):
    """Create interactive time series plot."""
    fig = px.line(
        df_pandas,
        x=x_col,
        y=y_col,
        title=title
    )
    fig.update_layout(hovermode="x unified")
    return fig
```


## Polars with Pandas Interop


```python
import polars as pl
import pandas as pd

# Convert Polars to Pandas (when needed for libraries that require pandas)
polars_df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
pandas_df = polars_df.to_pandas()

# Convert Pandas to Polars
pandas_df = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
polars_df = pl.from_pandas(pandas_df)

# Efficient conversion with zero-copy when possible
polars_df = pl.from_pandas(pandas_df, nan_to_null=True)

# Use Polars for heavy lifting, Pandas for compatibility
def hybrid_pipeline(input_path: str):
    """Use Polars for processing, Pandas for visualization libraries."""

    # Heavy processing with Polars
    processed = (
        pl.scan_parquet(input_path)
        .filter(pl.col("value") > 0)
        .group_by("category")
        .agg([
            pl.col("value").sum(),
            pl.col("value").mean().alias("avg_value")
        ])
        .collect()
    )

    # Convert for seaborn/matplotlib
    import seaborn as sns
    pandas_df = processed.to_pandas()
    sns.barplot(data=pandas_df, x="category", y="value")

    return processed
```
