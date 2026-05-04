---
name: dash-example-1-sales-analytics-dashboard
description: 'Sub-skill of dash: Example 1: Sales Analytics Dashboard (+2).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Example 1: Sales Analytics Dashboard (+2)

## Example 1: Sales Analytics Dashboard


```python
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


*See sub-skills for full details.*

## Example 2: Real-Time Monitoring Dashboard


```python
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from collections import deque
import random
from datetime import datetime

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])


*See sub-skills for full details.*

## Example 3: Data Table with AG Grid


```python
from dash import Dash, html, callback, Output, Input
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Generate sample data

*See sub-skills for full details.*
