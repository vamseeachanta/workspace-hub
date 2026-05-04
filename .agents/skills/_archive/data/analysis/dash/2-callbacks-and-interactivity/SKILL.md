---
name: dash-2-callbacks-and-interactivity
description: 'Sub-skill of dash: 2. Callbacks and Interactivity.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 2. Callbacks and Interactivity

## 2. Callbacks and Interactivity


**Basic Callback:**
```python
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

app = Dash(__name__)

# Sample data
df = pd.DataFrame({
    "date": pd.date_range("2025-01-01", periods=100),
    "category": ["A", "B", "C", "D"] * 25,
    "value": range(100)
})

# Layout
app.layout = html.Div([
    html.H1("Interactive Dashboard"),

    html.Label("Select Category:"),
    dcc.Dropdown(
        id="category-dropdown",
        options=[{"label": c, "value": c} for c in df["category"].unique()],
        value="A",
        clearable=False
    ),

    dcc.Graph(id="line-chart")
])

# Callback
@callback(
    Output("line-chart", "figure"),
    Input("category-dropdown", "value")
)
def update_chart(selected_category):
    filtered_df = df[df["category"] == selected_category]

    fig = px.line(
        filtered_df,
        x="date",
        y="value",
        title=f"Values for Category {selected_category}"
    )

    return fig

if __name__ == "__main__":
    app.run(debug=True)
```

**Multiple Inputs and Outputs:**
```python
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

app = Dash(__name__)

# Sample data
df = pd.DataFrame({
    "date": pd.date_range("2025-01-01", periods=365),
    "category": ["A", "B", "C"] * 122 + ["A"],
    "region": ["North", "South", "East", "West"] * 91 + ["North"],
    "value": [i + (i % 30) * 10 for i in range(365)]
})

app.layout = html.Div([
    html.H1("Multi-Input Dashboard"),

    html.Div([
        html.Div([
            html.Label("Category"),
            dcc.Dropdown(
                id="category-filter",
                options=[{"label": c, "value": c} for c in df["category"].unique()],
                value=["A", "B", "C"],
                multi=True
            )
        ], style={"width": "45%", "display": "inline-block"}),

        html.Div([
            html.Label("Region"),
            dcc.Dropdown(
                id="region-filter",
                options=[{"label": r, "value": r} for r in df["region"].unique()],
                value=["North", "South", "East", "West"],
                multi=True
            )
        ], style={"width": "45%", "display": "inline-block", "marginLeft": "5%"})
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id="trend-chart")
        ], style={"width": "60%", "display": "inline-block"}),

        html.Div([
            dcc.Graph(id="pie-chart")
        ], style={"width": "38%", "display": "inline-block", "marginLeft": "2%"})
    ]),

    html.Div(id="summary-stats")
])

@callback(
    [Output("trend-chart", "figure"),
     Output("pie-chart", "figure"),
     Output("summary-stats", "children")],
    [Input("category-filter", "value"),
     Input("region-filter", "value")]
)
def update_all(categories, regions):
    # Filter data
    filtered = df[
        (df["category"].isin(categories)) &
        (df["region"].isin(regions))
    ]

    # Trend chart
    trend = filtered.groupby("date")["value"].sum().reset_index()
    trend_fig = px.line(trend, x="date", y="value", title="Value Trend")

    # Pie chart
    by_category = filtered.groupby("category")["value"].sum().reset_index()
    pie_fig = px.pie(by_category, values="value", names="category", title="By Category")

    # Summary stats
    stats = html.Div([
        html.H4("Summary Statistics"),
        html.P(f"Total records: {len(filtered):,}"),
        html.P(f"Total value: {filtered['value'].sum():,}"),
        html.P(f"Average value: {filtered['value'].mean():.2f}")
    ])

    return trend_fig, pie_fig, stats

if __name__ == "__main__":
    app.run(debug=True)
```

**Chained Callbacks:**
```python
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd

app = Dash(__name__)

# Hierarchical data
data = {
    "USA": {"California": ["San Francisco", "Los Angeles"], "Texas": ["Houston", "Dallas"]},
    "Canada": {"Ontario": ["Toronto", "Ottawa"], "Quebec": ["Montreal", "Quebec City"]}
}

app.layout = html.Div([
    html.H1("Chained Dropdowns"),

    html.Label("Country"),
    dcc.Dropdown(id="country-dropdown"),

    html.Label("State/Province"),
    dcc.Dropdown(id="state-dropdown"),

    html.Label("City"),
    dcc.Dropdown(id="city-dropdown"),

    html.Div(id="selection-output")
])

# Populate country dropdown
@callback(
    Output("country-dropdown", "options"),
    Input("country-dropdown", "id")  # Dummy input to trigger on load
)
def set_countries(_):
    return [{"label": c, "value": c} for c in data.keys()]

# Update state options based on country
@callback(
    Output("state-dropdown", "options"),
    Output("state-dropdown", "value"),
    Input("country-dropdown", "value")
)
def set_states(country):

*Content truncated — see parent skill for full reference.*
