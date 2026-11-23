---
name: dash-5-multi-page-applications
description: 'Sub-skill of dash: 5. Multi-Page Applications.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 5. Multi-Page Applications

## 5. Multi-Page Applications


**Project Structure:**
```
my_dash_app/
├── app.py              # Main entry point
├── pages/
│   ├── __init__.py
│   ├── home.py
│   ├── analytics.py
│   └── settings.py
├── components/
│   ├── __init__.py
│   ├── navbar.py
│   └── footer.py
├── utils/
│   ├── __init__.py
│   └── data.py
└── assets/
    ├── style.css
    └── logo.png
```

**Main App (app.py):**
```python
from dash import Dash, html, dcc, page_container
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Analytics", href="/analytics")),
        dbc.NavItem(dbc.NavLink("Settings", href="/settings")),
    ],
    brand="My Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
)

# Layout with navigation and page container
app.layout = html.Div([
    navbar,
    dbc.Container([
        page_container
    ], fluid=True, className="mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

**Home Page (pages/home.py):**
```python
from dash import html, register_page
import dash_bootstrap_components as dbc

register_page(__name__, path="/", name="Home")

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Welcome to the Dashboard"),
            html.P("Select a page from the navigation bar to get started."),
            dbc.Card([
                dbc.CardBody([
                    html.H4("Quick Links"),
                    dbc.ListGroup([
                        dbc.ListGroupItem("Analytics", href="/analytics"),
                        dbc.ListGroupItem("Settings", href="/settings")
                    ])
                ])
            ])
        ])
    ])
])
```

**Analytics Page (pages/analytics.py):**
```python
from dash import html, dcc, callback, Output, Input, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

register_page(__name__, path="/analytics", name="Analytics")

# Generate sample data
df = pd.DataFrame({
    "date": pd.date_range("2025-01-01", periods=365),
    "value": [100 + i + (i % 30) * 5 for i in range(365)]
})

layout = dbc.Container([
    html.H1("Analytics"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Chart Type"),
            dcc.Dropdown(
                id="chart-type",
                options=[
                    {"label": "Line", "value": "line"},
                    {"label": "Bar", "value": "bar"},
                    {"label": "Area", "value": "area"}
                ],
                value="line"
            )
        ], md=4)
    ], className="mb-4"),

    dcc.Graph(id="analytics-chart")
])

@callback(
    Output("analytics-chart", "figure"),
    Input("chart-type", "value")
)
def update_chart(chart_type):
    if chart_type == "line":
        fig = px.line(df, x="date", y="value")
    elif chart_type == "bar":
        monthly = df.resample("M", on="date")["value"].sum().reset_index()
        fig = px.bar(monthly, x="date", y="value")
    else:
        fig = px.area(df, x="date", y="value")

    return fig
```
