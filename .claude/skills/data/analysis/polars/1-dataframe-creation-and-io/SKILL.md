---
name: polars-1-dataframe-creation-and-io
description: 'Sub-skill of polars: 1. DataFrame Creation and I/O.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. DataFrame Creation and I/O

## 1. DataFrame Creation and I/O


**Creating DataFrames:**
```python
import polars as pl
import numpy as np
from datetime import datetime, date

# From Python dictionaries
df = pl.DataFrame({
    "id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "value": [100.5, 200.3, 150.7, 300.2, 250.8],
    "category": ["A", "B", "A", "C", "B"],
    "timestamp": [
        datetime(2025, 1, 1, 10, 0),
        datetime(2025, 1, 2, 11, 30),
        datetime(2025, 1, 3, 9, 15),
        datetime(2025, 1, 4, 14, 45),
        datetime(2025, 1, 5, 16, 0),
    ]
})

print(df)
print(f"Shape: {df.shape}")
print(f"Schema: {df.schema}")

# From NumPy arrays
np_data = np.random.randn(1000, 5)
df_numpy = pl.DataFrame(
    np_data,
    schema=["col_a", "col_b", "col_c", "col_d", "col_e"]
)

# From list of dictionaries
records = [
    {"x": 1, "y": "a"},
    {"x": 2, "y": "b"},
    {"x": 3, "y": "c"}
]
df_records = pl.DataFrame(records)

# Specify schema explicitly
df_typed = pl.DataFrame(
    {
        "integers": [1, 2, 3],
        "floats": [1.0, 2.0, 3.0],
        "strings": ["a", "b", "c"]
    },
    schema={
        "integers": pl.Int32,
        "floats": pl.Float64,
        "strings": pl.Utf8
    }
)
```

**Reading Files:**
```python
# CSV files
df = pl.read_csv("data.csv")

# With options
df = pl.read_csv(
    "data.csv",
    separator=",",
    has_header=True,
    skip_rows=0,
    n_rows=10000,  # Read only first N rows
    columns=["col1", "col2", "col3"],  # Select columns
    dtypes={"id": pl.Int64, "value": pl.Float32},  # Specify types
    null_values=["NA", "N/A", ""],
    ignore_errors=True,
    try_parse_dates=True,
    encoding="utf8"
)

# Parquet files (recommended for large data)
df = pl.read_parquet("data.parquet")

# Multiple Parquet files with globbing
df = pl.read_parquet("data/*.parquet")

# Parquet with row group filtering
df = pl.read_parquet(
    "large_data.parquet",
    columns=["id", "value", "date"],
    n_rows=100000,
    row_count_name="row_nr"
)

# JSON files
df = pl.read_json("data.json")

# JSON Lines (newline-delimited JSON)
df = pl.read_ndjson("data.jsonl")

# Excel files
df = pl.read_excel("data.xlsx", sheet_name="Sheet1")

# Delta Lake
df = pl.read_delta("delta_table/")

# From SQL database using ConnectorX (fast!)
df = pl.read_database(
    query="SELECT * FROM sales WHERE date > '2025-01-01'",
    connection="postgresql://user:pass@localhost/db"
)

# From URL
df = pl.read_csv("https://example.com/data.csv")
```

**Writing Files:**
```python
# CSV
df.write_csv("output.csv")

# Parquet (recommended)
df.write_parquet(
    "output.parquet",
    compression="zstd",  # zstd, lz4, snappy, gzip, brotli
    compression_level=3,
    statistics=True,
    row_group_size=100000
)

# JSON
df.write_json("output.json", row_oriented=True)
df.write_ndjson("output.jsonl")

# Delta Lake
df.write_delta("delta_table/", mode="overwrite")

# IPC/Arrow format (fastest for inter-process communication)
df.write_ipc("output.arrow")
```
