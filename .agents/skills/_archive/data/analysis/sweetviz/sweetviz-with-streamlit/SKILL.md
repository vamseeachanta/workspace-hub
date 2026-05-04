---
name: sweetviz-sweetviz-with-streamlit
description: 'Sub-skill of sweetviz: Sweetviz with Streamlit (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Sweetviz with Streamlit (+1)

## Sweetviz with Streamlit


```python
#!/usr/bin/env python3
"""sweetviz_streamlit.py - Streamlit app for Sweetviz reports"""

import streamlit as st
import sweetviz as sv
import pandas as pd
import tempfile
import os

st.set_page_config(page_title="Sweetviz EDA", layout="wide")
st.title("Sweetviz Exploratory Data Analysis")

# File upload
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Data Preview")
    st.dataframe(df.head(100))

    st.subheader("Dataset Info")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", df.isnull().sum().sum())

    # Analysis options
    st.sidebar.header("Analysis Options")

    target_col = st.sidebar.selectbox(
        "Target Variable (optional)",
        ["None"] + list(df.columns)
    )

    pairwise = st.sidebar.selectbox(
        "Pairwise Analysis",
        ["auto", "on", "off"]
    )

    skip_cols = st.sidebar.multiselect(
        "Columns to Skip",
        list(df.columns)
    )

    if st.button("Generate Report"):
        with st.spinner("Generating Sweetviz report..."):
            feat_cfg = sv.FeatureConfig(skip=skip_cols) if skip_cols else None

            report = sv.analyze(
                source=df,
                target_feat=target_col if target_col != "None" else None,
                feat_cfg=feat_cfg,
                pairwise_analysis=pairwise
            )

            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
                report.show_html(f.name, open_browser=False)

                with open(f.name, "r") as html_file:
                    html_content = html_file.read()

                os.unlink(f.name)

            # Display in iframe
            st.components.v1.html(html_content, height=800, scrolling=True)
```


## Sweetviz with Jupyter Magic


```python
# In Jupyter notebook
import sweetviz as sv
import pandas as pd

# Load data
df = pd.read_csv("data.csv")

# Quick analysis (opens in new tab)
report = sv.analyze(df)
report.show_notebook()  # Opens in browser from notebook

# Inline display (for newer Jupyter versions)
report.show_notebook(
    w="100%",  # Width
    h="600px",  # Height
    scale=0.8  # Scale factor
)

# For comparison
train_df = df.sample(frac=0.8)
test_df = df.drop(train_df.index)

comparison = sv.compare(
    [train_df, "Train"],
    [test_df, "Test"]
)
comparison.show_notebook()
```
