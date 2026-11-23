---
name: ydata-profiling-ydata-profiling-with-streamlit
description: 'Sub-skill of ydata-profiling: YData Profiling with Streamlit (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# YData Profiling with Streamlit (+1)

## YData Profiling with Streamlit


```python
import streamlit as st
from ydata_profiling import ProfileReport
import pandas as pd
from streamlit_pandas_profiling import st_profile_report

st.set_page_config(page_title="Data Profiler", layout="wide")
st.title("Interactive Data Profiler")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Data Preview")
    st.dataframe(df.head(100))

    # Profile options
    with st.sidebar:
        st.header("Profile Options")
        minimal = st.checkbox("Minimal Mode", value=False)
        explorative = st.checkbox("Explorative Mode", value=True)

    if st.button("Generate Profile"):
        with st.spinner("Generating report..."):
            profile = ProfileReport(
                df,
                title="Data Profile",
                minimal=minimal,
                explorative=explorative
            )

            st_profile_report(profile)
```


## YData Profiling with Polars


```python
from ydata_profiling import ProfileReport
import polars as pl
import pandas as pd

def profile_polars_df(
    lf: pl.LazyFrame,
    title: str = "Polars Data Profile",
    **kwargs
) -> ProfileReport:
    """
    Profile Polars LazyFrame using YData Profiling.

    Args:
        lf: Polars LazyFrame
        title: Report title
        **kwargs: Additional ProfileReport arguments

    Returns:
        ProfileReport object
    """
    # Collect and convert to pandas
    df_polars = lf.collect()
    df_pandas = df_polars.to_pandas()

    return ProfileReport(df_pandas, title=title, **kwargs)

# Usage
# lf = pl.scan_parquet("data.parquet")
# profile = profile_polars_df(lf, title="Polars Data Profile")
# profile.to_file("profile.html")
```
