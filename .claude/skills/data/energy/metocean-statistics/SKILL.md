---
name: metocean-statistics
description: Statistical analysis of metocean data including extreme value analysis, return periods, joint probability distributions, and directional statistics. Use for design criteria, fatigue analysis, and operational limits.
capabilities: []
requires: []
see_also: []
---

# Metocean Statistics Skill

## When to Use

Trigger this skill when the user asks about:

**Extreme Value Analysis**
- "Calculate extreme wave heights"
- "Return period analysis"
- "Fit GEV distribution"
- "100-year return period"
- "Peak-over-threshold analysis"
- "Annual maxima statistics"

**Distribution Fitting**
- "Joint probability distribution"
- "Hs-Tp joint distribution"
- "Environmental contours"
- "IFORM contours"
- "Fit distribution to wave data"

**Temporal Statistics**
- "Monthly statistics"
- "Seasonal trends"
- "Annual variability"
- "Exceedance duration"

**Directional Analysis**
- "Wave rose"
- "Wind rose"
- "Directional statistics"
- "Sector-based analysis"

**Design Applications**
- "Design criteria"
- "Fatigue analysis"
- "Operational limits"
- "Weather windows"

## Analysis Types

### Temporal Statistics

**Monthly Aggregations**
- Mean, max, min, standard deviation
- Percentiles (P50, P90, P99)
- Sample count and data availability

**Seasonal Aggregations**
- Winter (DJF), Spring (MAM), Summer (JJA), Autumn (SON)
- Seasonal extremes
- Inter-annual variability

**Annual Trends**
- Annual mean and max time series
- Trend analysis (linear regression)
- Climate variability indicators

**Exceedance Duration**
- Persistence above threshold
- Storm duration statistics
- Operational weather windows

### Extreme Value Analysis

**Block Maxima Method**
- Annual maxima extraction
- Monthly maxima for shorter records
- Requires minimum 10 years for reliability
- Standard approach for design criteria

**Peak-Over-Threshold (POT)**
- Extract independent peaks above threshold
- Suitable for shorter records (3+ years)
- More efficient use of data
- Requires declustering of dependent events

**GEV Distribution (Generalized Extreme Value)**
- Three-parameter distribution (shape, location, scale)
- Encompasses Gumbel, Frechet, Weibull types
- Standard for block maxima analysis
- Shape parameter indicates tail behavior

**GPD Distribution (Generalized Pareto)**
- Two-parameter distribution for exceedances
- Paired with POT method
- Threshold selection critical
- More flexible for tail modeling

### Return Periods

**Standard Return Periods**
| Period | Application |
|--------|-------------|
| 1-year | Annual operating design |
| 2-year | Seasonal planning |
| 5-year | Short-term structure design |
| 10-year | Installation operations |
| 25-year | Platform design basis |
| 50-year | Structure design life |
| 100-year | Ultimate limit state |
| 500-year | Abnormal/survival conditions |

**Confidence Intervals**
- Profile likelihood method
- Bootstrap resampling
- Delta method approximation
- Typically report 95% CI

### Joint Probability

**Hs-Tp Joint Distribution**
- Wave height and period correlation
- Scatter diagram representation
- Steepness limits (physical constraints)
- Critical for dynamic analysis

**Wind-Wave Correlation**
- Wind speed vs wave height
- Lag correlation analysis
- Sea state development
- Combined loading analysis

**Environmental Contours**
- IFORM method (Inverse First Order Reliability Method)
- Direct sampling approach
- Joint exceedance probability
- Design envelope definition

### Directional Analysis

**Wave Roses**
- Direction vs magnitude distribution
- Sector occurrence frequency
- Mean and maximum by sector
- Seasonal directional variation

**Wind Roses**
- Similar to wave roses
- Different directional convention (from vs to)
- Fetch-limited conditions
- Dominant wind patterns

**Sector-Based Statistics**
- 8, 12, or 16 sector divisions
- Exceedance by direction
- Design wave by sector
- Directional spreading

## External Tool Integration

### metocean-stats Package

**Installation:**
```bash
pip install metocean-stats
```

