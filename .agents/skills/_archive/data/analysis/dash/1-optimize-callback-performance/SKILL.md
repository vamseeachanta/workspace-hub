---
name: dash-1-optimize-callback-performance
description: 'Sub-skill of dash: 1. Optimize Callback Performance (+3).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Optimize Callback Performance (+3)

## 1. Optimize Callback Performance


```python
# Use prevent_initial_call when appropriate
@callback(
    Output("output", "children"),
    Input("button", "n_clicks"),
    prevent_initial_call=True
)
def handle_click(n_clicks):
    return f"Clicked {n_clicks} times"

# Use State for non-triggering inputs
@callback(
    Output("output", "children"),
    Input("submit-btn", "n_clicks"),
    State("input-field", "value")  # Doesn't trigger callback
)
def submit_form(n_clicks, value):
    return f"Submitted: {value}"
```


## 2. Efficient Data Loading


```python
# Cache expensive computations
from flask_caching import Cache

cache = Cache(app.server, config={"CACHE_TYPE": "simple"})

@cache.memoize(timeout=300)
def load_data():
    return pd.read_parquet("large_file.parquet")
```


## 3. Modular Callbacks


```python
# Separate callbacks into modules
# callbacks/analytics.py
from dash import callback, Output, Input

def register_callbacks(app):
    @callback(
        Output("chart", "figure"),
        Input("dropdown", "value")
    )
    def update_chart(value):
        return create_figure(value)
```


## 4. Error Handling


```python
from dash import callback, Output, Input
from dash.exceptions import PreventUpdate

@callback(
    Output("output", "children"),
    Input("input", "value")
)
def safe_callback(value):
    if value is None:
        raise PreventUpdate

    try:
        result = process(value)
        return result
    except Exception as e:
        return html.Div(f"Error: {str(e)}", className="text-danger")
```
