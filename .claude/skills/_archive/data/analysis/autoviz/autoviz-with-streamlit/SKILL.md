---
name: autoviz-autoviz-with-streamlit
description: 'Sub-skill of autoviz: AutoViz with Streamlit (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# AutoViz with Streamlit (+1)

## AutoViz with Streamlit


```python
import streamlit as st
from autoviz import AutoViz_Class
import pandas as pd
import os
import tempfile

st.set_page_config(page_title="AutoViz EDA Tool", layout="wide")

st.title("AutoViz Exploratory Data Analysis")

# File upload
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Data Preview")
    st.dataframe(df.head(100))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Columns", len(df.columns))

    # Target variable selection
    target = st.selectbox(
        "Select target variable (optional)",
        ["None"] + list(df.columns)
    )

    if st.button("Run AutoViz Analysis"):
        with st.spinner("Generating visualizations..."):
            # Create temp directory for outputs
            with tempfile.TemporaryDirectory() as tmpdir:
                AV = AutoViz_Class()

                df_analyzed = AV.AutoViz(
                    filename="",
                    dfte=df,
                    depVar="" if target == "None" else target,
                    chart_format="png",
                    save_plot_dir=tmpdir,
                    verbose=0
                )

                # Display generated charts
                st.subheader("Generated Visualizations")

                for file in os.listdir(tmpdir):
                    if file.endswith(".png"):
                        st.image(os.path.join(tmpdir, file))

        st.success("Analysis complete!")
```


## AutoViz with Polars


```python
from autoviz import AutoViz_Class
import polars as pl
import pandas as pd

def autoviz_polars(lf: pl.LazyFrame, target: str = "", **kwargs) -> pd.DataFrame:
    """
    Run AutoViz on Polars LazyFrame.

    Args:
        lf: Polars LazyFrame
        target: Target variable name
        **kwargs: Additional AutoViz parameters

    Returns:
        Analyzed DataFrame
    """
    # Collect LazyFrame to DataFrame, then convert to pandas
    df_polars = lf.collect()
    df_pandas = df_polars.to_pandas()

    AV = AutoViz_Class()

    return AV.AutoViz(
        filename="",
        dfte=df_pandas,
        depVar=target,
        **kwargs
    )

# Usage
# lf = pl.scan_csv("data.csv")
# df_analyzed = autoviz_polars(lf, target="revenue", chart_format="png")
```
