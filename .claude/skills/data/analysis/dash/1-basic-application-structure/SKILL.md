---
name: dash-1-basic-application-structure
description: 'Sub-skill of dash: 1. Basic Application Structure.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Basic Application Structure

## 1. Basic Application Structure


**Minimal Dash App:**
```python
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

# Initialize app
app = Dash(__name__)

# Sample data
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "NYC", "NYC", "NYC"]
})

# Create figure
fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

# Layout
app.layout = html.Div([
    html.H1("Hello Dash"),
    html.P("This is a simple Dash application."),
    dcc.Graph(id="example-graph", figure=fig)
])

# Run server
if __name__ == "__main__":
    app.run(debug=True)
```

**Run the app:**
```bash
python app.py
# Visit http://127.0.0.1:8050/
```
