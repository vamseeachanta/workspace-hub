---
name: data-analysis-caching-for-performance
description: 'Sub-skill of data-analysis: Caching for Performance (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Caching for Performance (+2)

## Caching for Performance


```python
import streamlit as st
from functools import lru_cache

@st.cache_data(ttl=3600)  # Streamlit caching
def load_and_process_data():
    return pl.read_parquet("data.parquet")

@lru_cache(maxsize=100)  # General Python caching
def expensive_calculation(params_tuple):
    return compute_metrics(params_tuple)
```

## Consistent Styling


```python
# Define color palette
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "neutral": "#7f7f7f"
}


*See sub-skills for full details.*

## Error Handling for Data Loading


```python
def safe_load_data(path, fallback=None):
    """Load data with comprehensive error handling."""
    try:
        if path.endswith('.parquet'):
            return pl.read_parquet(path)
        elif path.endswith('.csv'):
            return pl.read_csv(path)
        else:
            raise ValueError(f"Unsupported format: {path}")

*See sub-skills for full details.*
