---
name: data-analysis-1-lazy-evaluation-first
description: 'Sub-skill of data-analysis: 1. Lazy Evaluation First (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Lazy Evaluation First (+3)

## 1. Lazy Evaluation First

```python
# Prefer lazy operations, collect only when needed
result = (
    pl.scan_parquet("data/*.parquet")
    .filter(...)
    .group_by(...)
    .agg(...)
    .collect()  # Execute at the end
)
```


## 2. Progressive Disclosure in Dashboards

```python
# Start with summary, allow drill-down
st.header("Overview")
show_metrics()

with st.expander("Detailed Analysis"):
    show_detailed_charts()

with st.expander("Raw Data"):
    st.dataframe(df)
```


## 3. Reproducible Reports

```python
# Include metadata in reports
report_metadata = {
    "generated_at": datetime.now().isoformat(),
    "data_source": "sales_database",
    "date_range": f"{start_date} to {end_date}",
    "filters_applied": filters
}
```


## 4. Performance Monitoring

```python
import time

def timed_operation(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"{name} completed in {duration:.2f}s")
            return result
        return wrapper
    return decorator

@timed_operation("Data aggregation")
def aggregate_sales():
    ...
```