**Extreme Value Analysis:**
```python
from metocean_stats import EVA

# Block maxima approach
eva = EVA(data=wave_heights, method='block_maxima', block_size='year')
eva.fit('GEV')

# Get return levels
rp_10yr = eva.return_level(10)
rp_100yr = eva.return_level(100)

# Confidence intervals
rp_100yr_ci = eva.return_level_ci(100, alpha=0.05)

# Diagnostic plots
eva.plot_return_levels()
eva.plot_qq()
eva.plot_probability()
```

**Peak-Over-Threshold:**
```python
from metocean_stats import EVA

# POT approach
eva_pot = EVA(
    data=wave_heights,
    method='peak_over_threshold',
    threshold=np.percentile(wave_heights, 95),
    decluster_time='48h'
)
eva_pot.fit('GPD')

# Return levels from POT
rp_values = eva_pot.return_level([1, 10, 50, 100])
```

**Return Period Tables:**
```python
from metocean_stats import return_periods

# Multi-parameter return period table
rp_table = return_periods.calculate(
    data=df,
    parameters=['Hs', 'Tp', 'U10'],
    return_periods=[1, 2, 5, 10, 25, 50, 100],
    method='GEV',
    confidence_level=0.95
)

# Export to CSV
rp_table.to_csv('return_periods.csv')
```

**Joint Probability Analysis:**
```python
from metocean_stats import joint_probability

# Kernel density estimation
jp = joint_probability.fit(
    df['Hs'],
    df['Tp'],
    method='kernel',
    bandwidth='scott'
)

# Contour plots
jp.plot_contours(levels=[0.1, 0.5, 0.9])

# Scatter diagram
jp.plot_scatter_diagram(hs_bins=20, tp_bins=20)
```

**Environmental Contours:**
```python
from metocean_stats.contours import IFORM, DirectSampling

# IFORM contours
iform = IFORM(df['Hs'], df['Tp'])
contour_100yr = iform.contour(return_period=100, n_points=100)
iform.plot()

# Direct sampling contours
ds = DirectSampling(df['Hs'], df['Tp'], n_samples=10000)
contour_ds = ds.contour(return_period=100)
ds.plot()
```

**Directional Statistics:**
```python
from metocean_stats import directional

# Sector statistics
dir_stats = directional.sector_stats(
    speeds=df['Hs'],
    directions=df['wave_dir'],
    sectors=16,
    statistics=['mean', 'max', 'p90', 'count']
)

# Wave rose plot
directional.plot_rose(
    speeds=df['Hs'],
    directions=df['wave_dir'],
    bins=[0, 1, 2, 3, 4, 5],
    title='Significant Wave Height Rose'
)

# Directional extremes
dir_extremes = directional.sector_extremes(
    speeds=df['Hs'],
    directions=df['wave_dir'],
    sectors=8,
    return_periods=[1, 10, 50, 100]
)
```

### scipy.stats Integration

**GEV Distribution Fitting:**
```python
from scipy import stats
import numpy as np

# Extract annual maxima
annual_max = df.groupby(df['time'].dt.year)['Hs'].max().values

# Fit GEV distribution
shape, loc, scale = stats.genextreme.fit(annual_max)

# Return level calculation
def return_level(T, shape, loc, scale):
    """Calculate return level for return period T years."""
    p = 1 - 1/T
    return stats.genextreme.ppf(p, shape, loc=loc, scale=scale)

# Calculate return levels
return_periods = [1, 2, 5, 10, 25, 50, 100, 500]
return_levels = {T: return_level(T, shape, loc, scale) for T in return_periods}

# Goodness of fit
ks_stat, p_value = stats.kstest(annual_max, 'genextreme', args=(shape, loc, scale))
```

