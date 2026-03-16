---
name: metocean-visualizer-core-patterns
description: 'Sub-skill of metocean-visualizer: Core Patterns.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Core Patterns

## Core Patterns


```python
"""
ABOUTME: Interactive visualization toolkit for metocean data analysis
ABOUTME: Provides chart templates for waves, wind, currents, and mapping
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional


class MetoceanChartBuilder:
    """Build interactive metocean charts with Plotly."""

    def time_series(
        self,
        df: pd.DataFrame,
        output_path: Optional[str] = None
    ) -> go.Figure:
        """Create interactive time series of wave parameters."""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,

*See sub-skills for full details.*
