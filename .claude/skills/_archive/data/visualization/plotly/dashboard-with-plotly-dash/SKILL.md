---
name: plotly-dashboard-with-plotly-dash
description: 'Sub-skill of plotly: Dashboard with Plotly Dash.'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Dashboard with Plotly Dash

## Dashboard with Plotly Dash


```python
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Load data
df = pd.read_csv('../data/processed/dashboard_data.csv')

# Initialize app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1('Interactive Dashboard'),

    html.Div([
        html.Label('Select Category:'),
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': cat, 'value': cat} for cat in df['category'].unique()],
            value=df['category'].unique()[0]
        )
    ], style={'width': '50%'}),


*See sub-skills for full details.*
