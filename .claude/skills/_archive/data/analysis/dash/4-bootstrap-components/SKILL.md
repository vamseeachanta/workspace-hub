---
name: dash-4-bootstrap-components
description: 'Sub-skill of dash: 4. Bootstrap Components.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 4. Bootstrap Components

## 4. Bootstrap Components


**Using Dash Bootstrap Components:**
```python
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Initialize with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data
df = pd.DataFrame({
    "date": pd.date_range("2025-01-01", periods=100),
    "sales": [100 + i * 2 + (i % 7) * 10 for i in range(100)],
    "orders": [50 + i + (i % 5) * 5 for i in range(100)]
})

# Layout with Bootstrap components
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Sales Dashboard", className="text-primary"),
            html.P("Interactive analytics powered by Dash", className="lead")
        ])
    ], className="mb-4"),

    # Metrics row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Sales", className="card-title"),
                    html.H2(f"${df['sales'].sum():,}", className="text-success")
                ])
            ])
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Orders", className="card-title"),
                    html.H2(f"{df['orders'].sum():,}", className="text-info")
                ])
            ])
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Avg Order Value", className="card-title"),
                    html.H2(f"${df['sales'].sum() / df['orders'].sum():.2f}", className="text-warning")
                ])
            ])
        ], md=4)
    ], className="mb-4"),

    # Filters
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filters"),
                dbc.CardBody([
                    dbc.Label("Date Range"),
                    dcc.DatePickerRange(
                        id="date-range",
                        start_date=df["date"].min(),
                        end_date=df["date"].max(),
                        className="mb-3"
                    ),
                    dbc.Label("Metric"),
                    dcc.Dropdown(
                        id="metric-dropdown",
                        options=[
                            {"label": "Sales", "value": "sales"},
                            {"label": "Orders", "value": "orders"}
                        ],
                        value="sales"
                    )
                ])
            ])
        ], md=3),
        dbc.Col([
            dcc.Graph(id="main-chart")
        ], md=9)
    ]),

    # Tabs
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="Daily Data", tab_id="daily"),
                dbc.Tab(label="Summary", tab_id="summary")
            ], id="tabs", active_tab="daily"),
            html.Div(id="tab-content", className="mt-3")
        ])
    ], className="mt-4")

], fluid=True)

@callback(
    Output("main-chart", "figure"),
    [Input("date-range", "start_date"),
     Input("date-range", "end_date"),
     Input("metric-dropdown", "value")]
)
def update_chart(start_date, end_date, metric):
    filtered = df[
        (df["date"] >= start_date) &
        (df["date"] <= end_date)
    ]

    fig = px.line(
        filtered,
        x="date",
        y=metric,
        title=f"{metric.title()} Over Time"
    )
    fig.update_layout(template="plotly_white")

    return fig

@callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab(tab):
    if tab == "daily":
        return dbc.Table.from_dataframe(
            df.tail(10),
            striped=True,
            bordered=True,
            hover=True
        )
    elif tab == "summary":
        return html.Div([
            html.P(f"Total Records: {len(df)}"),
            html.P(f"Date Range: {df['date'].min()} to {df['date'].max()}"),
            html.P(f"Sales Range: ${df['sales'].min()} - ${df['sales'].max()}")
        ])

if __name__ == "__main__":
    app.run(debug=True)
```