**GPD Distribution for POT:**
```python
from scipy import stats
import numpy as np

# Define threshold (e.g., 95th percentile)
threshold = np.percentile(wave_heights, 95)

# Extract exceedances
exceedances = wave_heights[wave_heights > threshold] - threshold

# Fit GPD
shape_gpd, loc_gpd, scale_gpd = stats.genpareto.fit(exceedances, floc=0)

# POT return level
def pot_return_level(T, threshold, shape, scale, rate):
    """Return level from POT analysis."""
    m = T * rate  # expected number of exceedances
    return threshold + scale / shape * ((m) ** shape - 1)

# Calculate exceedance rate (events per year)
n_years = (df['time'].max() - df['time'].min()).days / 365.25
rate = len(exceedances) / n_years
```

**QQ Plot Diagnostics:**
```python
import matplotlib.pyplot as plt
from scipy import stats

# QQ plot for GEV fit
fig, ax = plt.subplots(figsize=(8, 6))
stats.probplot(annual_max, dist=stats.genextreme, sparams=(shape, loc, scale), plot=ax)
ax.set_title('GEV Q-Q Plot')
plt.savefig('qq_plot.png')
```

## NREL Floating Wind Methodology

### Site Conditions Assessment

The NREL floating wind methodology provides a standardized approach for
characterizing offshore site conditions for floating wind turbine design.

**Return Period Table Format:**
| Return Period | Hs (m) | Tp (s) | U10 (m/s) | Current (m/s) |
|--------------|--------|--------|-----------|---------------|
| 1-year | 5.2 | 10.5 | 18.3 | 0.45 |
| 10-year | 7.8 | 12.1 | 23.4 | 0.62 |
| 50-year | 9.4 | 13.2 | 27.1 | 0.78 |
| 100-year | 10.2 | 13.8 | 28.9 | 0.85 |
| 500-year | 12.1 | 15.1 | 32.4 | 1.02 |

**Design Load Cases:**
- DLC 1.6: Normal operation with extreme waves
- DLC 6.1: Parked, extreme conditions (50-year)
- DLC 6.2: Parked, extreme conditions (50-year) with fault

**Joint Distribution Requirements:**
- Hs-Tp scatter diagram (minimum 10 years)
- Environmental contours for DLC validation
- Conditional Tp given Hs for response analysis

### Environmental Contour Methods

**IFORM Method:**
- Transform to standard normal space
- Apply reliability index for target probability
- Inverse transform to physical space
- Conservative for design applications

**Direct Sampling:**
- Monte Carlo simulation in physical space
- Empirical exceedance probability
- Better captures complex dependencies
- Computationally intensive

## Python Workflow Examples

### Complete Analysis Pipeline

```python
import pandas as pd
import numpy as np
from scipy import stats
from datetime import date

async def run_extreme_analysis(station_id: str, start_year: int, end_year: int):
    """Complete extreme value analysis workflow."""

    # Import metocean module components
    from worldenergydata.metocean.clients.ndbc_client import NDBCClient
    from worldenergydata.metocean.processors.data_harmonizer import DataHarmonizer

    # Fetch historical data
    async with NDBCClient() as client:
        data = await client.fetch_historical(
            station_id=station_id,
            start_date=date(start_year, 1, 1),
            end_date=date(end_year, 12, 31)
        )

    # Harmonize data
    harmonizer = DataHarmonizer()
    records = []
    for obs in data.data:
        record = harmonizer.harmonize_ndbc(obs, data.latitude, data.longitude)
        records.append(record)

    df = pd.DataFrame(records)
    df['time'] = pd.to_datetime(df['observation_time'])

    # Extract annual maxima
    annual_max = df.groupby(df['time'].dt.year)['wave_height_m'].max()

    # Fit GEV distribution
    shape, loc, scale = stats.genextreme.fit(annual_max.values)

    # Calculate return levels with confidence intervals
    return_periods = [1, 2, 5, 10, 25, 50, 100, 500]
    results = []

    for T in return_periods:
        p = 1 - 1/T
        rl = stats.genextreme.ppf(p, shape, loc=loc, scale=scale)

        # Bootstrap confidence intervals
        n_bootstrap = 1000
        bootstrap_rl = []
        for _ in range(n_bootstrap):
            sample = np.random.choice(annual_max.values, size=len(annual_max), replace=True)
            s, l, sc = stats.genextreme.fit(sample)
            bootstrap_rl.append(stats.genextreme.ppf(p, s, loc=l, scale=sc))

        ci_lower = np.percentile(bootstrap_rl, 2.5)
        ci_upper = np.percentile(bootstrap_rl, 97.5)

        results.append({
            'return_period_years': T,
            'Hs_m': round(rl, 2),
            'Hs_lower_CI': round(ci_lower, 2),
            'Hs_upper_CI': round(ci_upper, 2)
        })

    return pd.DataFrame(results)
```

