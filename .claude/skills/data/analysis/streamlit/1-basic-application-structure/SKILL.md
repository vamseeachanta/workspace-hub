---
name: streamlit-1-basic-application-structure
description: 'Sub-skill of streamlit: 1. Basic Application Structure (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Basic Application Structure (+1)

## 1. Basic Application Structure


**Minimal App (app.py):**
```python
import streamlit as st
import pandas as pd
import polars as pl

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="My Data App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and header
st.title("My Data Application")
st.header("Welcome to the Dashboard")
st.subheader("Data Analysis Section")

# Text elements
st.text("This is plain text")
st.markdown("**Bold** and *italic* text with [links](https://streamlit.io)")
st.caption("This is a caption for additional context")
st.code("print('Hello, Streamlit!')", language="python")

# Display data
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["NYC", "LA", "Chicago"]
})

st.dataframe(df)  # Interactive table
st.table(df)       # Static table
st.json({"key": "value", "list": [1, 2, 3]})

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Revenue", "$1.2M", "+12%")
col2.metric("Users", "10,234", "-2%")
col3.metric("Conversion", "3.2%", "+0.5%")
```

**Run the app:**
```bash
streamlit run app.py
```


## 2. Widgets and User Input


**Input Widgets:**
```python
import streamlit as st
from datetime import datetime, date

# Text inputs
name = st.text_input("Enter your name", value="User")
bio = st.text_area("Tell us about yourself", height=100)
password = st.text_input("Password", type="password")

# Numeric inputs
age = st.number_input("Age", min_value=0, max_value=120, value=25, step=1)
price = st.slider("Price Range", 0.0, 100.0, (25.0, 75.0))  # Range slider
rating = st.slider("Rating", 1, 5, 3)

# Selection widgets
option = st.selectbox("Choose an option", ["Option A", "Option B", "Option C"])
options = st.multiselect("Select multiple", ["Red", "Green", "Blue"], default=["Red"])
radio_choice = st.radio("Pick one", ["Small", "Medium", "Large"], horizontal=True)

# Boolean inputs
agree = st.checkbox("I agree to the terms")
toggle = st.toggle("Enable feature")

# Date and time
selected_date = st.date_input("Select a date", value=date.today())
date_range = st.date_input(
    "Date range",
    value=(date(2025, 1, 1), date.today()),
    format="YYYY-MM-DD"
)
selected_time = st.time_input("Select a time")

# File upload
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv", "xlsx"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(f"Loaded {len(df)} rows")

# Color picker
color = st.color_picker("Pick a color", "#00FF00")

# Buttons
if st.button("Click me"):
    st.write("Button clicked!")

# Download button
@st.cache_data
def get_data():
    return pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})

csv = get_data().to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="data.csv",
    mime="text/csv"
)
```
