---
name: statistical-analysis-statistical-methods
description: 'Sub-skill of statistical-analysis: Statistical Methods (+2).'
version: 1.0.0
category: data-analytics
type: reference
scripts_exempt: true
---

# Statistical Methods (+2)

## Statistical Methods


**Z-score method** (for normally distributed data):
```python
z_scores = (df['value'] - df['value'].mean()) / df['value'].std()
outliers = df[abs(z_scores) > 3]  # More than 3 standard deviations
```

**IQR method** (robust to non-normal distributions):
```python
Q1 = df['value'].quantile(0.25)
Q3 = df['value'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
outliers = df[(df['value'] < lower_bound) | (df['value'] > upper_bound)]
```

**Percentile method** (simplest):
```python
outliers = df[(df['value'] < df['value'].quantile(0.01)) |
              (df['value'] > df['value'].quantile(0.99))]
```


## Handling Outliers


Do NOT automatically remove outliers. Instead:

1. **Investigate**: Is this a data error, a genuine extreme value, or a different population?
2. **Data errors**: Fix or remove (e.g., negative ages, timestamps in year 1970)
3. **Genuine extremes**: Keep them but consider using robust statistics (median instead of mean)
4. **Different population**: Segment them out for separate analysis (e.g., enterprise vs. SMB customers)

**Report what you did**: "We excluded 47 records (0.3%) with transaction amounts >$50K, which represent bulk enterprise orders analyzed separately."


## Time Series Anomaly Detection


For detecting unusual values in a time series:

1. Compute expected value (moving average or same-period-last-year)
2. Compute deviation from expected
3. Flag deviations beyond a threshold (typically 2-3 standard deviations of the residuals)
4. Distinguish between point anomalies (single unusual value) and change points (sustained shift)
