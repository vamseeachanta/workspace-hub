---
name: pandas-data-processing-3-data-transformation
description: 'Sub-skill of pandas-data-processing: 3. Data Transformation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 3. Data Transformation

## 3. Data Transformation


**Pivot Operations:**
```python
def pivot_mooring_data(
    df: pd.DataFrame,
    index: str = 'Time',
    columns: str = 'LineID',
    values: str = 'Tension'
) -> pd.DataFrame:
    """
    Pivot long-format mooring data to wide format.

    Args:
        df: Input DataFrame in long format
        index: Index column (usually time)
        columns: Column to pivot (usually line identifier)
        values: Value column (tension, angle, etc.)

    Returns:
        Pivoted DataFrame
    """
    pivoted = df.pivot(
        index=index,
        columns=columns,
        values=values
    )

    # Rename columns
    pivoted.columns = [f'{values}_Line{col}' for col in pivoted.columns]

    return pivoted

# Example: Convert long format to wide format
# Long format:
#   Time  LineID  Tension
#   0.0   1       1500
#   0.0   2       1520
#   0.1   1       1505
#   0.1   2       1525

long_format = pd.DataFrame({
    'Time': [0.0, 0.0, 0.1, 0.1, 0.2, 0.2],
    'LineID': [1, 2, 1, 2, 1, 2],
    'Tension': [1500, 1520, 1505, 1525, 1510, 1530]
})

wide_format = pivot_mooring_data(long_format)
print(wide_format)
# Output:
#       Tension_Line1  Tension_Line2
# Time
# 0.0   1500           1520
# 0.1   1505           1525
# 0.2   1510           1530
```

**Melt Operations:**
```python
def melt_wide_format(
    df: pd.DataFrame,
    id_vars: list = None,
    value_name: str = 'Value',
    var_name: str = 'Parameter'
) -> pd.DataFrame:
    """
    Convert wide-format data to long format.

    Args:
        df: Input DataFrame in wide format
        id_vars: Identifier variables to preserve
        value_name: Name for value column
        var_name: Name for variable column

    Returns:
        Melted DataFrame
    """
    if id_vars is None:
        id_vars = [df.index.name or 'index']
        df_reset = df.reset_index()
    else:
        df_reset = df

    melted = pd.melt(
        df_reset,
        id_vars=id_vars,
        value_name=value_name,
        var_name=var_name
    )

    return melted

# Example: Convert multi-column tensions to long format
wide_data = pd.DataFrame({
    'Time': [0.0, 0.1, 0.2],
    'Tension_Line1': [1500, 1505, 1510],
    'Tension_Line2': [1520, 1525, 1530],
    'Tension_Line3': [1480, 1485, 1490]
})

long_data = melt_wide_format(
    wide_data,
    id_vars=['Time'],
    value_name='Tension',
    var_name='Line'
)

print(long_data)
# Output:
#   Time  Line            Tension
#   0.0   Tension_Line1   1500
#   0.0   Tension_Line2   1520
#   0.0   Tension_Line3   1480
#   ...
```
