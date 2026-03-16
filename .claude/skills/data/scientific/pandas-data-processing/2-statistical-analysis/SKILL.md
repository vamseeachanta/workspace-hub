---
name: pandas-data-processing-2-statistical-analysis
description: 'Sub-skill of pandas-data-processing: 2. Statistical Analysis.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 2. Statistical Analysis

## 2. Statistical Analysis


**Summary Statistics:**
```python
def generate_statistical_summary(
    df: pd.DataFrame,
    columns: list = None
) -> pd.DataFrame:
    """
    Generate comprehensive statistical summary.

    Args:
        df: Input DataFrame
        columns: Columns to analyze (None = all numeric)

    Returns:
        DataFrame with statistical metrics
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    # Standard statistics
    summary = df[columns].describe()

    # Additional statistics
    additional_stats = pd.DataFrame({
        'median': df[columns].median(),
        'skewness': df[columns].skew(),
        'kurtosis': df[columns].kurtosis(),
        'variance': df[columns].var()
    }).T

    # Combine
    full_summary = pd.concat([summary, additional_stats])

    return full_summary

# Example
motion_stats = generate_statistical_summary(
    results,
    columns=['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']
)

print(motion_stats)

# Export to CSV
motion_stats.to_csv('reports/motion_statistics.csv')
```

**Extreme Value Analysis:**
```python
def extract_extreme_values(
    df: pd.DataFrame,
    column: str,
    n_extremes: int = 10,
    extreme_type: str = 'max'
) -> pd.DataFrame:
    """
    Extract extreme values (max or min) from time series.

    Args:
        df: Input DataFrame with datetime index
        column: Column to analyze
        n_extremes: Number of extreme values to extract
        extreme_type: 'max' or 'min'

    Returns:
        DataFrame with extreme events
    """
    if extreme_type == 'max':
        extremes = df.nlargest(n_extremes, column)
    elif extreme_type == 'min':
        extremes = df.nsmallest(n_extremes, column)
    else:
        raise ValueError("extreme_type must be 'max' or 'min'")

    # Sort by time
    extremes = extremes.sort_index()

    return extremes

# Example: Top 10 maximum tensions
max_tensions = extract_extreme_values(
    results,
    column='Tension_Line1',
    n_extremes=10,
    extreme_type='max'
)

print("Top 10 Maximum Tensions:")
print(max_tensions[['Tension_Line1']])
```