### Monthly Statistics Calculation

```python
def calculate_monthly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate comprehensive monthly statistics for metocean parameters."""

    # Ensure datetime index
    df = df.copy()
    df['month'] = pd.to_datetime(df['observation_time']).dt.month

    # Define aggregation functions
    agg_funcs = {
        'wave_height_m': ['mean', 'max', 'min', 'std', 'count',
                          lambda x: x.quantile(0.5),
                          lambda x: x.quantile(0.9),
                          lambda x: x.quantile(0.99)],
        'wave_period_s': ['mean', 'max', 'std'],
        'wind_speed_ms': ['mean', 'max', 'std']
    }

    # Calculate monthly statistics
    monthly = df.groupby('month').agg(agg_funcs)

    # Flatten column names
    monthly.columns = ['_'.join(col).strip() for col in monthly.columns.values]

    # Add month names
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly.index = [month_names[i-1] for i in monthly.index]

    return monthly
```

### Seasonal Statistics

```python
def calculate_seasonal_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate seasonal statistics for metocean parameters."""

    df = df.copy()
    df['time'] = pd.to_datetime(df['observation_time'])
    df['month'] = df['time'].dt.month

    # Define seasons
    season_map = {12: 'Winter', 1: 'Winter', 2: 'Winter',
                  3: 'Spring', 4: 'Spring', 5: 'Spring',
                  6: 'Summer', 7: 'Summer', 8: 'Summer',
                  9: 'Autumn', 10: 'Autumn', 11: 'Autumn'}

    df['season'] = df['month'].map(season_map)

    # Calculate seasonal statistics
    seasonal = df.groupby('season').agg({
        'wave_height_m': ['mean', 'max', 'std', 'count'],
        'wind_speed_ms': ['mean', 'max', 'std']
    })

    # Order seasons
    season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
    seasonal = seasonal.reindex(season_order)

    return seasonal
```

### Directional Analysis

```python
def calculate_directional_stats(
    df: pd.DataFrame,
    speed_col: str = 'wave_height_m',
    dir_col: str = 'wave_direction_deg',
    sectors: int = 16
) -> dict:
    """Calculate statistics by directional sector."""

    df = df.copy()
    sector_width = 360 / sectors

    # Assign sectors (centered on N, E, S, W for 8 sectors)
    df['sector'] = ((df[dir_col] + sector_width/2) / sector_width).astype(int) % sectors
    df['sector_center'] = df['sector'] * sector_width

    stats_by_sector = {}
    total_count = len(df.dropna(subset=[speed_col, dir_col]))

    for sector in range(sectors):
        sector_center = sector * sector_width
        sector_data = df[df['sector'] == sector][speed_col].dropna()

        if len(sector_data) > 0:
            stats_by_sector[sector_center] = {
                'direction_deg': sector_center,
                'direction_label': _get_direction_label(sector_center),
                'mean': round(sector_data.mean(), 2),
                'max': round(sector_data.max(), 2),
                'std': round(sector_data.std(), 2),
                'p90': round(sector_data.quantile(0.9), 2),
                'count': len(sector_data),
                'occurrence_pct': round(len(sector_data) / total_count * 100, 1)
            }
        else:
            stats_by_sector[sector_center] = {
                'direction_deg': sector_center,
                'direction_label': _get_direction_label(sector_center),
                'mean': None, 'max': None, 'std': None, 'p90': None,
                'count': 0, 'occurrence_pct': 0
            }

    return stats_by_sector


def _get_direction_label(degrees: float) -> str:
    """Convert degrees to compass direction label."""
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = int((degrees + 11.25) / 22.5) % 16
    return directions[index]
```

