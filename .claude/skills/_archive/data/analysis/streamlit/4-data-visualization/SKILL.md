---
name: streamlit-4-data-visualization
description: 'Sub-skill of streamlit: 4. Data Visualization (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 4. Data Visualization (+1)

## 4. Data Visualization


**Plotly Integration:**
```python
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Sample data
df = pd.DataFrame({
    "date": pd.date_range("2025-01-01", periods=100),
    "value": [i + (i % 7) * 5 for i in range(100)],
    "category": ["A", "B", "C", "D"] * 25
})

# Plotly Express charts
fig = px.line(df, x="date", y="value", color="category", title="Time Series")
st.plotly_chart(fig, use_container_width=True)

# Scatter plot
fig_scatter = px.scatter(
    df, x="date", y="value",
    color="category", size="value",
    hover_data=["category"]
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Bar chart
category_totals = df.groupby("category")["value"].sum().reset_index()
fig_bar = px.bar(category_totals, x="category", y="value", title="Category Totals")
st.plotly_chart(fig_bar, use_container_width=True)

# Graph Objects for more control
fig_go = go.Figure()
fig_go.add_trace(go.Scatter(
    x=df["date"],
    y=df["value"],
    mode="lines+markers",
    name="Values"
))
fig_go.update_layout(title="Custom Plotly Chart", hovermode="x unified")
st.plotly_chart(fig_go, use_container_width=True)
```

**Built-in Charts:**
```python
import streamlit as st
import pandas as pd
import numpy as np

# Sample data
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=["A", "B", "C"]
)

# Simple line chart
st.line_chart(chart_data)

# Area chart
st.area_chart(chart_data)

# Bar chart
st.bar_chart(chart_data)

# Scatter chart (Streamlit 1.26+)
scatter_data = pd.DataFrame({
    "x": np.random.randn(100),
    "y": np.random.randn(100),
    "size": np.random.rand(100) * 100
})
st.scatter_chart(scatter_data, x="x", y="y", size="size")

# Map
map_data = pd.DataFrame({
    "lat": np.random.randn(100) / 50 + 37.76,
    "lon": np.random.randn(100) / 50 - 122.4
})
st.map(map_data)
```

**Matplotlib Integration:**
```python
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Create matplotlib figure
fig, ax = plt.subplots(figsize=(10, 6))
x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), label="sin(x)")
ax.plot(x, np.cos(x), label="cos(x)")
ax.legend()
ax.set_title("Matplotlib Chart")

# Display in Streamlit
st.pyplot(fig)
```


## 5. Caching for Performance


**Cache Data (for expensive data operations):**
```python
import streamlit as st
import pandas as pd
import polars as pl
import time

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """Load and cache data. Cache key: file_path."""
    time.sleep(2)  # Simulate slow load
    return pd.read_csv(file_path)

@st.cache_data(ttl=3600)  # Cache expires after 1 hour
def fetch_api_data(endpoint: str) -> dict:
    """Fetch data from API with time-based cache."""
    import requests
    response = requests.get(endpoint)
    return response.json()

@st.cache_data(show_spinner="Loading data...")
def load_with_spinner(path: str) -> pl.DataFrame:
    """Show custom spinner while loading."""
    return pl.read_parquet(path)

# Using cached functions
df = load_data("data/sales.csv")  # First call: slow
df = load_data("data/sales.csv")  # Second call: instant (cached)

# Clear cache programmatically
if st.button("Clear cache"):
    st.cache_data.clear()
```

**Cache Resources (for global resources):**
```python
import streamlit as st
from sqlalchemy import create_engine

@st.cache_resource
def get_database_connection():
    """Cache database connection (singleton pattern)."""
    return create_engine("postgresql://user:pass@localhost/db")

@st.cache_resource
def load_ml_model():
    """Cache ML model (loaded once per session)."""
    import joblib
    return joblib.load("model.pkl")

# Use cached resources
engine = get_database_connection()
model = load_ml_model()
```
