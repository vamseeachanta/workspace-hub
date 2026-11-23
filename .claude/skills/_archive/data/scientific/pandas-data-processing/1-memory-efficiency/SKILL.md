---
name: pandas-data-processing-1-memory-efficiency
description: 'Sub-skill of pandas-data-processing: 1. Memory Efficiency (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Memory Efficiency (+3)

## 1. Memory Efficiency


**Use appropriate data types:**
```python
# ❌ Bad: Default float64
df = pd.DataFrame({'value': np.random.randn(1000000)})
print(f"Memory: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

# ✅ Good: Use float32 when precision allows
df_optimized = pd.DataFrame({'value': np.random.randn(1000000).astype(np.float32)})
print(f"Memory: {df_optimized.memory_usage(deep=True).sum() / 1e6:.1f} MB")  # 50% reduction

# ✅ Use categorical for repeated strings
df['category'] = pd.Categorical(['A', 'B', 'C'] * 100000)
```

**Chunking for large files:**
```python
def process_large_csv_in_chunks(
    csv_file: Path,
    chunksize: int = 100_000
) -> pd.DataFrame:
    """Process large CSV in chunks to avoid memory issues."""
    chunks = []

    for chunk in pd.read_csv(csv_file, chunksize=chunksize):
        # Process each chunk
        chunk_processed = chunk[chunk['Value'] > 0]  # Example filter
        chunks.append(chunk_processed)

    # Combine all chunks
    result = pd.concat(chunks, ignore_index=True)

    return result
```


## 2. Vectorization


**Always prefer vectorized operations:**
```python
# ❌ Bad: Loop
df['result'] = 0
for i in range(len(df)):
    df.loc[i, 'result'] = df.loc[i, 'a'] + df.loc[i, 'b']

# ✅ Good: Vectorized
df['result'] = df['a'] + df['b']

# ✅ Better: NumPy for complex operations
df['result'] = np.where(
    df['a'] > 0,
    df['a'] + df['b'],
    df['a'] - df['b']
)
```


## 3. Index Usage


**Use index for time series:**
```python
# ✅ Set datetime index
df['Time'] = pd.to_datetime(df['Time'])
df.set_index('Time', inplace=True)

# Fast slicing
subset = df['2025-01-01':'2025-01-31']

# Fast resampling
daily_mean = df.resample('D').mean()
```


## 4. Data Validation


**Validate data before processing:**
```python
def validate_engineering_data(df: pd.DataFrame) -> bool:
    """Validate engineering data integrity."""
    # Check for missing values
    if df.isnull().any().any():
        print("⚠ Warning: Missing values detected")
        print(df.isnull().sum())

    # Check for duplicates
    if df.duplicated().any():
        print("⚠ Warning: Duplicate rows detected")
        print(f"Duplicates: {df.duplicated().sum()}")

    # Check data types
    print("Data types:")
    print(df.dtypes)

    # Check value ranges
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if (df[col] < 0).any():
            print(f"⚠ Warning: Negative values in {col}")

    return True
```