### Joint Probability Distribution

```python
def calculate_joint_distribution(
    df: pd.DataFrame,
    var1: str = 'wave_height_m',
    var2: str = 'wave_period_s',
    bins1: int = 20,
    bins2: int = 20
) -> pd.DataFrame:
    """Calculate Hs-Tp joint distribution (scatter diagram)."""

    # Remove NaN values
    data = df[[var1, var2]].dropna()

    # Define bin edges
    var1_edges = np.linspace(data[var1].min(), data[var1].max(), bins1 + 1)
    var2_edges = np.linspace(data[var2].min(), data[var2].max(), bins2 + 1)

    # Calculate 2D histogram
    hist, _, _ = np.histogram2d(
        data[var1], data[var2],
        bins=[var1_edges, var2_edges]
    )

    # Convert to probability
    prob = hist / hist.sum()

    # Create DataFrame
    var1_centers = (var1_edges[:-1] + var1_edges[1:]) / 2
    var2_centers = (var2_edges[:-1] + var2_edges[1:]) / 2

    scatter = pd.DataFrame(
        prob,
        index=np.round(var1_centers, 2),
        columns=np.round(var2_centers, 2)
    )

    return scatter
```

### Exceedance Duration Analysis

```python
def calculate_exceedance_duration(
    df: pd.DataFrame,
    parameter: str = 'wave_height_m',
    threshold: float = 2.5,
    time_col: str = 'observation_time'
) -> dict:
    """Calculate exceedance duration statistics."""

    df = df.copy()
    df['time'] = pd.to_datetime(df[time_col])
    df = df.sort_values('time')

    # Identify exceedance events
    df['exceeds'] = df[parameter] > threshold

    # Find contiguous exceedance periods
    df['event_id'] = (df['exceeds'] != df['exceeds'].shift()).cumsum()

    events = df[df['exceeds']].groupby('event_id').agg({
        'time': ['min', 'max', 'count']
    })
    events.columns = ['start', 'end', 'observations']
    events['duration_hours'] = (events['end'] - events['start']).dt.total_seconds() / 3600

    # Calculate statistics
    total_hours = (df['time'].max() - df['time'].min()).total_seconds() / 3600
    exceedance_hours = events['duration_hours'].sum()

    return {
        'threshold': threshold,
        'n_events': len(events),
        'total_exceedance_hours': round(exceedance_hours, 1),
        'exceedance_percentage': round(exceedance_hours / total_hours * 100, 2),
        'mean_duration_hours': round(events['duration_hours'].mean(), 1),
        'max_duration_hours': round(events['duration_hours'].max(), 1),
        'min_duration_hours': round(events['duration_hours'].min(), 1)
    }
```

## YAML Configuration Templates

### Extreme Value Analysis Configuration

```yaml
analysis:
  name: extreme_value_analysis
  type: extreme_value

  # Method selection
  method: block_maxima  # Options: block_maxima, peak_over_threshold
  block_size: year      # For block_maxima: year, month, season

  # Distribution fitting
  distribution: GEV     # Options: GEV, Gumbel, GPD
  fitting_method: MLE   # Options: MLE, PWM, LMOM

  # POT-specific settings (if method: peak_over_threshold)
  pot_settings:
    threshold_percentile: 95
    decluster_time_hours: 48
    min_separation: 3

  # Return periods
  return_periods: [1, 2, 5, 10, 25, 50, 100, 500]

  # Confidence intervals
  confidence:
    level: 0.95
    method: bootstrap   # Options: bootstrap, profile_likelihood, delta
    n_bootstrap: 1000

  # Output options
  output:
    format: csv
    include_diagnostics: true
    plot_return_levels: true
    plot_qq: true
```

### Joint Probability Configuration

