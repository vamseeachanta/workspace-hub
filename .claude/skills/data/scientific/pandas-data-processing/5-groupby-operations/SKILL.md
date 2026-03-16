---
name: pandas-data-processing-5-groupby-operations
description: 'Sub-skill of pandas-data-processing: 5. GroupBy Operations.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 5. GroupBy Operations

## 5. GroupBy Operations


**Group and Aggregate:**
```python
def group_by_sea_state(
    df: pd.DataFrame,
    hs_column: str = 'Hs',
    tp_column: str = 'Tp',
    hs_bins: list = None,
    tp_bins: list = None
) -> pd.DataFrame:
    """
    Group results by sea state (Hs, Tp bins).

    Args:
        df: Input DataFrame with sea state parameters
        hs_column: Column name for significant wave height
        tp_column: Column name for peak period
        hs_bins: Bins for Hs [0, 2, 4, 6, 8, 10]
        tp_bins: Bins for Tp [0, 6, 8, 10, 12, 14]

    Returns:
        Grouped statistics by sea state
    """
    if hs_bins is None:
        hs_bins = [0, 2, 4, 6, 8, 10, 12]
    if tp_bins is None:
        tp_bins = [0, 6, 8, 10, 12, 14, 16]

    # Create bins
    df['Hs_bin'] = pd.cut(df[hs_column], bins=hs_bins)
    df['Tp_bin'] = pd.cut(df[tp_column], bins=tp_bins)

    # Group and aggregate
    grouped = df.groupby(['Hs_bin', 'Tp_bin']).agg({
        'Tension_Max': ['mean', 'std', 'max'],
        'Motion_Max': ['mean', 'std', 'max'],
        'Offset_Max': ['mean', 'std', 'max']
    })

    return grouped

# Example
sea_state_results = pd.DataFrame({
    'Hs': [2.5, 3.0, 4.5, 5.0, 6.5, 7.0],
    'Tp': [7.0, 8.5, 9.0, 10.5, 11.0, 12.5],
    'Tension_Max': [1500, 1600, 1800, 2000, 2200, 2400],
    'Motion_Max': [2.0, 2.5, 3.0, 3.5, 4.0, 4.5],
    'Offset_Max': [50, 60, 70, 80, 90, 100]
})

grouped_stats = group_by_sea_state(sea_state_results)
print(grouped_stats)
```

**Multi-Level Grouping:**
```python
def analyze_by_loadcase_and_direction(
    df: pd.DataFrame,
    group_columns: list = ['LoadCase', 'Direction'],
    value_columns: list = None
) -> pd.DataFrame:
    """
    Analyze results grouped by load case and direction.

    Args:
        df: Input DataFrame
        group_columns: Columns to group by
        value_columns: Columns to aggregate (None = all numeric)

    Returns:
        Multi-level grouped statistics
    """
    if value_columns is None:
        value_columns = df.select_dtypes(include=[np.number]).columns.tolist()

    # Group and calculate statistics
    grouped = df.groupby(group_columns)[value_columns].agg([
        'count', 'mean', 'std', 'min', 'max'
    ])

    return grouped

# Example
load_case_data = pd.DataFrame({
    'LoadCase': ['Operating', 'Operating', 'Storm', 'Storm', 'Extreme', 'Extreme'],
    'Direction': [0, 45, 0, 45, 0, 45],
    'Tension': [1500, 1520, 2000, 2050, 2500, 2600],
    'Offset': [50, 55, 75, 80, 100, 110]
})

stats_by_case = analyze_by_loadcase_and_direction(load_case_data)
print(stats_by_case)
```
