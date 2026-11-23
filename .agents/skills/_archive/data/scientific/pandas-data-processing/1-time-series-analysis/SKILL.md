---
name: pandas-data-processing-1-time-series-analysis
description: 'Sub-skill of pandas-data-processing: 1. Time Series Analysis.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Time Series Analysis

## 1. Time Series Analysis


**Load and Process Time Series:**
```python
import pandas as pd
import numpy as np
from pathlib import Path

def load_orcaflex_time_series(
    csv_file: Path,
    time_column: str = 'Time',
    parse_dates: bool = True
) -> pd.DataFrame:
    """
    Load OrcaFlex time series results from CSV.

    Args:
        csv_file: Path to CSV file
        time_column: Name of time column
        parse_dates: Whether to parse time column as datetime

    Returns:
        DataFrame with time as index
    """
    # Load CSV
    df = pd.read_csv(csv_file)

    # Set time as index
    if parse_dates:
        df[time_column] = pd.to_datetime(df[time_column], unit='s')

    df.set_index(time_column, inplace=True)

    return df

# Usage
results = load_orcaflex_time_series(
    Path('data/processed/vessel_motions.csv')
)

print(f"Time range: {results.index[0]} to {results.index[-1]}")
print(f"Duration: {(results.index[-1] - results.index[0]).total_seconds()} seconds")
print(f"Sampling rate: {1 / results.index.to_series().diff().mean().total_seconds():.2f} Hz")
```

**Resampling and Aggregation:**
```python
def resample_time_series(
    df: pd.DataFrame,
    target_frequency: str = '1S',
    method: str = 'mean'
) -> pd.DataFrame:
    """
    Resample time series to target frequency.

    Args:
        df: Input DataFrame with datetime index
        target_frequency: Target frequency ('1S', '0.1S', '1min', etc.)
        method: Aggregation method ('mean', 'max', 'min', 'std')

    Returns:
        Resampled DataFrame
    """
    # Resample
    if method == 'mean':
        resampled = df.resample(target_frequency).mean()
    elif method == 'max':
        resampled = df.resample(target_frequency).max()
    elif method == 'min':
        resampled = df.resample(target_frequency).min()
    elif method == 'std':
        resampled = df.resample(target_frequency).std()
    else:
        raise ValueError(f"Unknown method: {method}")

    # Fill NaN values (forward fill)
    resampled.fillna(method='ffill', inplace=True)

    return resampled

# Example: Downsample from 0.05s to 1s
high_freq_data = load_orcaflex_time_series(
    Path('data/processed/mooring_tension_0.05s.csv')
)

low_freq_data = resample_time_series(
    high_freq_data,
    target_frequency='1S',
    method='mean'
)

print(f"Original points: {len(high_freq_data)}")
print(f"Resampled points: {len(low_freq_data)}")
```

**Rolling Statistics:**
```python
def calculate_rolling_statistics(
    df: pd.DataFrame,
    column: str,
    window: str = '60S'
) -> pd.DataFrame:
    """
    Calculate rolling statistics for time series.

    Args:
        df: Input DataFrame with datetime index
        column: Column name to analyze
        window: Rolling window size (time-based)

    Returns:
        DataFrame with rolling statistics
    """
    stats = pd.DataFrame(index=df.index)

    # Rolling calculations
    rolling = df[column].rolling(window=window)

    stats[f'{column}_mean'] = rolling.mean()
    stats[f'{column}_std'] = rolling.std()
    stats[f'{column}_max'] = rolling.max()
    stats[f'{column}_min'] = rolling.min()

    return stats

# Example: 60-second rolling statistics
tension_stats = calculate_rolling_statistics(
    results,
    column='Tension_Line1',
    window='60S'
)

# Plot rolling mean and standard deviation
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=results.index,
    y=results['Tension_Line1'],
    name='Raw Tension',
    opacity=0.3
))
fig.add_trace(go.Scatter(
    x=tension_stats.index,
    y=tension_stats['Tension_Line1_mean'],
    name='60s Rolling Mean',
    line=dict(width=3)
))

fig.update_layout(
    title='Mooring Tension: Raw vs Rolling Mean',
    xaxis_title='Time',
    yaxis_title='Tension (kN)'
)
fig.write_html('reports/tension_rolling_mean.html')
```