```yaml
joint_analysis:
  name: hs_tp_joint_distribution

  # Variables
  variables:
    x: wave_height_m
    y: wave_period_s

  # Distribution fitting
  method: kernel        # Options: kernel, parametric, copula
  bandwidth: scott      # Options: scott, silverman, custom

  # Scatter diagram
  scatter_diagram:
    x_bins: 20
    y_bins: 20
    normalize: probability

  # Environmental contours
  contours:
    method: IFORM       # Options: IFORM, direct_sampling, highest_density
    return_periods: [10, 50, 100]
    n_points: 100

  # Physical constraints
  constraints:
    max_steepness: 0.1  # Hs/Lp limit
    min_tp_factor: 3.0  # Tp >= factor * sqrt(Hs)
```

### Directional Analysis Configuration

```yaml
directional_analysis:
  name: wave_directional_stats

  # Sector definition
  sectors: 16           # Options: 8, 12, 16
  convention: from      # Options: from, to (direction waves come from)

  # Parameters to analyze
  parameters:
    - name: wave_height_m
      statistics: [mean, max, p90, occurrence]
    - name: wave_period_s
      statistics: [mean, max]

  # Rose plot settings
  rose_plot:
    bins: [0, 1, 2, 3, 4, 5, 6]
    colors: viridis
    legend_title: "Hs (m)"

  # Directional extremes
  extremes:
    method: sector_maxima
    return_periods: [1, 10, 50, 100]
```

### Monthly Statistics Configuration

```yaml
temporal_analysis:
  name: monthly_statistics

  # Aggregation period
  period: monthly       # Options: monthly, seasonal, annual

  # Statistics to calculate
  statistics:
    - mean
    - max
    - min
    - std
    - p50
    - p90
    - p99
    - count

  # Parameters
  parameters:
    - wave_height_m
    - wave_period_s
    - wind_speed_ms
    - wind_direction_deg

  # Output format
  output:
    format: csv
    include_plots: true
    plot_type: heatmap
```

## Output Formats

### Return Period Table (CSV)

```csv
return_period_years,Hs_m,Hs_lower_CI,Hs_upper_CI,Tp_s,Tp_lower_CI,Tp_upper_CI,U10_ms,U10_lower_CI,U10_upper_CI
1,5.2,4.8,5.6,10.5,9.8,11.2,18.3,16.9,19.7
2,6.1,5.6,6.6,11.2,10.4,12.0,20.5,18.9,22.1
5,7.1,6.5,7.7,11.8,10.9,12.7,22.1,20.3,23.9
10,7.8,7.1,8.5,12.1,11.2,13.0,23.4,21.4,25.4
25,8.7,7.9,9.5,12.6,11.6,13.6,25.2,23.0,27.4
50,9.4,8.4,10.4,13.2,12.1,14.3,27.1,24.7,29.5
100,10.2,9.0,11.4,13.8,12.6,15.0,28.9,26.2,31.6
500,12.1,10.5,13.7,15.1,13.7,16.5,32.4,29.2,35.6
```

### Summary Statistics (JSON)

```json
{
  "parameter": "wave_height_m",
  "unit": "m",
  "period": {
    "start": "2014-01-01",
    "end": "2024-12-31",
    "years": 11
  },
  "statistics": {
    "mean": 1.45,
    "std": 0.82,
    "min": 0.1,
    "max": 8.7,
    "p50": 1.3,
    "p90": 2.6,
    "p99": 4.1,
    "count": 96432,
    "missing_pct": 2.3
  },
  "monthly": {
    "Jan": {"mean": 2.1, "max": 7.2, "std": 1.1},
    "Feb": {"mean": 2.0, "max": 6.8, "std": 1.0},
    "...": "..."
  },
  "annual_maxima": {
    "2014": 6.2,
    "2015": 7.1,
    "...": "..."
  },
  "gev_parameters": {
    "shape": -0.12,
    "location": 5.8,
    "scale": 1.2
  }
}
```

### Directional Statistics (JSON)

