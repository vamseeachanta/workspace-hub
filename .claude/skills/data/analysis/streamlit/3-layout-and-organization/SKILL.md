---
name: streamlit-3-layout-and-organization
description: 'Sub-skill of streamlit: 3. Layout and Organization.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 3. Layout and Organization

## 3. Layout and Organization


**Columns:**
```python
import streamlit as st

# Equal columns
col1, col2, col3 = st.columns(3)

with col1:
    st.header("Column 1")
    st.write("Content for column 1")

with col2:
    st.header("Column 2")
    st.metric("Metric", "100")

with col3:
    st.header("Column 3")
    st.button("Action")

# Unequal columns
left, right = st.columns([2, 1])  # 2:1 ratio

with left:
    st.write("Wider column")

with right:
    st.write("Narrower column")
```

**Sidebar:**
```python
import streamlit as st

# Sidebar content
st.sidebar.title("Navigation")
st.sidebar.header("Filters")

# Sidebar widgets
category = st.sidebar.selectbox("Category", ["All", "A", "B", "C"])
min_value = st.sidebar.slider("Minimum Value", 0, 100, 25)
show_raw = st.sidebar.checkbox("Show raw data")

# Using 'with' syntax
with st.sidebar:
    st.header("Settings")
    theme = st.radio("Theme", ["Light", "Dark"])
    st.divider()
    st.caption("App v1.0.0")
```

**Tabs:**
```python
import streamlit as st

tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Data", "⚙️ Settings"])

with tab1:
    st.header("Chart View")
    # Add chart here

with tab2:
    st.header("Data View")
    # Add dataframe here

with tab3:
    st.header("Settings")
    # Add settings here
```

**Expanders and Containers:**
```python
import streamlit as st

# Expander (collapsible section)
with st.expander("Click to expand"):
    st.write("Hidden content revealed!")
    st.code("print('Hello')")

# Container (grouping elements)
with st.container():
    st.write("This is inside a container")
    col1, col2 = st.columns(2)
    col1.write("Left")
    col2.write("Right")

# Container with border
with st.container(border=True):
    st.write("Content with border")

# Empty placeholder (for dynamic updates)
placeholder = st.empty()
placeholder.text("Initial text")
# Later: placeholder.text("Updated text")
```
