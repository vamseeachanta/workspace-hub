---
name: streamlit-1-use-caching-appropriately
description: 'Sub-skill of streamlit: 1. Use Caching Appropriately (+3).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Use Caching Appropriately (+3)

## 1. Use Caching Appropriately


```python
# GOOD: Cache data loading
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

# GOOD: Cache resources (DB connections, models)
@st.cache_resource
def get_model():
    return load_model("model.pkl")

# AVOID: Caching with unhashable arguments
# Use _arg prefix to skip hashing
@st.cache_data
def process_data(_db_connection, query):
    return _db_connection.execute(query)
```


## 2. Organize Large Apps


```python
# utils/data.py
def load_data():
    pass

# utils/charts.py
def create_chart(df):
    pass

# app.py
from utils.data import load_data
from utils.charts import create_chart
```


## 3. Handle State Carefully


```python
# GOOD: Initialize state at the top
if "data" not in st.session_state:
    st.session_state.data = None

# GOOD: Use callbacks for complex updates
def on_filter_change():
    st.session_state.filtered_data = apply_filter(st.session_state.data)

st.selectbox("Filter", options, on_change=on_filter_change)
```


## 4. Optimize Performance


```python
# Use containers for layout stability
placeholder = st.empty()

# Batch widget updates in forms
with st.form("filters"):
    # Multiple widgets
    st.form_submit_button()

# Use columns for responsive layout
cols = st.columns([1, 2, 1])
```