```json
{
  "parameter": "wave_height_m",
  "sectors": 8,
  "convention": "direction_from",
  "data": [
    {"direction": 0, "label": "N", "mean": 1.2, "max": 5.4, "p90": 2.1, "occurrence_pct": 8.2},
    {"direction": 45, "label": "NE", "mean": 1.4, "max": 6.1, "p90": 2.4, "occurrence_pct": 12.5},
    {"direction": 90, "label": "E", "mean": 1.1, "max": 4.8, "p90": 1.9, "occurrence_pct": 9.8},
    {"direction": 135, "label": "SE", "mean": 0.9, "max": 4.2, "p90": 1.6, "occurrence_pct": 7.1},
    {"direction": 180, "label": "S", "mean": 1.3, "max": 5.8, "p90": 2.2, "occurrence_pct": 15.3},
    {"direction": 225, "label": "SW", "mean": 1.8, "max": 8.7, "p90": 3.1, "occurrence_pct": 22.4},
    {"direction": 270, "label": "W", "mean": 1.6, "max": 7.2, "p90": 2.8, "occurrence_pct": 16.2},
    {"direction": 315, "label": "NW", "mean": 1.3, "max": 5.9, "p90": 2.3, "occurrence_pct": 8.5}
  ]
}
```

## Best Practices

### Data Requirements

**Minimum Record Lengths:**
- Block maxima (annual): Minimum 10 years recommended
- Peak-over-threshold: Minimum 3 years with high-frequency data
- Monthly statistics: Minimum 3 years for seasonal patterns
- Directional analysis: Minimum 1 year continuous data

**Data Quality:**
- Check for gaps and document missing periods
- Validate against neighboring stations
- Remove spurious values (instrument errors)
- Ensure consistent time zone and conventions

### Distribution Fitting

**GEV Fitting:**
- Use maximum likelihood estimation (MLE)
- Check shape parameter range (-0.5 to 0.5 typical for ocean waves)
- Validate with QQ plots and probability plots
- Consider regional frequency analysis for short records

**Threshold Selection for POT:**
- Use mean residual life plot
- Test sensitivity to threshold choice
- Ensure independence of peaks (declustering)
- Typical threshold: 90th-95th percentile

### Uncertainty Quantification

**Always Report:**
- Confidence intervals for return levels
- Sample size and data availability
- Distribution fit quality metrics
- Assumptions and limitations

**Validation Methods:**
- Split-sample testing
- Cross-validation with nearby stations
- Comparison with historical extremes
- Sensitivity analysis

### Design Applications

**Conservative Approach:**
- Use upper confidence interval for design
- Consider climate change trends
- Account for measurement uncertainty
- Apply appropriate safety factors

## Common Workflows

### 1. Design Criteria Development

```
Step 1: Data Collection
  - Fetch 10+ years of hourly data
  - Check data quality and gaps
  - Document data source and period

Step 2: Annual Maxima Extraction
  - Extract annual maximum for each year
  - Check for outliers
  - Ensure independence

Step 3: Distribution Fitting
  - Fit GEV distribution
  - Validate fit with diagnostics
  - Check shape parameter

Step 4: Return Period Calculation
  - Calculate return levels (1-500 year)
  - Compute confidence intervals
  - Create return period table

Step 5: Export Results
  - CSV table for engineering use
  - JSON for database storage
  - Plots for reports
```

### 2. Fatigue Analysis Support

```
Step 1: Load Time Series
  - Hourly Hs-Tp pairs
  - Minimum 3 years data

Step 2: Joint Distribution
  - Calculate scatter diagram
  - Fit joint distribution
  - Define Hs-Tp bins

Step 3: Occurrence Matrix
  - Calculate occurrence hours per bin
  - Normalize to annual basis
  - Export for fatigue tools

Step 4: Validate
  - Check physical constraints
  - Compare with design basis
  - Document assumptions
```

### 3. Operational Weather Windows

```
Step 1: Define Operational Limits
  - Maximum Hs for operation
  - Maximum wind speed
  - Minimum visibility

Step 2: Monthly Exceedance
  - Calculate monthly exceedance %
  - Identify seasonal patterns
  - Calculate weather window statistics

Step 3: Persistence Analysis
  - Duration above threshold
  - Duration below threshold
  - Waiting time statistics

Step 4: Planning Output
  - Monthly operability table
  - Seasonal summary
  - Risk assessment input
```
