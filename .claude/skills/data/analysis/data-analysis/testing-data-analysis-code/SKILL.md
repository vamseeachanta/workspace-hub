---
name: data-analysis-testing-data-analysis-code
description: 'Sub-skill of data-analysis: Testing Data Analysis Code.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Testing Data Analysis Code

## Testing Data Analysis Code


```python
import pytest
import polars as pl

def test_aggregation_logic():
    """Test aggregation produces expected results."""
    test_data = pl.DataFrame({
        "category": ["A", "A", "B"],
        "value": [100, 200, 150]
    })

    result = aggregate_by_category(test_data)

    assert result.filter(pl.col("category") == "A")["total"][0] == 300
    assert result.filter(pl.col("category") == "B")["total"][0] == 150

def test_dashboard_callback():
    """Test dashboard callback returns valid figures."""
    from dash.testing.composite import DashComposite

    # Test callback outputs are valid plotly figures
    main, pie, bar = update_charts("revenue")

    assert main.data is not None
    assert pie.data is not None

*See sub-skills for full details.*
