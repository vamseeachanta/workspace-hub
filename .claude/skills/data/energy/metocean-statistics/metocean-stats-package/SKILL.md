---
name: metocean-statistics-metocean-stats-package
description: 'Sub-skill of metocean-statistics: metocean-stats Package (+1).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# metocean-stats Package (+1)

## metocean-stats Package


**Installation:**
```bash
pip install metocean-stats
```

**Extreme Value Analysis:**
```python
from metocean_stats import EVA

# Block maxima approach

*See sub-skills for full details.*

## scipy.stats Integration


**GEV Distribution Fitting:**
```python
from scipy import stats
import numpy as np

# Extract annual maxima
annual_max = df.groupby(df['time'].dt.year)['Hs'].max().values

# Fit GEV distribution
shape, loc, scale = stats.genextreme.fit(annual_max)

*See sub-skills for full details.*
